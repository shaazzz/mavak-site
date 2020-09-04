from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect

from course.models import Course, Lesson
from markdown2 import markdown
from comment.json import json_of_root
from next_prev import prev_in_order, next_in_order
from django.utils import timezone

from quiz.models import Quiz


def todayCourseView(req):
    return redirect('/content/date/' + str(timezone.now().year) + '-' + str(timezone.now().month) + '-' + str(
        timezone.now().day) + '/')


def courseView(req, date):
    if date.today() < date and not req.user.is_staff:
        return render(req, "content/not_started.html", {
            'start_date': date,
            'current': timezone.now(),
        })
    ls = Lesson.objects.filter(release__lt=date - timedelta(days=1), drop_off_date__gt=date)
    qs = Quiz.objects.filter(start__lte=date + timedelta(days=1), end__gte=date)
    next_date = date + timedelta(days=1)
    nxt = str(next_date.year) + '-' + str(next_date.month) + '-' + str(next_date.day)
    prev_date = date + timedelta(days=-1)
    prv = str(prev_date.year) + '-' + str(prev_date.month) + '-' + str(prev_date.day)
    return render(req, "content/course.html", {
        'tarikh': date,
        'lessons': ls,
        'next': nxt,
        'prev': prv,
        'quizzes': qs,
    })


def lessonView(req, date, lesson):
    if date.today() < date and not req.user.is_staff:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})
    l = get_object_or_404(Lesson, name=lesson, release__lt=date - timedelta(days=1), drop_off_date__gt=date)
    c = get_object_or_404(Course, id=l.course_id)
    lessons = Lesson.objects.filter(release__lt=date - timedelta(days=1), drop_off_date__gt=date)
    next = next_in_order(l, qs=lessons)
    prev = prev_in_order(l, qs=lessons)
    return render(req, "content/lesson.html", {
        'title': l.title,
        'content': markdown(l.text),
        'next': next,
        'prev': prev,
        'comment': json_of_root('/courses/' + c.name + '/' + lesson, req.user),
    })
