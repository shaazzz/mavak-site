from django.shortcuts import render, get_object_or_404
from .models import Course, Lesson
from markdown2 import markdown

def courseView(req, name):
    c = get_object_or_404(Course, name= name)
    l = Lesson.objects.filter(course = c)
    return render(req, "course/course.html", {
        'title': c.title,
        'lessons': l,
    })

def lessonView(req, name, lesson):
    c = get_object_or_404(Course, name= name)
    l = get_object_or_404(Lesson, course= c, name=lesson)
    return render(req, "course/lesson.html", {
        'title': l.title,
        'content': markdown(l.text),
    })

