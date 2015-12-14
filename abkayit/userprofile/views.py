# -*- coding:utf-8  -*-
import logging

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

from userprofile.forms import CreateUserForm, InstProfileForm, StuProfileForm
from userprofile.models import SubscribeNotice

from abkayit.models import *
from abkayit.settings import USER_TYPES
from abkayit.backend import prepare_template_data

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
        note = _("Register to system to give training,  participation in courses before the conferences, and  participation in conferences.")
        form = CreateUserForm()
        if request.method == 'POST':
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
        data['createuserform']=form
        data['note']=note
        return render_to_response("userprofile/subscription.html",data,context_instance=RequestContext(request))
    else:
        return redirect("controlpanel")

def createprofile(request):
    d = {'clientip': request.META['REMOTE_ADDR'], 'user': request.user}
    data = prepare_template_data(request)
    form=StuProfileForm()
    note=_("Isleme devam edebilmek icin lutfen profilinizi tamamlayın")
    if request.POST:
        form=StuProfileForm(request.user,request.POST)
        if form.is_valid():
            try:
                profile=form.save(commit=False)
                profile.is_student=True
                profile.user=User.objects.get(email=request.user)
                profile.save()
                note=_("Profil kaydedildi.")
                return redirect("applytocourse")
            except:
                note=_("Profil oluşturulurken hata olustu.")
    data['createuserform']=form
    data['note']=note
    return render_to_response("userprofile/subscription.html",data,context_instance=RequestContext(request))

def logout(request):
    logout_user(request)
    return HttpResponseRedirect("/")
