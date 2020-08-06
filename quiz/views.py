from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer
from users.models import Student
from django.utils import timezone
from json import dumps

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
