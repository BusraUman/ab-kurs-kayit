# -*- coding:utf-8  -*-
import logging
import hashlib
import random
from django.shortcuts import render, render_to_response, redirect
from django.http.response import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.contrib.auth import authenticate,login
from django.contrib.auth import logout as logout_user
from django.template import RequestContext
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

from userprofile.forms import *
from userprofile.models import *

from abkayit.models import *
from abkayit.backend import prepare_template_data, create_verification_link
from abkayit.adaptor import send_email
from abkayit.settings import USER_TYPES,GENDER

log=logging.getLogger(__name__)

@csrf_exempt
def loginview(request):
	# TODO: kullanici ve parola hatali ise ve login olamazsa bir login sayfasina yonlendirilip capcha konulmasi csrf li form ile username password alinmasi gerekiyor
	state=""
	alerttype=""
	if not request.user.is_authenticated():
		username=""
		password=""
		alerttype="alert-info"
		state="Hesabiniz varsa buradan giris yapabilirsiniz!"
		if request.POST:
			username=request.POST['username']
			password=request.POST['password']
			user=authenticate(username=username,password=password)
			if user is not None:
				login(request,user)
				log.info("%s user successfuly logged in" % (request.user),extra={'clientip': request.META['REMOTE_ADDR'], 'user': request.user})
	return HttpResponseRedirect('/')

def subscribe(request):
    d = {'clientip': request.META['REMOTE_ADDR'], 'user': request.user}
    data = prepare_template_data(request)    
    if not request.user.is_authenticated():
        data['buttonname1']="register"
        data['buttonname2']="cancel"
        note = _("Register to system to give training,  participation in courses before the conferences, and  participation in conferences.")
        form = CreateUserForm()
        if 'register' in request.POST:
            form = CreateUserForm(request.POST)
            if form.is_valid():
                try:
                    user = form.save(commit=True)
                    user.set_password(user.password)
                    user.save()
                    note = _("""Your account created. You can give course proposal, you can register in courses before the conferences, 
                                and you can register to the conferences""")
                    form = None
                except Exception as e:
                    note="Hesap olusturulamadi. Lutfen daha sonra tekrar deneyin!"
                    log.error(e.message, extra=d)
        elif 'cancel' in request.POST:
            return redirect("index")
        data['createuserform']=form
        data['note']=note
        return render_to_response("userprofile/subscription.html",data,context_instance=RequestContext(request))
    else:
        return redirect("controlpanel")

def createprofile(request):
    d = {'clientip': request.META['REMOTE_ADDR'], 'user': request.user}
    data = prepare_template_data(request)
    data['buttonname1']='next'
    data['buttonname2']='cancel'
    uform=UpdateUserForm(instance=User.objects.get(email=request.user))
    form=StuProfileForm()
    note=_("Isleme devam edebilmek icin lutfen profilinizi tamamlayın")
    gender=''
    data['uform']=uform
    if 'next' in request.POST:
        first_name = request.POST.get('first_name','')
        last_name = request.POST.get('last_name','')
        form=StuProfileForm(request.user,request.POST,ruser=request.user)
        if form.is_valid():
            gender=form.cleaned_data['gender']
            try:
                if first_name or last_name:
                    u=User.objects.get(email=request.user)
                    u.first_name=first_name
                    u.last_name=last_name
                    u.save()
                profile=form.save(commit=False)
                profile.is_student=True
                profile.user=User.objects.get(email=request.user)
                profile.save()
                note=_("Profil kaydedildi. Lütfen konaklama seciminizi yapin")
            except:
                note=_("Kullanıcı profili oluşturulurken hata olustu. Lütfen sistem yöneticiniz ile iletişime geciniz")
            achoices=Accommodation.objects.filter(usertype__in=['stu','hepsi']).filter(gender__in=[gender,'H']).values_list('id','name').order_by('name')
            form = AccomodationPrefForm(achoices)
            data['buttonname1']='register'
            data['uform']=None
    elif 'register' in request.POST:
        gender=UserProfile.objects.get(user=User.objects.get(email=request.user)).gender
        achoices=Accommodation.objects.filter(usertype__in=['stu','hepsi']).filter(gender__in=[gender,'H']).values_list('id','name').order_by('name')
        form = AccomodationPrefForm(achoices,request.POST)
        if form.is_valid():
            if form.cleaned_data['accomodation']:
                try:
                    counter=0
                    for a in form.cleaned_data['accomodation']:
                        counter+=1
                        uaccpref=UserAccomodationPref(user=UserProfile.objects.get(user=request.user.pk),accomodation=Accommodation.objects.get(pk=a),usertype="stu",preference_order=counter)
                        uaccpref.save()
                    return redirect("applytocourse")
                except:
                    note=_("Profil oluşturuldu ancak konaklama tercihi olusturulurken hata olustu.")
            else:
                note=_("Lütfen aşağıdaki alanları doldurun!")
        else:
            note=_("Lutfen asagidaki alanları doldurun")
    elif 'cancel' in request.POST:
        return redirect("index")
    data['createuserform']=form
    data['note']=note
    return render_to_response("userprofile/subscription.html",data,context_instance=RequestContext(request))

