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
        Comment.objects.create(
            root= req.POST['root'],
            text= req.POST['text'],
            sender= req.user,
        )
    else:
        Comment.objects.create(
            root= req.POST['root'],
            text= req.POST['text'],
            parent= get_object_or_404(Comment, id=req.POST['parent']),
            sender= req.user,
        )
    return redirect(req.POST['root'])
