from django.shortcuts import render, redirect, get_object_or_404
from .models import Comment

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
                'parent': get_object_or_404(Comment, id= req.GET['parent'])
            })
    if req.POST.get('parent', '###') == '###':
        pri = req.POST.get('private', 'off')
        Comment.objects.create(
            root= req.POST['root'],
            text= req.POST['text'],
            private= pri == "on",
            sender= req.user,
        )
    else:
        parent = get_object_or_404(Comment, id=req.POST['parent'])
        Comment.objects.create(
            root= req.POST['root'],
            text= req.POST['text'],
            parent= parent,
            private= parent.private,
            sender= req.user,
        )
    return redirect(req.POST['root'])
