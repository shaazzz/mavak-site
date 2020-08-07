from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer
from users.models import Student
from django.utils import timezone
from django.http import JsonResponse
from json import dumps, loads
from django.db.models import Sum

def get_answer(qu, stu):
    qs = Answer.objects.filter(question= qu, student= stu)
    if not qs.exists():
        return ""
    return qs.first().text

def json_of_problems(qs, stu):
    return dumps(dumps([{
        'text': x.text,
        'mxgrade': x.mxgrade,
        'order': x.order,
        'typ': x.typ,
        'answer': get_answer(x, stu),
    } for x in qs ]))

def submitView(req, name):
    q = get_object_or_404(Quiz, name= name)
    if req.user.is_anonymous:
        return JsonResponse({ 'ok': False, 'reason': 'anonymous' })
    if q.start > timezone.now():
        return JsonResponse({ 'ok': False, 'reason': 'not started' })
    if q.end < timezone.now():
        return JsonResponse({ 'ok': False, 'reason': 'finished' })
    stu = get_object_or_404(Student, user= req.user)
    Answer.objects.filter(question__quiz= q, student= stu).delete()
    ans = loads(req.POST['answers'])
    for x in ans:
        ques = get_object_or_404(Question, quiz= q, order= x['order'])
        Answer.objects.create(question= ques, student= stu, text= x['text'], grade= -1, grademsg= "تصحیح نشده")
    return JsonResponse({ 'ok': True })

def scoreBoardView(req, name):
    if not req.user.is_staff:
        return redirect("/users/login")
    stu = Answer.objects.values("student").annotate(nomre= Sum("grade"))
    return render(req, "quiz/scoreboard.html", {
        'students': stu,
    })

def quizView(req, name):
    q = get_object_or_404(Quiz, name= name)
    if req.user.is_anonymous:
        return redirect("/users/login")
    if q.start > timezone.now():
        return render(req, "quiz/not_started.html", {
            'quiz': q,
            'current': timezone.now(),
        })
    if q.end < timezone.now():
        return render(req, "quiz/finished.html", {
            'quiz': q,
        })
    stu = get_object_or_404(Student, user= req.user)
    return render(req, "quiz/current.html", {
        'quiz': q,
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz= q), stu),
    })
