from .models import Comment
from json import dumps
from django.db.models import Q

def json_of_comment(c):
    ch = Comment.objects.filter(parent=c)
    return {
        'text': c.text,
        'sender_name': c.sender.first_name+' '+c.sender.last_name,
        'id': str(c.id),
        'children': json_of_query(ch),
    }

def json_of_query(q):
    return [ json_of_comment(x) for x in q ]

def json_of_root(root, user):
    if (user.is_anonymous):
        q = Comment.objects.filter(private=False)
    elif (user.is_staff):
        q = Comment.objects
    else:
        q = Comment.objects.filter(Q(private=False)|Q(sender=user))    
    return {
        'root': root,
        'json': dumps(dumps(json_of_query(q.filter(root=root, parent= None)))),
    }
