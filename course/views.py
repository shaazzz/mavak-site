import hashlib
import json
import os
import re
import urllib.request
from urllib.parse import urlparse

from background_task import background
from django.http import HttpResponseNotFound, JsonResponse
from django.shortcuts import render, get_object_or_404
from markdown2 import markdown
from next_prev import prev_in_order, next_in_order

from comment.json import json_of_root
from main.markdown import markdown
from quiz.models import Secret
from quiz.oj.ReqHandler import ReqHandler
from .models import Course, Lesson


def courseView(req, name):
    c = get_object_or_404(Course, name=name)
    l = Lesson.objects.filter(course=c)
    return render(req, "course/course.html", {
        'title': c.title,
        'lessons': l,
    })


def cleanContents(req):
    if not req.user.is_staff:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    ls = Lesson.objects.all()
    for l in ls:
        x = l.text
        l.text = re.sub(r'<style>[\s\S]+video[\s\S]+style>\s*', r"", l.text)
        l.text = re.sub(
            r'<div.+<script type="text\/JavaScript" src="https:\/\/www\.aparat\.com\/embed\/(.{5})[\S]+'
            r'ipt>\s*<\/div>\s*(<br>)*',
            r"% aparat.\1 %", l.text)
        if x != l.text:
            print(l.text)
        l.save()
    return JsonResponse({"ok": "true"})


@background
def upload_Helper(name, data):
    c = get_object_or_404(Course, name=name)
    lessons = Lesson.objects.filter(course=c)
    name = data['name']
    title = data['title']
    start_time = data['start_time']
    finish_time = data['finish_time']
    videoLink = data['videoLink']
    ls = [lll for lll in Lesson.objects.filter(course=c, name=name)]
    if len(ls) > 0:
        raise Exception("این درس قبلا آپلود شده است!")

    if finish_time == "until_end":
        finish_time = ""
    else:
        finish_time = "-t " + finish_time
    up = urlparse(videoLink)
    os.system("mkdir tmp_upload")
    filename = "tmp_upload/" + os.path.basename(up.path)
    cut_filename = "tmp_upload/cut-" + os.path.basename(up.path)

    urllib.request.urlretrieve(videoLink, filename)

    if os.system('ffmpeg -y -i ' + filename +
                 ' -ss ' + start_time + ' ' + finish_time + ' -c copy ' + cut_filename) != 0:
        raise Exception("خطا در برش فیلم!")

    reqHandler = ReqHandler()
    secret = json.loads(Secret.objects.get(key="APARAT_LOGIN").value)

    text = reqHandler.aparatRequest("login", {
        "luser": secret["aparat_username"],
        "lpass": hashlib.sha1(
            hashlib.md5(secret["aparat_password"].encode('utf-8')).hexdigest().encode('utf-8')).hexdigest(),
    })
    response = json.loads(text)
    if response['login']['type'] == 'error':
        raise Exception(response['login']['value'])
    login_token = response['login']["ltoken"]

    text = reqHandler.aparatRequest("uploadform", {
        "luser": secret["aparat_username"],
        "ltoken": login_token
    })
    url = json.loads(text)["uploadform"]['formAction']
    frm_id = json.loads(text)["uploadform"]["frm-id"]
    response = json.loads(os.popen('curl -F "frm-id=' + str(
        frm_id) + '" -F "data[title]=' + title + '" -F "data[category]=3" '
                                                 '-F "video=@\"' + cut_filename + '\"" ' + url).read())

    os.system("rm -rf tmp_upload/")
    if response['uploadpost']['type'] == 'error':
        raise Exception(response['uploadpost']['text'])
    uid = response['uploadpost']['uid']
    l = Lesson.objects.create(course=c, name=name, title=title, text="% aparat." + uid + " %", order=len(lessons) + 1)
    return "Success"


def uploadVideo(req, name):
    if not req.user.is_staff:
        return HttpResponseNotFound('<h1>Page not found</h1>')
    c = get_object_or_404(Course, name=name)
    lessons = Lesson.objects.filter(course=c)
    if req.method == 'GET':
        return render(req, 'course/uploadVideo.html', {
            'course': c,
            'form_name': c.name + str(len(lessons) + 1),
            'form_title': c.title + " " + str(len(lessons) + 1),
            'start_time': '00:00:00',
            'finish_time': 'until_end',
            'form_all_tags': [
                'المپیاد کامپیوتر',
                'کامپیوتر',
                'المپیاد',
                'C++',
                'ترکیبیات',
            ]
        })
    upload_Helper(name, req.POST)
    name = req.POST['name']
    title = req.POST['title']
    videoLink = req.POST['videoLink']

    return render(req, 'course/uploadVideo.html', {
        'course': c,
        'form_name': name,
        'form_title': title,
        'start_time': '00:00:00',
        'finish_time': 'until_end',
        'videoLink': videoLink,
        'form_all_tags': [
            'المپیاد کامپیوتر',
            'کامپیوتر',
            'المپیاد',
            'C++',
            'ترکیبیات',
        ],
        "success": True,
        "success_desc": "<a href=\"../" + name + "\">" + title + "</a>\n"
                                                                 "با موفقیت در صف آپلود قرار گرفت،"
                                                                 " تا مدتی دیگر این صفحه در"
                                                                 " دسترس قرار میگیرد اگر این اتفاق نیفتاد در صفحه"
                                                                 " ادمین قسمت task ها مشکل پیش آمده را بررسی کنید"
    })


def lessonView(req, name, lesson):
    c = get_object_or_404(Course, name=name)
    l = get_object_or_404(Lesson, course=c, name=lesson)
    lessons = Lesson.objects.filter(course=c)
    next = next_in_order(l, qs=lessons)
    prev = prev_in_order(l, qs=lessons)
    if next is not None:
        next = next.name
    if prev is not None:
        prev = prev.name
    return render(req, "course/lesson.html", {
        'title': l.title,
        'content': markdown(l.text),
        'next': next,
        'prev': prev,
        'comment': json_of_root('/courses/' + name + '/' + lesson, req.user),
    })


def allCoursesView(req):
    # if not req.user.is_staff:
    #    return HttpResponseNotFound('<h1>Page not found</h1>')
    cs = Course.objects.all()
    return render(req, "course/all_courses.html", {
        'courses': cs,
    })
