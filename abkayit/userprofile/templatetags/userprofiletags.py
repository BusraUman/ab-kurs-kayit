#!-*- coding-utf8 -*-
# coding=utf-8

from django import template

from abkayit.models import ApprovalDate, Site

from userprofile.models import TrainessClassicTestAnswers
from userprofile.userprofileops import UserProfileOPS

from training.models import Course, TrainessCourseRecord

register = template.Library()


@register.simple_tag(name="getanswer")
def getanswer(question, user):
    try:
        return TrainessClassicTestAnswers.objects.get(question=question, user=user.userprofile).answer
    except:
        return ""


@register.simple_tag(name="getanswers")
def getanswers(tuser, ruser, courseid):
    answers = []
    if ruser.is_staff:
        answers = TrainessClassicTestAnswers.objects.filter(user=tuser, question__site__is_active=True)
    elif courseid:
        course = Course.objects.get(pk=int(courseid))
        questions = course.textboxquestion.all()
        for q in questions:
            answers.append(TrainessClassicTestAnswers.objects.filter(question=q, user=tuser))
        answers.extend(TrainessClassicTestAnswers.objects.filter(user=tuser, question__site__is_active=True,
                                                                 question__is_sitewide=True))

    html = ""
    if answers:
        html = "<dt>Cevaplar:</dt><dd><section><ul>"
        for answer in answers:
            html += "<li> <b>" + answer.question.detail + "</b> <p>" + answer.answer + "</p> </li>"
        html += "</section></ul></dd>"

    return html


@register.simple_tag(name="oldeventprefs")
def oldeventprefs(tuser):
    html = ""
    try:
        sites = Site.objects.filter(is_active=False)

        for site in sites:
            trainessoldprefs = TrainessCourseRecord.objects.filter(trainess=tuser, course__site=site).order_by(
                'preference_order')
            if trainessoldprefs:
                html += "<section><p>" + site.name + " - " + site.year + "</p><ul>"
                for top in trainessoldprefs:
                    if top.approved:
                        html += "<li>" + str(top.preference_order) + ".tercih: " + top.course.name + " (Onaylanmış) </li>"
                    else:
                        html += "<li>" + str(top.preference_order) + ".tercih: " + top.course.name + " </li>"
                html += "</ul></section>"
        if html:
            html = "<h4>Eski Tercihleri: </h4>" + html
    except Exception as e:
        print e.message
    return html


@register.simple_tag(name="getoperationsmenu")
def getoperationsmenu(uprofile):
    html = ""

    if UserProfileOPS.is_instructor(uprofile):
        html += """<li>
        <a href="/egitim/controlpanel"><i class="fa fa-book fa-fw"></i> Kursum</a>
        </li>
        <li>
            <a href="/egitim/katilimciekle"><i class="fa fa-book fa-fw"></i> Kursiyer Ekle</a>
        </li>"""
    else:
        html += """
        <li>
            <a href="/egitim/applytocourse"><i class="fa fa-check-square-o fa-fw"></i> Kurs Başvurusu</a>
        </li>
        <li>
            <a href="/egitim/approve_course_preference"><i class="fa fa-thumbs-o-up fa-fw"></i> Başvuru Durum/Onayla</a>
        </li>
        """

    return html

@register.simple_tag(name="instinfo")
def instinfo(uprofile):
    html = ""
    if UserProfileOPS.is_instructor(uprofile):
        html += "<li><a href=\"/accounts/egitmen/bilgi\"><i class=\"fa-info-circle fa-fw\"></i> Egitmen Bilgileri </a></li>"

    return html
#