def activate(request, key):
    user_verification = UserVerification.objects.get(activation_key=key)
    if user_verification:
        user = User.objects.get(username=user_verification.user_email)
        user.is_active=True
        user.save()
        return HttpResponse("kullanici aktif edildi")

@login_required(login_url='/')
def password_reset(request):
	d = {'clientip': request.META['REMOTE_ADDR'], 'user': request.user}
	data = prepare_template_data(request)
	form = ChangePasswordForm()
	note = _("Change your password")
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			try:
				request.user.set_password(form.cleaned_data['password'])
				request.user.save()
				note = _("""Your password has been changed""")
				form = None
			except Exception as e:
				note = _("""Your password couldn't be changed""")
				log.error(e.message, extra=d)
	data['changepasswordform'] = form
	data['note'] = note
	return render_to_response("userprofile/change_password.html", data, context_instance=RequestContext(request))

def password_reset_key(request):
	d = {'clientip': request.META['REMOTE_ADDR'], 'user': request.user}
	data = prepare_template_data(request)
	note = _("Please enter your registered email")
	if request.method == 'POST':
		try:
			user = User.objects.get(username=request.POST['email'])
			user_verification, created = UserVerification.objects.get_or_create(user_email=user.username)
			user_verification.password_reset_key = create_verification_link(user)
			user_verification.save()
			context = {}
			context['user'] = user
			context['activation_key'] = user_verification.password_reset_key
			domain = Site.objects.get(is_active=True).home_url
			if domain.endswith('/'):
				domain = domain.rstrip('/')
			context['domain'] = domain
	
			send_email("userprofile/messages/send_reset_password_key_subject.html",
							"userprofile/messages/send_reset_password_key.html",
							"userprofile/messages/send_reset_password_key.text",
							context,
							settings.EMAIL_FROM_ADDRESS,
							[user.username])
	
			note = _("""Password reset key has been sent""")
		except Exception as e:
			note = _("""Password reset operation failed""")
			log.error(e.message, extra=d)
	data['note'] = note
	return render_to_response("userprofile/change_password_key_request.html", data, context_instance=RequestContext(request))


def password_reset_key_done(request, key=None):
	d = {'clientip': request.META['REMOTE_ADDR'], 'user': request.user}
	data = prepare_template_data(request)
	note = _("Change your password")
	form = ChangePasswordForm()
	note = _("Change your password")
	try:
		user_verification = UserVerification.objects.get(password_reset_key=key)
		user = User.objects.get(username=user_verification.user_email)
		user.is_authenticated = False
		user.save()
		request.user = user
	except Exception as e:
		note = _("""Password reset operation failed""")
		log.error(e.message, extra=d)
	if request.method == 'POST':
		form = ChangePasswordForm(request.POST)
		if form.is_valid():
			try:
				request.user.set_password(form.cleaned_data['password'])
				request.user.save()
				note = _("""Your password has been changed""")
				form = None
				redirect("index")
			except Exception as e:
				note = _("""Your password couldn't be changed""")
				log.error(e.message, extra=d)
	data['changepasswordform'] = form
	data['note'] = note
	data['user'] = request.user
	return render_to_response("userprofile/change_password.html", data, context_instance=RequestContext(request))




def logout(request):
	logout_user(request)
	return HttpResponseRedirect("/")


