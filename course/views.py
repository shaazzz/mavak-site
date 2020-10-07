from django.http import HttpResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404
from markdown2 import markdown
from next_prev import prev_in_order, next_in_order
from main.markdown import markdown

from comment.json import json_of_root
from .models import Course, Lesson


def courseView(req, name):
    c = get_object_or_404(Course, name=name)
    l = Lesson.objects.filter(course=c)
    return render(req, "course/course.html", {
        'title': c.title,
        'lessons': l,
    })


def lessonView(req, name, lesson):
    c = get_object_or_404(Course, name=name)
    l = get_object_or_404(Lesson, course=c, name=lesson)
    lessons = Lesson.objects.filter(course=c)
    next = next_in_order(l, qs=lessons)
    prev = prev_in_order(l, qs=lessons)
    return render(req, "course/lesson.html", {
        'title': l.title,
        'content': markdown(l.text),
        'next': next,
        'prev': prev,
        'comment': json_of_root('/courses/' + name + '/' + lesson, req.user),
    })


def allCoursesView(req):
    #if not req.user.is_staff:
    #    return HttpResponseNotFound('<h1>Page not found</h1>')
    cs = Course.objects.all()
    return render(req, "course/all_courses.html", {
        'courses': cs,
    })
