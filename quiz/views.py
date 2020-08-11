from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer
from users.models import Student
from django.utils import timezone
from django.http import JsonResponse
from json import dumps, loads
from django.db.models import Sum, Q, Window, F
from django.db.models.functions import Rank

def get_answer(qu, stu):
    qs = Answer.objects.filter(question= qu, student= stu)
    if not qs.exists():
        return {
            'text': "",
            'grade': 'پاسخی داده نشده است. به این قسمت دست نزنید.',
            'grademsg': '',
        }
    ans = qs.first()
    return {
        'text': ans.text,
        'grade': ans.grade,
        'grademsg': ans.grademsg,
    }

def json_of_problems(qs, stu):
    return dumps(dumps([{
        'text': x.text,
        'mxgrade': x.mxgrade,
        'order': x.order,
        'typ': x.typ,
        'answer': get_answer(x, stu),
    } for x in qs ]))

def checkedView(req, name, user):
    if (not req.user.is_staff):
        return JsonResponse({ 'ok': False, 'reason': 'anonymous' })
    yaroo = get_object_or_404(Student, user__username= user)
    q = get_object_or_404(Quiz, name= name)
    ans = loads(req.POST['answers'])
    for x in ans:
        ano = get_object_or_404(
            Answer, question__quiz= q, student= yaroo, question__order= x['order']
        )
        ano.grade = x['grade']
        ano.grademsg = x['grademsg']
        ano.save()
    return JsonResponse({ 'ok': True })

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
    q = get_object_or_404(Quiz, name= name)
    if not req.user.is_staff:
        return redirect("/users/login")
    stu = Student.objects.annotate(
        nomre= Sum("answer__grade", filter= Q(answer__question__quiz= q))
    ).filter(~Q(nomre= None)).order_by("-nomre")
    return render(req, "quiz/scoreboard.html", {
        'students': stu,
    })

def bulkCheckView(req, name):
    if (not req.user.is_staff):
        return redirect("/users/login")
    if req.method == 'GET':
        return render(req, "quiz/bulkcheck.html")
    n = req.POST['order']
    qu = get_object_or_404(Question, quiz__name= name, order= n)
    Answer.objects.filter(question= qu).update(grade= 0, grademsg= "تصحیح خودکار")
    Answer.objects.filter(question= qu, text= req.POST['answer']).update(grade= qu.mxgrade)
    return redirect("../scoreboard/")

def checkView(req, name, user):
    if (not req.user.is_staff):
        return redirect("/users/login")
    yaroo = get_object_or_404(Student, user__username= user)
    q = get_object_or_404(Quiz, name= name)
    return render(req, "quiz/current.html", {
        'mode': 'check',
        'quiz': q,
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz= q), yaroo),
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
        'mode': 'current',
        'quiz': q,
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz= q), stu),
    })
