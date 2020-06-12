from django.shortcuts import render, get_object_or_404
from text.models import Text
from markdown2 import markdown

def index(req):
    t = get_object_or_404(Text, name= 'home')
    return render(req, "main/index.html", {
        'content': markdown(t.text),
    })
