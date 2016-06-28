#!-*- coding-utf8 -*-
# coding=utf-8
from datetime import datetime
from django import template

from abkayit.models import ApprovalDate

register = template.Library()


@register.simple_tag(name="mod")
def mod(num):
    return -num


@register.simple_tag(name="isdategtnow_head")
def isdategtnow_head(datedict, key):
    now = datetime.now()
    adate = datedict.get(key)
    if adate:
        if adate.end_date >= now >= adate.start_date:
            return "Onayla"
    return "Gelecegini Teyit Etti"


@register.simple_tag(name="manuallyaddtrainess")
def manuallyaddtrainess(site):
    now = datetime.date(datetime.now())
    if now > site.application_end_date:
        return """
        <div class="alert alert-info">Sistemde profili tanimli olup başvuruyu kaçırmış kullanıcıları "Kursiyer Ekle"
         butonuna tıklayarak kursunuza ekleyebilirsiniz</div>
        <a href="#addprefpopup" class="btn btn-primary pull-right" type="button" data-toggle="modal"><i class="fa fa-fw fa-plus"></i>
        Kursiyer Ekle
      </a>"""


@register.simple_tag(name="isdategtnow_body")
def isdategtnow_body(datedict, key, t, course, user):
    now = datetime.now()
    adate = datedict.get(key)
    if adate:
        if adate.end_date >= now >= adate.start_date and user.userprofile.can_elect and not t.consentemailsent:
            approvedprefs = t.trainess.trainesscourserecord_set.all().filter(approved=True)
            is_selectable = True
            priviliged_pref = None
            for approvedpref in approvedprefs:
                if t.preference_order > approvedpref.preference_order:
                    is_selectable = False
                    priviliged_pref = approvedpref
            if is_selectable:
                dom = "<div class=\"checkbox\">"
                if t.approved:
                    dom += "<input type=\"checkbox\" checked name=\"students%s\" value=\"%s\"/>" % (course.id, t.pk)
                else:
                    dom += "<input type=\"checkbox\" name=\"students%s\" value=\"%s\"/>" % (course.id, t.pk)
                dom += "</div>"
                return dom
            else:
                return "%d. tercihi kabul edilmis." % priviliged_pref.preference_order
    if t.trainess_approved:
        return "Evet"
    else:
        return "Hayir"
