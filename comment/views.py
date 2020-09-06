import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from quiz.models import Secret
from .models import Comment


def sendCommentToTelegram(comment):
    chat_id = Secret.objects.get(key="telegram_comments_chat_id").value
    token = Secret.objects.get(key="botToken").value
    url = "https://api.telegram.org/bot" + token + "/sendMessages"
    params = {
        "chat_id": chat_id,
        "parse_mode": "MarkdownV2",
        'text': comment.get_message()
    }
    requests.post(url, data=params)


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
