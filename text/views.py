from django.shortcuts import render, get_object_or_404
from .models import Text
from markdown2 import markdown

def renderText(req, name):
    t = get_object_or_404(Text, name= name)
    return render(req, "text/renderText.html", {
        'content': markdown(t.text),
    })
