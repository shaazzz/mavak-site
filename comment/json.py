from .models import Comment
from json import dumps

def json_of_comment(c):
    ch = Comment.objects.filter(parent=c)
    return {
        'text': c.text,
        'id': str(c.id),
        'children': json_of_query(ch),
    }

def json_of_query(q):
    return [ json_of_comment(x) for x in q ]

def json_of_root(root):
    return {
        'root': root,
        'json': dumps(dumps(json_of_query(Comment.objects.filter(root=root, parent= None)))),
    }
