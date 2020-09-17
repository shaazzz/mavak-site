from datetime import timedelta

from django.http import JsonResponse, HttpResponseNotFound
from django.shortcuts import render, get_object_or_404, redirect

from course.models import Course, Lesson
from markdown2 import markdown
from comment.json import json_of_root
from next_prev import prev_in_order, next_in_order
from django.utils import timezone

from quiz.models import Quiz


def todayCourseView(req):
    return redirect('/content/date/' + str(timezone.now().year) + '-' + str(timezone.now().month) + '-' + str(
        timezone.now().day) + '/all/')


def getGroups(rows):
    groups = []
    now = []
    last_id = None
    for row in rows:
        if last_id is not None and last_id != row.date_id:
            groups.append(now)
            now = []
        now.append(row)
        last_id = row.date_id
    if last_id is not None:
        groups.append(now)
    return groups


def syllabusView(req):
    addit = "where release<'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
    if req.user.is_staff:
        addit = ""
    ls = Lesson.objects.raw("select *,'lesson' as type,(DATE(release, 'weekday 5', '-7 days')) "
                            "as date_id from course_lesson " + addit +
                            " order by release")
    qs = Quiz.objects.raw("select *,'quiz' as type,quiz_quiz.start as release,quiz_quiz.end as drop_off_date,"
                          "(DATE(quiz_quiz.start, 'weekday 5', '-7 days')) as date_id from quiz_quiz " + addit +
                          " order by release")

    ls = [row for row in ls] + [row for row in qs]
    ls.sort(key=lambda x: x.date_id)
    return render(req, "content/syllabus.html", {
        'lesson_groups': getGroups(ls),
        'tag': "all",
    })


def syllabusWithTagView(req, tag):
    condition = "where release<'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
    if req.user.is_staff:
        condition = ""
    ls = Lesson.objects.raw("select course_lesson.*,'lesson' as type,(DATE(release, 'weekday 5', '-7 days')) "
                            "as date_id from course_lesson inner join course_tag on course_tag.course_id"
                            "=course_lesson.course_id INNER join main_tag on course_tag.tag_id=main_tag.id and "
                            "main_tag.name='" + tag + "' " + condition + " order by release")
    qs = Quiz.objects.raw("select quiz_quiz.*,'quiz' as type,quiz_quiz.start as release,quiz_quiz.end "
                          "as drop_off_date, (DATE(quiz_quiz.start, 'weekday 5', '-7 days')) as date_id "
                          "from quiz_quiz inner join quiz_tag on quiz_tag.quiz_id=quiz_quiz.id INNER join "
                          "main_tag on quiz_tag.tag_id=main_tag.id and main_tag.name="
                          "'" + tag + "' " + condition + " order by release")

    ls = [row for row in ls] + [row for row in qs]
    for i in ls:
        i.release = i.release.replace(tzinfo=None)
    ls.sort(key=lambda x: x.release)
    return render(req, "content/syllabus.html", {
        'lesson_groups': getGroups(ls),
        'tag': tag,
    })


def courseView(req, date, tag="all"):
    if date.today() < date and not req.user.is_staff:
        return render(req, "content/not_started.html", {
            'start_date': date,
            'current': timezone.now(),
        })
    query_date = date + timedelta(days=1)
    if tag != "all":
        ls = Lesson.objects.raw("SELECT * from course_lesson  inner join course_tag on course_tag.course_id="
                                "course_lesson.course_id inner join main_tag on main_tag.id=course_tag.tag_id "
                                "where course_lesson.release<'" + str(query_date) +
                                "' and course_lesson.drop_off_date>'" + str(date) +
                                "' and main_tag.name='" + tag + "'")
        qs = Quiz.objects.raw("SELECT * from quiz_quiz inner join quiz_tag on quiz_tag.quiz_id=quiz_quiz.id inner "
                              "join main_tag on main_tag.id=quiz_tag.tag_id where "
                              "quiz_quiz.start<='" + str(query_date) + "' and quiz_quiz.end>'" + str(date) +
                              "' and main_tag.name='" + tag + "'")
    else:
        ls = Lesson.objects.filter(release__lt=query_date, drop_off_date__gt=date)
        qs = Quiz.objects.filter(start__lte=query_date, end__gt=date)
    next_date = date + timedelta(days=1)
    nxt = str(next_date.year) + '-' + str(next_date.month) + '-' + str(next_date.day)
    prev_date = date + timedelta(days=-1)
    prv = str(prev_date.year) + '-' + str(prev_date.month) + '-' + str(prev_date.day)
    return render(req, "content/course.html", {
        'tarikh': date,
        'lessons': ls,
        'next': nxt,
        'prev': prv,
        'tag': tag,
        'quizzes': qs,
    })


def lessonView(req, date, lesson, tag="all"):
    if date.today() < date and not req.user.is_staff:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})

    query_date = date + timedelta(days=1)
    if tag != "all":
        lessons = [les for les in
                   Lesson.objects.raw("SELECT * from course_lesson  inner join course_tag on course_tag.course_id="
                                      "course_lesson.course_id inner join main_tag on main_tag.id=course_tag.tag_id "
                                      "where course_lesson.release<'" + str(query_date) +
                                      "' and course_lesson.drop_off_date>'" + str(date) +
                                      "' and main_tag.name='" + tag + "'")]
        l = Lesson.objects.raw("SELECT * from course_lesson  inner join course_tag on course_tag.course_id="
                               "course_lesson.course_id inner join main_tag on main_tag.id=course_tag.tag_id "
                               "where course_lesson.release<'" + str(query_date) +
                               "' and course_lesson.drop_off_date>'" + str(date) +
                               "' and main_tag.name='" + tag + "' and course_lesson.name='" + lesson + "' group by course_lesson.name")
        if len(l) != 1:
            return HttpResponseNotFound('<h1>این درس پیدا نشد</h1>')
        else:
            l = l[0]
    else:
        lessons = [les for les in Lesson.objects.filter(release__lt=query_date, drop_off_date__gt=date)]
        l = get_object_or_404(Lesson, name=lesson, release__lt=query_date, drop_off_date__gt=date)
    c = get_object_or_404(Course, id=l.course_id)
    next, prev = None, None
    if len(lessons) > lessons.index(l) + 1:
        next = lessons[lessons.index(l) + 1]
    if lessons.index(l) > 0:
        prev = lessons[lessons.index(l) - 1]
    return render(req, "content/lesson.html", {
        'lesson': l,
        'title': l.title,
        'content': markdown(l.text),
        'is_staff': req.user.is_staff,
        'tag': tag,
        'next': next,
        'prev': prev,
        'comment': json_of_root('/courses/' + c.name + '/' + lesson, req.user),
    })
