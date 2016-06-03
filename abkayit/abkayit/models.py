#!/usr/bin/python
# -*- coding: utf-8 -*-

from datetime import datetime

from django.db import models
from django.utils.translation import ugettext_lazy as _
from ckeditor.fields import RichTextField


def make_choices(choices):
    """
    :param choices: Returns tuples of localized choices based on the dict choices parameter.
    Uses lazy translation for choices names.
    """
    return tuple([(k, _(v)) for k, v in choices.items()])


class Site(models.Model):
    name = models.CharField(verbose_name=_("Site Name"), max_length="255")
    year = models.CharField(verbose_name=_("Year"), max_length="4")
    logo = models.ImageField(verbose_name=_("Logo"), upload_to="static/imagstatic/images")
    is_active = models.BooleanField(verbose_name=_("Is Active"), default=False)
    home_url = models.CharField(verbose_name=_("Home Url"), max_length="128", null=True)
    application_start_date = models.DateField(verbose_name=_("Course Application Start Date"), default=datetime.now)
    application_end_date = models.DateField(verbose_name=_("Course Application End Date"), default=datetime.now)
    event_start_date = models.DateField(verbose_name=_("Event Start Date"), default=datetime.now)
    event_end_date = models.DateField(verbose_name=_("Event End Date"), default=datetime.now)

    def __unicode__(self):
        return self.name


class Menu(models.Model):
    name = models.CharField(verbose_name=_("Name"), max_length="255")
    order = models.IntegerField(verbose_name=_("Order"))
    site = models.ForeignKey(Site)

    def __unicode__(self):
        return self.name

    class Meta:
        unique_together = ('order', 'site',)


class Content(models.Model):
    name = models.CharField(verbose_name=_("Content Name"), max_length="255")
    content = RichTextField(verbose_name=_("HTML Content"))
    menu = models.OneToOneField(Menu, related_name="+", null=True)

    def __unicode__(self):
        return self.name


class Answer(models.Model):
    detail = models.CharField(verbose_name=_("Detail"), max_length="500")

    class Meta:
        verbose_name = _("Answer")
        verbose_name_plural = _("Answers")

    def __unicode__(self):
        return self.detail


class Question(models.Model):
    no = models.IntegerField()
    detail = models.CharField(verbose_name=_("Question"), max_length="5000")
    choices = models.ManyToManyField(Answer, related_name="choices")
    rightanswer = models.ForeignKey(Answer, related_name="rightanswer")
    active = models.BooleanField(verbose_name=_("Is Active"), default=False)

    class Meta:
        verbose_name = _("Question")
        verbose_name_plural = _("Questions")

    def __unicode__(self):
        return self.detail


class ApprovalDate(models.Model):
    start_date = models.DateTimeField(verbose_name=_("Start Date"), default=datetime.now)
    end_date = models.DateTimeField(verbose_name=_("End Date"), default=datetime.now)
    preference_order = models.SmallIntegerField(verbose_name=_("Preference"))
    site = models.ForeignKey(Site)
    for_instructor = models.BooleanField(verbose_name=_("For Instructor?"), default=True)
    for_trainess = models.BooleanField(verbose_name=_("For Trainess?"), default=False)

    class Meta:
        verbose_name = _("Approval Date")
