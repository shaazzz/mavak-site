import json
import os
import re

import requests
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt

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
        "parse_mode": "MarkdownV2",
        'text': comment.get_message().encode(encoding='UTF-8', errors='strict')
    }
    x = requests.post(url, data=params)
    print(comment.get_message())
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
def addFromTelegramView(req, token):
    telegram_response_token = Secret.objects.get(key="telegram_response_token").value
    if telegram_response_token != token:
        return JsonResponse({"ok": False, "reason": "invalid token"})
    body = req.body.decode('utf8')
    inp = json.loads(body)
    if "message" not in inp or "reply_to_message" not in inp["message"] or "chat" \
            not in inp["message"]["reply_to_message"] or "text" not in \
            inp["message"]["reply_to_message"]:
        return JsonResponse({"ok": True, "result": "comment ignored"})
    reply_text = inp["message"]["reply_to_message"]["text"]
    text = inp["message"]["text"]
    parent = get_object_or_404(Comment, id=reply_text.split("\n")[0])
    root = re.findall(r"\[.+\]", reply_text.split("\n")[1])[0][1:-1].replace('\\-', '-')
    username = inp['message']["from"]["username"].lower()
    print(username)
    try:
        user = OJHandle.objects.get(judge="TELEGRAM", handle=username).student.user
    except ObjectDoesNotExist:
        user = User.objects.get(username="mikaeel")
    cmt = Comment.objects.create(
        root=root,
        text=text,
        parent=parent,
        private=parent.private,
        sender=user,
    )
    sendCommentToTelegram(cmt)
    return JsonResponse({"ok": True, "result": "comment added"})
