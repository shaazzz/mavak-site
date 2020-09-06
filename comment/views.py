import json
import os
import re

import requests
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from course.models import Course
from quiz.models import Secret
from users.models import OJHandle
from .models import Comment


def sendCommentToTelegram(comment):
    # '''
    proxy = 'http://127.0.0.1:38673/'
    os.environ['http_proxy'] = proxy
    os.environ['HTTP_PROXY'] = proxy
    os.environ['https_proxy'] = proxy
    os.environ['HTTPS_PROXY'] = proxy
    # '''

    chat_id = Secret.objects.get(key="telegram_comments_chat_id").value
    token = Secret.objects.get(key="botToken").value
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    params = {
        "chat_id": chat_id,
        'text': comment.get_message().encode(encoding='UTF-8', errors='strict')
    }
    x = requests.post(url, data=params)
    print(x.text)


def newView(req):
    if not req.user.is_authenticated:
        return redirect('/users/login')
    if req.method == 'GET':
        if req.GET.get('parent', '###') == '###':
            return render(req, 'comment/newComment.html', {
                'root': req.GET.get('root', ''),
                'user': req.user,
            })
        else:
            return render(req, 'comment/newResponse.html', {
                'root': req.GET.get('root', ''),
                'user': req.user,
                'parent': get_object_or_404(Comment, id=req.GET['parent'])
            })
    cmt = None
    if req.POST.get('parent', '###') == '###':
        pri = req.POST.get('private', 'off')
        cmt = Comment.objects.create(
            root=req.POST['root'],
            text=req.POST['text'],
            private=pri == "on",
            sender=req.user,
        )
    else:
        parent = get_object_or_404(Comment, id=req.POST['parent'])
        cmt = Comment.objects.create(
            root=req.POST['root'],
            text=req.POST['text'],
            parent=parent,
            private=parent.private,
            sender=req.user,
        )
    sendCommentToTelegram(cmt)
    return redirect(req.POST['root'])


@csrf_exempt
def telegramView(req, token):
    telegram_response_token = Secret.objects.get(key="telegram_response_token").value
    if telegram_response_token != token:
        return JsonResponse({"ok": False, "reason": "invalid token"})
    body = req.body.decode('utf8')
    inp = json.loads(body)
    text = inp["message"]["text"]
    if text.startswith("/show_unanswered_comments"):
        tags = text[len("/show_unanswered_comments") + 1:].split()
        comments = Comment.objects.raw(
            'select comment_comment.*, ("@"||replace(GROUP_CONCAT(DISTINCT users_ojhandle.handle), ",",'
            ' "\n@")) as handles from comment_comment inner join course_lesson  inner join course_course'
            ' on course_course.id=course_lesson.course_id and comment_comment.root='
            '("/courses/"||course_course.name||"/"||course_lesson.name) INNER join course_tag on '
            'course_tag.course_id=course_course.id INNER join users_supportertag on users_supportertag.tag_id'
            '=course_tag.tag_id INNER join users_ojhandle on users_supportertag.student_id='
            'users_ojhandle.student_id and users_ojhandle.judge="TELEGRAM" where comment_comment.answered='
            'false group by comment_comment.id')
        for c in comments:
            c.text += c.handles
            sendCommentToTelegram(c)
        return JsonResponse({"ok": True})

    if "message" not in inp or "reply_to_message" not in inp["message"] or "chat" \
            not in inp["message"]["reply_to_message"] or "text" not in \
            inp["message"]["reply_to_message"]:
        return JsonResponse({"ok": True, "result": "request ignored"})
    reply_text = inp["message"]["reply_to_message"]["text"]
    parent = \
        Comment.objects.raw('select comment_comment.*, ("@"||replace(GROUP_CONCAT(DISTINCT users_ojhandle.handle)'
                            ', ",", "\n@")) as handles from comment_comment inner join course_lesson  inner join course_course'
                            ' on course_course.id=course_lesson.course_id and comment_comment.root='
                            '("/courses/"||course_course.name||"/"||course_lesson.name) INNER join course_tag on '
                            'course_tag.course_id=course_course.id INNER join users_supportertag on users_supportertag.tag_id'
                            '=course_tag.tag_id INNER join users_ojhandle on users_supportertag.student_id='
                            'users_ojhandle.student_id and users_ojhandle.judge="TELEGRAM" where comment_comment.id='
                            + reply_text.split("\n")[0])[0]
    if text == "/ignore":
        parent.answered = True
        parent.save()
        return JsonResponse({"ok": True, "result": "comment ignored"})
    if text == "/delete":
        parent.delete()
        return JsonResponse({"ok": True, "result": "comment deleted"})

    username = inp['message']["from"]["username"].lower()
    try:
        user = OJHandle.objects.get(judge="TELEGRAM", handle=username).student.user
    except ObjectDoesNotExist:
        user = User.objects.get(username="mikaeel")

    cmt = Comment.objects.create(
        root=parent.root,
        text=text,
        parent=parent,
        private=parent.private,
        sender=user,
    )
    cmt.answered = True
    cmt.save()
    sendCommentToTelegram(cmt)
    return JsonResponse({"ok": True, "result": "comment added"})
