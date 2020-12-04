from datetime import timedelta

from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils import timezone

from comment.json import json_of_root
from course.models import Course, Lesson, CollectionLesson
from main.markdown import markdown
from quiz.models import Quiz, CollectionQuiz
from users.models import Collection


def todayCourseView(req):
    collections = Collection.objects.filter(name__startswith='div')
    return render(req, "content/collections.html", {
        'pref': '/content/date/' + str(timezone.now().year) + '-' + str(timezone.now().month) + '-' + str(
            timezone.now().day),
        'collections': collections,
    })


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
    collections = Collection.objects.filter(name__startswith='div')
    return render(req, "content/collections.html", {
        'pref': '/content/syllabus',
        'collections': collections,
    })


def syllabusCollectionView(req, collection):
    condition = "and release<'" + timezone.now().strftime("%Y-%m-%d %H:%M:%S") + "'"
    if req.user.is_staff:
        condition = ""
    ls = Lesson.objects.raw("select course_lesson.*,'lesson' as type, course_collectionlesson.start as release, "
                            "course_collectionlesson.end as drop_off_date,"
                            "(DATE(course_collectionlesson.start, 'weekday 5', '-7 days')) "
                            "as date_id from course_collectionlesson "
                            "inner join course_lesson on course_lesson.id=course_collectionlesson.lesson_id "
                            "inner join users_collection on course_collectionlesson.collection_id="
                            "users_collection.id inner join course_tag on course_tag.course_id"
                            "=course_lesson.course_id INNER join main_tag on course_tag.tag_id=main_tag.id"
                            " where users_collection.name='" + collection + "'" + condition + " group by course_lesson"
                                                                                              ".id order by release")
    qs = Quiz.objects.raw("select quiz_quiz.*,'quiz' as type,quiz_collectionquiz.start as release,"
                          "quiz_collectionquiz.end as drop_off_date, (DATE(quiz_collectionquiz.start,"
                          " 'weekday 5', '-7 days')) as date_id from quiz_collectionquiz INNER join quiz_quiz"
                          " on quiz_quiz.id=quiz_collectionquiz.quiz_id INNER join users_collection on "
                          "quiz_collectionquiz.collection_id=users_collection.id inner join quiz_tag on "
                          "quiz_tag.quiz_id=quiz_quiz.id INNER join main_tag on quiz_tag.tag_id=main_tag.id"
                          " where users_collection.name='" + collection + "' " + "" + " group by quiz_quiz.id "
                                                                                      "order by release")

    ls = [row for row in ls] + [row for row in qs]
    for i in ls:
        i.release = i.release.replace(tzinfo=None)
    ls.sort(key=lambda x: x.release)
    return render(req, "content/syllabus.html", {
        'lesson_groups': getGroups(ls),
        'collection': collection,
    })


def courseView(req, date, collection):
    if date.today() < date and not req.user.is_staff:
        return render(req, "content/not_started.html", {
            'start_date': date,
            'current': timezone.now(),
        })
    query_date = date + timedelta(days=1)
    '''
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
        ls = Lesson.objects.filter(release__lt=query_date, drop_off_date__gt=date).values_list('pub_date')
        qs = Quiz.objects.filter(start__lte=query_date, end__gt=date)

'''
    ls = CollectionLesson.objects.filter(
        collection__name=collection, start__lt=query_date, end__gt=date)
    qs = CollectionQuiz.objects.filter(
        collection__name=collection, start__lt=query_date, end__gt=date)
    print(ls)
    next_date = date + timedelta(days=1)
    nxt = str(next_date.year) + '-' + str(next_date.month) + '-' + str(next_date.day)
    prev_date = date + timedelta(days=-1)
    prv = str(prev_date.year) + '-' + str(prev_date.month) + '-' + str(prev_date.day)
    return render(req, "content/course.html", {
        'tarikh': date,
        'lessons': ls,
        'next': nxt,
        'prev': prv,
        'collection': collection,
        'quizzes': qs,
    })


def lessonView(req, date, lesson, collection):
    if date.today() < date and not req.user.is_staff:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})

    query_date = date + timedelta(days=1)

    lessons = [lss for lss in CollectionLesson.objects.filter(
        collection__name=collection, start__lt=query_date, end__gt=date)]
    l = get_object_or_404(CollectionLesson, collection__name=collection, start__lt=query_date,
                          end__gt=date, lesson__name=lesson)
    c = get_object_or_404(Course, id=l.lesson.course_id)
    next, prev = None, None
    if len(lessons) > lessons.index(l) + 1:
        next = lessons[lessons.index(l) + 1].lesson.name
    if lessons.index(l) > 0:
        prev = lessons[lessons.index(l) - 1].lesson.name
    return render(req, "content/lesson.html", {
        'lesson': l,
        'title': l.lesson.title,
        'content': markdown(l.lesson.text),
        'is_staff': req.user.is_staff,
        'collection': collection,
        'next': next,
        'prev': prev,
        'comment': json_of_root('/courses/' + c.name + '/' + lesson, req.user),
    })
