from django.shortcuts import render, get_object_or_404, redirect
from .models import Quiz, Question, Answer, Secret, Collection, CollectionQuiz
from users.models import Student, OJHandle
from django.utils import timezone
from django.http import JsonResponse
from json import dumps, loads
from django.db.models import Sum, Q, Window, F
from django.db.models.functions import Rank
from .oj.codeforces import judge as judgeCF
from .oj.atcoder import judge as judgeAT
from django.core.serializers.json import DjangoJSONEncoder

def get_answer(qu, stu):
    qs = Answer.objects.filter(question= qu, student= stu)
    if not qs.exists():
        return {
            'text': "",
            'grade': 0,
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

def collectionScoreBoardView(req, name):
    q = get_object_or_404(Collection, name= name)
    stu = Student.objects.raw('SELECT * FROM (SELECT student_id as id, SUM(grade * quiz_collectionquiz.multiple) as nomre FROM quiz_answer INNER JOIN quiz_question ON question_id=quiz_question.id INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id WHERE quiz_collectionquiz.collection_id="'+ str(q.id) +'" GROUP BY student_id ORDER BY nomre DESC) WHERE nomre > 0;')
    return render(req, "quiz/ranking.html", {
        'students': stu,
    })
 
def next_rate(prev_rate, grade, max_grade):
    max_rate = 600
    f = prev_rate * max_grade / max_rate / max_rate
    prev_rate *= (1-f)
    return prev_rate+grade
    
def collectionProfileView(req, name, user):
    q = get_object_or_404(Collection, name= name)
    yaroo = get_object_or_404(Student, id= int(user))
    stu = Student.objects.raw('SELECT * FROM   (SELECT 0 as rate, quiz_collectionquiz.id as id, SUM(mxgrade*quiz_collectionquiz.multiple) as maxgrade, SUM(grade * quiz_collectionquiz.multiple) as nomre,   (quiz_quiz.title || " | " || cast(SUM(grade * quiz_collectionquiz.multiple) as text) || "امتیاز") as desc  FROM quiz_answer INNER JOIN quiz_question ON question_id=quiz_question.id   INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id   INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id   WHERE quiz_collectionquiz.collection_id='+str(q.id)+' and student_id='+str(yaroo.id)+' GROUP BY quiz_collectionquiz.id ORDER BY id) WHERE nomre > 0;')
    rates=[]
    rt=0
    for pers in stu:
        rt=next_rate(rt,pers.nomre,pers.maxgrade)
        pers.rate=rt
        rates.append(pers)
    return render(req, "quiz/profile.html", {
        'Rates': rates,
        'last_rate': rt,
        'user': user,
    })

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

def pickAnswerFromJson(req, name):
    if (not req.user.is_staff):
        return redirect("/users/login")
    if req.method == 'GET':
        return render(req, "quiz/pickjson.html")
    n = req.POST['order']
    qu = get_object_or_404(Question, quiz__name= name, order= n)
    data = loads(req.POST['answer'])
    Answer.objects.filter(question= qu).delete()
    for x in data:
        try:
            stu = None
            if qu.text.split("\n")[0] == "ATCODER":
                stu = OJHandle.objects.get(judge= "ATCODER", handle= x['handle']).student        
            else:
                stu = Student.objects.get(user__username= x['handle'])
            Answer.objects.create(
                question= qu,
                student= stu,
                text= ".",
                grade= x['total_points'],
                grademsg= "تصحیح با داوری خارجی",
            )
        except Exception as e:
            print(e)
            print(x)
    return redirect("../scoreboard/")


def autoCheckerView(req, name):
    if (not req.user.is_staff):
        return redirect("/users/login")
    qu = Question.objects.filter(quiz__name= name)
    for q in qu:
        if q.typ[0] != 'O' or q.typ == 'OJ':
            if q.typ != 'auto':
                continue
        Answer.objects.filter(question= q).update(grade= 0, grademsg= "تصحیح خودکار. پاسخ صحیح:" + q.hint)
        Answer.objects.filter(question= q, text= q.hint.strip()).update(grade= q.mxgrade)
    return redirect("../scoreboard/")

def pickAnswerFromOJView(req, name):
    if (not req.user.is_staff):
        return redirect("/users/login")
    qu = Question.objects.filter(quiz__name= name, typ= "OJ")
    qs = []
    for q in qu:
        if q.text[:2] == "AT":
            try:
                Answer.objects.filter(question= q).delete()
                problems = q.text.split("\n")[1].split(" ")
                handles = [ x.handle for x in OJHandle.objects.filter(judge= "ATCODER") ]
                data = judgeAT(handles, problems, q.mxgrade)
                ignored = []
                evaled = 0
                for x in data:
                    try:
                        stu = OJHandle.objects.get(judge= "ATCODER", handle= x['handle']).student
                        Answer.objects.create(
                            question= q,
                            student= stu,
                            text= ".",
                            grade= x['total_points'],
                            grademsg= "تصحیح با داوری خارجی"
                        )
                        evaled += 1
                    except Exception as e:
                        ignored.append(str(e))
                qs.append({
                    "order": q.order,
                    "subtyp": "اتکدر",
                    "evaled": evaled,
                    "ignored": ignored,
                })
            except Exception as e:
                qs.append({
                    "order": q.order,
                    "subtyp": "اتکدر",
                    "error": str(e),
                })
        if q.text[:2] == "CF":
            try:
                secret = Secret.objects.get(key= "CF_API").value
                data = judgeCF(secret, q.text[3:], q.mxgrade)
                ignored = []
                evaled = 0
                for x in data:
                    try:
                        stu = OJHandle.objects.get(judge= "CF", handle= x['handle']).student
                        Answer.objects.filter(question= q, student= stu).delete()
                        Answer.objects.create(
                            question= q,
                            student= stu,
                            text= ".",
                            grade= x['total_points'],
                            grademsg= "تصحیح با داوری خارجی"
                        )
                        evaled += 1
                    except Exception as e:
                        ignored.append(str(e))
                qs.append({
                    "order": q.order,
                    "subtyp": "کد فرسز",
                    "evaled": evaled,
                    "ignored": ignored,
                })
            except Exception as e:
                qs.append({
                    "order": q.order,
                    "subtyp": "کد فرسز",
                    "error": str(e),
                })
    return render(req, "quiz/oj.html", {
        "questions": qs,
    })

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
    stu = get_object_or_404(Student, user= req.user)
    if q.end < timezone.now():
        return render(req, "quiz/current.html", {
            'mode': 'visit',
            'quiz': q,
            'current': timezone.now(),
            'problems': json_of_problems(Question.objects.filter(quiz= q), stu),
        })
    return render(req, "quiz/current.html", {
        'mode': 'current',
        'quiz': q,
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz= q), stu),
    })
