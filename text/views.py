from django.shortcuts import render, get_object_or_404
from main.markdown import markdown

from .models import Text


def renderText(req, name):
    t = get_object_or_404(Text, name=name)
    return render(req, "text/renderText.html", {
        'content': markdown(t.text),
    })
