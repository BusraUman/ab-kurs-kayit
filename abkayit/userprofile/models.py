#!/usr/bin/env python
#-*- coding:utf-8 -*-

import datetime

from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _
from django_countries.fields import CountryField
from django_countries.data import COUNTRIES

from abkayit.settings import USER_TYPES, UNIVERSITIES, GENDER

from abkayit.models import Site


class UserVerification(models.Model):
    user_email = models.CharField(max_length=40) 
    activation_key = models.CharField(max_length=40, null=True)
    password_reset_key = models.CharField(max_length=40, null=True)
    activation_key_expires = models.DateTimeField(null=True)
    password_reset_key_expires = models.DateTimeField(null=True)

    def __unicode__(self):
        return self.user_email

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    birthdate = models.DateField(verbose_name=_("Bird Date"), default=datetime.date(1970,1,1))
    tckimlikno = models.CharField(verbose_name=_("Turkish ID No"), max_length=11, blank=True)
    ykimlikno = models.CharField(verbose_name=_("Foreigner ID No"), max_length=11, blank=True)
    gender = models.CharField(choices={'E':_("Male"), 'K':_("Female")}.items(), verbose_name=_("Gender"), max_length=1)
    mobilephonenumber = models.CharField(verbose_name=_("Mobile Phone Number"), max_length=14)
    address = models.TextField(verbose_name=_("Home Address"))
    job = models.CharField(verbose_name=_("Job"), max_length=40)
    city = models.CharField(verbose_name= _("City"), max_length=40)
    country = CountryField(verbose_name= _("Country"), choices=COUNTRIES,default='TR')
    title =  models.CharField(verbose_name= _("Title"), max_length=40)
    organization = models.CharField(verbose_name= _("Organization"), max_length=50)
    university = models.CharField(choices=UNIVERSITIES, verbose_name=_("University"), max_length=300,blank=True)
    department = models.CharField(verbose_name= _("Department"), max_length=50) 
    is_instructor = models.BooleanField(verbose_name=_("Is Instructor"), default=False)
    is_student = models.BooleanField(verbose_name=_("Is Student"), default=False)
    is_speaker = models.BooleanField(verbose_name=_("Is Speaker"), default=False)
    is_participant = models.BooleanField(verbose_name=_("Is Participant"), default=False)
    additional_information = models.TextField(verbose_name=_("Additional Information"), null=True)
    userpassedtest = models.BooleanField(verbose_name=_("Basvuru yapabilir mi?"), default=False)
    def __unicode__(self):
        return self.user.username

class SubscribeNotice(models.Model):
    usertype = models.CharField(choices=USER_TYPES.items(), verbose_name=_("User Type"), max_length=4)
    subnotice = models.TextField(verbose_name=_("Subscription Notice"))
    def __unicode__(self):
        return self.usertype
    
class Accommodation(models.Model):
    gender = models.CharField(choices=GENDER.items(), verbose_name=_("Gender"), max_length=1)
    usertype = models.CharField(choices=USER_TYPES.items(),verbose_name=_("User Type"),max_length=15)
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    address = models.CharField(verbose_name=_("Address"), max_length=300)
    website = models.CharField(verbose_name=_("Website"), max_length=300)
    site = models.ForeignKey(Site)
    def __unicode__(self):
        return self.name
    class Meta:
        verbose_name = _("Accommodation")
        verbose_name_plural = _("Accommodations")
            
class UserAccomodationPref(models.Model):
    user = models.ForeignKey(UserProfile)
    accomodation = models.ForeignKey(Accommodation)
    usertype = models.CharField(choices=USER_TYPES.items(), verbose_name=_("User Type"), max_length=30)
    preference_order = models.SmallIntegerField(default=1)
    approved = models.BooleanField(default=False)
    def __unicode__(self):
        return self.user.user.username
    class Meta:
        verbose_name = _("Participant Accommodation Preference")
        verbose_name_plural = _("Participant Accommodation Preferences")
