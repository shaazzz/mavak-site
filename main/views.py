from django.shortcuts import render, get_object_or_404, redirect
from text.models import Text
from markdown2 import markdown


def index(req):
    return redirect("/users/me")

'''
t = get_object_or_404(Text, name='home')
return render(req, "main/index.html", {
    'content': markdown(t.text),
})
'''
