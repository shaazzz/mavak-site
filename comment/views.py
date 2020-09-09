import json
import os
import re
import time

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


def firstRun():
    print("start run")
    comments = Comment.objects.raw("select * from comment_comment where EXISTS "
                                   "(SELECT * FROM comment_comment AS c2 WHERE c2.parent_id=comment_comment.id)")
    for c in comments:
        c.answered = 1
        c.save()

    print("finish run")


def deleteMessageTelegram(msg_id):
    chat_id = Secret.objects.get(key="telegram_comments_chat_id").value
    token = Secret.objects.get(key="botToken").value
    url = "https://api.telegram.org/bot" + token + "/deleteMessage"
    params = {
        "chat_id": chat_id,
        'message_id': msg_id
    }
    x = requests.post(url, data=params)


def sendMessageToTelegram(s):
    chat_id = Secret.objects.get(key="telegram_comments_chat_id").value
    token = Secret.objects.get(key="botToken").value
    url = "https://api.telegram.org/bot" + token + "/sendMessage"
    params = {
        "chat_id": chat_id,
        'text': s
    }
    x = requests.post(url, data=params)


def sendCommentToTelegram(comment):
    sendMessageToTelegram(comment.get_message().encode(encoding='UTF-8', errors='strict'))


def newView(req):
    # firstRun()
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
    cmt = Comment.objects.raw('select comment_comment.*, ("@"||replace(GROUP_CONCAT(DISTINCT users_ojhandle.handle)'
                              ', ",", "\n@")) as handles from comment_comment inner join course_lesson  inner join course_course'
                              ' on course_course.id=course_lesson.course_id and comment_comment.root='
                              '("/courses/"||course_course.name||"/"||course_lesson.name) INNER join course_tag on '
                              'course_tag.course_id=course_course.id INNER join users_supportertag on users_supportertag.tag_id'
                              '=course_tag.tag_id INNER join users_ojhandle on users_supportertag.student_id='
                              'users_ojhandle.student_id and users_ojhandle.judge="TELEGRAM" where comment_comment.id='
                              + str(cmt.id))[0]
    cmt.text += "\n\n" + cmt.handles
    sendCommentToTelegram(cmt)
    return redirect(req.POST['root'])


@csrf_exempt
def telegramView(req, token):
    global inp
    try:
        telegram_response_token = Secret.objects.get(key="telegram_response_token").value
        if telegram_response_token != token:
            return JsonResponse({"ok": False, "reason": "invalid token"})
        body = req.body.decode('utf8')
        inp = json.loads(body)
        text = inp["message"]["text"]
        if text.startswith("/show_unanswered_comments"):
        sendMessageToTelegram("show request ignored, id:" + str(inp["update_id"]) + "\n" + str(e))
        return JsonResponse({"ok": True, "result": "request ignored"})
            return JsonResponse({"ok": True})
            comments = Comment.objects.raw(
                'select comment_comment.*, ("@"||replace(GROUP_CONCAT(DISTINCT users_ojhandle.handle), ",",'
                ' "\n@")) as handles from comment_comment inner join course_lesson  inner join course_course'
                ' on course_course.id=course_lesson.course_id and comment_comment.root='
                '("/courses/"||course_course.name||"/"||course_lesson.name) INNER join course_tag on '
                'course_tag.course_id=course_course.id INNER join users_supportertag on users_supportertag.tag_id'
                '=course_tag.tag_id INNER join users_ojhandle on users_supportertag.student_id='
                'users_ojhandle.student_id and users_ojhandle.judge="TELEGRAM" where comment_comment.answered='
                '0 group by comment_comment.id')
            for c in comments:
                c.text += "\n\n" + c.handles
                sendCommentToTelegram(c)
                time.sleep(2)
            return JsonResponse({"ok": True})
        if "message" not in inp or "reply_to_message" not in inp["message"] or "chat" \
                not in inp["message"]["reply_to_message"] or "text" not in \
                inp["message"]["reply_to_message"] or \
                inp["message"]["reply_to_message"]["from"]["username"] != "mavakbot":
            print("request ignored")
            return JsonResponse({"ok": True, "result": "request ignored"})
        reply_text = inp["message"]["reply_to_message"]["text"]
        src_id = inp["message"]["reply_to_message"]["message_id"]
        deleteMessageTelegram(src_id)
        src_id = inp["message"]["message_id"]
        deleteMessageTelegram(src_id)
        first_line = reply_text.split("\n")[0]
        if not first_line.isnumeric():
            sendMessageToTelegram("reply ignored")
            return JsonResponse({"ok": False, "result": "parent not found"})
        parent = \
            Comment.objects.raw('select comment_comment.*, ("@"||replace(GROUP_CONCAT(DISTINCT users_ojhandle.handle)'
                                ', ",", "\n@")) as handles from comment_comment inner join course_lesson  inner join course_course'
                                ' on course_course.id=course_lesson.course_id and comment_comment.root='
                                '("/courses/"||course_course.name||"/"||course_lesson.name) INNER join course_tag on '
                                'course_tag.course_id=course_course.id INNER join users_supportertag on users_supportertag.tag_id'
                                '=course_tag.tag_id INNER join users_ojhandle on users_supportertag.student_id='
                                'users_ojhandle.student_id and users_ojhandle.judge="TELEGRAM" where comment_comment.id='
                                + first_line)[0]
        if parent.root is None:
            sendMessageToTelegram("parent not found:" + first_line)
            return JsonResponse({"ok": False, "result": "parent not found"})
        if text == "/ignore":
            parent.answered = True
            parent.save()
            sendMessageToTelegram("comment ignored")
            return JsonResponse({"ok": True, "result": "comment ignored"})
        if text == "/delete":
            parent.delete()
            sendMessageToTelegram("comment deleted")
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
        cmt.text += "\n\n" + parent.handles
        sendMessageToTelegram("comment added")
        return JsonResponse({"ok": True, "result": "comment added"})
    except Exception as e:
        sendMessageToTelegram("request ignored, id:" + str(inp["update_id"]) + "\n" + str(e))
        return JsonResponse({"ok": True, "result": "request ignored"})
