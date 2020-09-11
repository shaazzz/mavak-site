from django.shortcuts import render, get_object_or_404, redirect
from markdown2 import markdown

from comment.json import json_of_root
from .models import Quiz, Question, Answer, Secret, Collection, CollectionQuiz, RateColor
from users.models import Student, OJHandle
from django.utils import timezone
from django.http import JsonResponse
from json import dumps, loads
from django.db.models import Sum, Q, Window, F
from django.db.models.functions import Rank
from .oj.codeforces import judge as judgeCF
from .oj.atcoder import judge as judgeAT
from django.core.serializers.json import DjangoJSONEncoder
import copy


def get_answer(qu, stu):
    qs = Answer.objects.filter(question=qu, student=stu)
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
        'id': x.id,
        'text': x.text,
        'mxgrade': x.mxgrade,
        'order': x.order,
        'typ': x.typ,
        'answer': get_answer(x, stu),
    } for x in qs]))


def checkedView(req, name, user):
    if (not req.user.is_staff):
        return JsonResponse({'ok': False, 'reason': 'anonymous'})
    yaroo = get_object_or_404(Student, user__username=user)
    q = get_object_or_404(Quiz, name=name)
    ans = loads(req.POST['answers'])
    for x in ans:
        ano = get_object_or_404(
            Answer, student=yaroo, question__id=x['id']
        )
        ano.grade = x['grade']
        ano.grademsg = x['grademsg']
        ano.save()
    return JsonResponse({'ok': True})


def submitView(req, name):
    q = get_object_or_404(Quiz, name=name)
    if req.user.is_anonymous:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})
    if q.start > timezone.now():
        return JsonResponse({'ok': False, 'reason': 'not started'})
    if q.end < timezone.now():
        return JsonResponse({'ok': False, 'reason': 'finished'})
    stu = get_object_or_404(Student, user=req.user)
    Answer.objects.filter(question__quiz=q, student=stu).delete()
    ans = loads(req.POST['answers'])
    for x in ans:
        ques = get_object_or_404(Question, id=x['id'])
        Answer.objects.create(question=ques, student=stu, text=x['text'], grade=-1, grademsg="تصحیح نشده")
    return JsonResponse({'ok': True})


def getLastRates(name):
    q = get_object_or_404(Collection, name=name)
    stu = Student.objects.raw(
        'SELECT * FROM   (SELECT 0 as rate, quiz_answer.student_id, quiz_collectionquiz.expectedScore, '
        'quiz_collectionquiz.id as id, SUM(mxgrade*quiz_collectionquiz.multiple) as maxgrade, '
        'SUM(grade * quiz_collectionquiz.multiple) as nomre, (quiz_quiz.title || " | " || '
        'cast(SUM(grade * quiz_collectionquiz.multiple) as text) || "/" || '
        'cast(SUM(mxgrade * quiz_collectionquiz.multiple) as text) || " ریتینگ") as desc FROM quiz_answer '
        'INNER JOIN quiz_question ON question_id=quiz_question.id INNER JOIN quiz_quiz ON '
        'quiz_question.quiz_id=quiz_quiz.id INNER join users_studentgroup_students on '
        'users_studentgroup_students.student_id=quiz_answer.student_id INNER JOIN quiz_collection '
        'on quiz_collection.students_id=users_studentgroup_students.studentgroup_id '
        'INNER JOIN quiz_collectionquiz ON quiz_quiz.id=quiz_collectionquiz.quiz_id '
        'WHERE quiz_collection.id=' + str(q.id) +
        ' GROUP BY quiz_collectionquiz.id, quiz_answer.student_id ORDER BY id) WHERE nomre > 0;'
    )
    quz = CollectionQuiz.objects.raw('SELECT *, '
                                     '(quiz_quiz.title || " | 0/" || cast(SUM(mxgrade * quiz_collectionquiz.multiple) '
                                     'as text) || " ریتینگ") '
                                     'as desc, quiz_collectionquiz.expectedScore, '
                                     'SUM(multiple*mxgrade) as maxgrade FROM quiz_collectionquiz '
                                     'INNER JOIN quiz_question ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
                                     'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
                                     'WHERE quiz_collectionquiz.collection_id='
                                     + str(q.id) + ' GROUP BY quiz_collectionquiz.id ORDER BY id')
    students = Student.objects.raw("SELECT users_student.id from users_student "
                                   "INNER join users_studentgroup_students on"
                                   " users_studentgroup_students.student_id=users_student.id "
                                   "INNER join quiz_collection on "
                                   "quiz_collection.students_id=users_studentgroup_students.studentgroup_id "
                                   "where quiz_collection.id=" + str(q.id))
    rt = {}
    data = []
    for pers in students:
        rt[pers.id] = 100
    for qu in quz:
        mark = {}
        for pers in stu:
            data.append(pers.nomre)
            if pers.id == qu.id:
                rt[pers.student_id] = next_rate(rt[pers.student_id], pers.expectedScore, pers.nomre, pers.maxgrade)
                mark[pers.student_id] = True
        for pers in students:
            if pers.id not in mark:
                rt[pers.id] = next_rate(rt[pers.id], qu.expectedScore, 0, qu.maxgrade)
                mark[pers.id] = True
    return rt


def collectionScoreBoardView(req, name):
    q = get_object_or_404(Collection, name=name)
    stu = Student.objects.raw(
        'SELECT * FROM '
        ' (SELECT quiz_answer.student_id as id, SUM(grade * quiz_collectionquiz.multiple) as nomre FROM quiz_answer'
        ' INNER JOIN quiz_question ON quiz_answer.question_id=quiz_question.id'
        ' INNER join quiz_collectionquiz on quiz_collectionquiz.quiz_id=quiz_question.quiz_id'
        ' INNER join quiz_collection on quiz_collection.id=quiz_collectionquiz.collection_id'
        ' INNER join users_studentgroup_students on quiz_answer.student_id=users_studentgroup_students.student_id '
        ' INNER join users_studentgroup on users_studentgroup_students.studentgroup_id=users_studentgroup.id'
        ' and quiz_collection.students_id=users_studentgroup.id'
        ' WHERE quiz_collection.id=' + str(
            q.id) + ' GROUP BY quiz_answer.student_id ORDER BY nomre DESC) WHERE nomre > 0;')
    acc = Student.objects.raw(
        'SELECT * FROM '
        ' (SELECT users_ojhandle.handle, quiz_answer.student_id as id, SUM(grade * quiz_collectionquiz.multiple) '
        ' as nomre FROM quiz_answer INNER JOIN quiz_question ON question_id=quiz_question.id '
        'INNER JOIN users_ojhandle ON users_ojhandle.student_id=quiz_answer.student_id AND users_ojhandle.judge="CF" '
        'INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
        'WHERE quiz_collectionquiz.collection_id=' + str(
            q.id) + ' GROUP BY quiz_answer.student_id ORDER BY nomre DESC) WHERE nomre > 0;')
    rate_colors = RateColor.objects.raw('SELECT * from quiz_ratecolor')

    rt = getLastRates(name)
    new_stu = []
    for s in stu:
        new_s = copy.copy(s)
        new_s.nomre = rt[s.id]
        if new_s.nomre >= 0:
            new_s.user_color = None
            for rate_color in rate_colors:
                if rate_color.startValue <= new_s.nomre < rate_color.endValue:
                    new_s.user_color = rate_color
            new_stu.append(new_s)

    new_stu = sorted(new_stu, key=lambda x: -x.nomre)
    return render(req, "quiz/ranking.html", {
        'students': new_stu,
        'cf_accounts': acc,
        'title': q.title,
        "collection_name": q.name,
    })


def next_rate(prev_rate, expected_score, grade, max_grade):
    scale = 0.5
    grade *= scale
    expected_score *= scale
    grade -= expected_score / 2
    max_grade *= scale
    max_rate = 800
    f = prev_rate * max_grade / max_rate / max_rate
    prev_rate *= (1 - f)
    return int(prev_rate + grade)


def collectionProfileView(req, name, user):
    q = get_object_or_404(Collection, name=name)
    yaroo = get_object_or_404(Student, id=int(user))
    stu = Student.objects.raw(
        'SELECT * FROM   (SELECT 0 as rate, quiz_collectionquiz.expectedScore, quiz_collectionquiz.id as id, '
        'SUM(mxgrade*quiz_collectionquiz.multiple) as maxgrade, SUM(grade * quiz_collectionquiz.multiple) as nomre,'
        ' (quiz_quiz.title || " | " || cast(SUM(grade * quiz_collectionquiz.multiple) as text) || "/" || '
        'cast(SUM(mxgrade * quiz_collectionquiz.multiple) as text) || " امتیاز") as desc  FROM quiz_answer '
        'INNER JOIN quiz_question ON question_id=quiz_question.id '
        'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
        'INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
        'WHERE quiz_collectionquiz.collection_id=' + str(
            q.id) + ' and student_id=' + str(
            yaroo.id) + ' GROUP BY quiz_collectionquiz.id ORDER BY id) WHERE nomre > 0;')
    quz = CollectionQuiz.objects.raw('SELECT *, '
                                     '(quiz_quiz.title || " | 0/" || cast(SUM(mxgrade * quiz_collectionquiz.multiple) '
                                     'as text) || " امتیاز") '
                                     'as desc, quiz_collectionquiz.expectedScore, SUM(multiple*mxgrade) as maxgrade FROM quiz_collectionquiz '
                                     'INNER JOIN quiz_question ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
                                     'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
                                     'WHERE quiz_collectionquiz.collection_id='
                                     + str(q.id) + ' GROUP BY quiz_collectionquiz.id ORDER BY id')
    acc = Student.objects.raw(
        'SELECT * FROM '
        ' (SELECT users_ojhandle.handle, quiz_collectionquiz.expectedScore, quiz_answer.student_id as id, '
        'SUM(grade * quiz_collectionquiz.multiple) as nomre FROM quiz_answer '
        'INNER JOIN quiz_question ON question_id=quiz_question.id '
        'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
        'INNER JOIN users_ojhandle ON users_ojhandle.student_id=quiz_answer.student_id AND users_ojhandle.judge="CF" '
        'INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
        'WHERE quiz_collectionquiz.collection_id=' + str(
            q.id) + ' and quiz_answer.student_id=' + str(
            yaroo.id) + ' GROUP BY quiz_answer.student_id ORDER BY nomre DESC) WHERE nomre > 0;')

    rate_colors = RateColor.objects.raw('SELECT * from quiz_ratecolor')

    rates = []
    rt = 100
    sum_nomre = 0
    for qu in quz:
        for pers in stu:
            if pers.id == qu.id:
                rt = next_rate(rt, pers.expectedScore, pers.nomre, pers.maxgrade)
                pers.rate = rt
                sum_nomre += pers.nomre
                rates.append(pers)
                break
        else:
            new_pers = copy.copy(yaroo)
            new_pers.id = qu.id
            new_pers.nomre = 0
            new_pers.desc = qu.desc
            new_pers.expectedScore = qu.expectedScore
            new_pers.maxgrade = qu.maxgrade
            rt = next_rate(rt, new_pers.expectedScore, new_pers.nomre, new_pers.maxgrade)
            new_pers.rate = rt
            rates.append(new_pers)
    user_color = None
    for rate_color in rate_colors:
        if rate_color.startValue <= rt < rate_color.endValue:
            user_color = rate_color

    return render(req, "quiz/profile.html", {
        'Rates': rates,
        'cf_accounts': acc,
        'rate_colors': rate_colors,
        'user_color': user_color,
        'last_rate': rt,
        'user': yaroo,
    })


def scoreBoardView(req, name):
    q = get_object_or_404(Quiz, name=name)
    if not req.user.is_staff:
        return redirect("/users/login")
    stu = Student.objects.annotate(
        nomre=Sum("answer__grade", filter=Q(answer__question__quiz=q))
    ).filter(~Q(nomre=None)).order_by("-nomre")
    return render(req, "quiz/scoreboard.html", {
        'students': stu,
    })


def pickAnswerFromJson(req, name):
    if (not req.user.is_staff):
        return redirect("/users/login")
    if req.method == 'GET':
        return render(req, "quiz/pickjson.html")
    n = req.POST['order']
    qu = get_object_or_404(Question, quiz__name=name, order=n)
    data = loads(req.POST['answer'])
    Answer.objects.filter(question=qu).delete()
    for x in data:
        try:
            stu = None
            if qu.text.split("\n")[0] == "ATCODER":
                stu = OJHandle.objects.get(judge="ATCODER", handle=x['handle']).student
            else:
                stu = Student.objects.get(user__username=x['handle'])
            Answer.objects.create(
                question=qu,
                student=stu,
                text=".",
                grade=x['total_points'],
                grademsg="تصحیح با داوری خارجی",
            )
        except Exception as e:
            print(e)
            print(x)
    return redirect("../scoreboard/")


def un_correct(s: str):
    new = ['۰', '۱', '۲', '۳', '۴', '۵', '۶', '۷', '۸', '۹']
    old = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
    for i in range(10):
        s = s.replace(old[i], new[i])
    return s


def autoCheckerView(req, name):
    mode = "strict"
    if "mode" in req.GET:
        mode = req.GET["mode"]
    if not req.user.is_staff:
        return redirect("/users/login")
    qu = Question.objects.filter(quiz__name=name)
    for q in qu:
        if q.typ[0] != 'O' or q.typ == 'OJ':
            if q.typ != 'auto':
                continue
        hint_reg = ""
        for c in q.hint.strip():
            hint_reg += '[,]{0,1}' + c
        Answer.objects.filter(question=q).update(grade=0, grademsg="تصحیح خودکار. پاسخ صحیح:" + q.hint)
        if mode == "strict":
            Answer.objects.filter(question=q, text__regex=r'^[ \n]*(' + hint_reg + '|' + un_correct(
                q.hint.strip()) + ')([^0123456789۰۱۲۳۴۵۶۷۸۹](.*[\n]*)*)*$').update(grade=q.mxgrade)
        else:
            Answer.objects.filter(question=q,
                                  text__regex=r'^[ \n]*(' + hint_reg + '|' + un_correct(
                                      q.hint.strip()) + ')([^0123456789۰۱۲۳۴۵۶۷۸۹](.*[\n]*)*)*$').update(
                grade=q.mxgrade)
            Answer.objects.filter(question=q, text__regex=r'^[ \n]*(' + hint_reg + '|' + un_correct(
                q.hint.strip()) + ')[ \n]*$').update(grade=(q.mxgrade + 1) / 2)
    return redirect("../scoreboard/")


def pickAnswerFromOJView(req, name):
    if (not req.user.is_staff):
        return redirect("/users/login")
    qu = Question.objects.filter(quiz__name=name, typ="OJ")
    qs = []
    for q in qu:
        if q.text[:2] == "AT":
            try:
                Answer.objects.filter(question=q).delete()
                problems = q.text.split("\n")[1].split(" ")
                handles = [x.handle for x in OJHandle.objects.filter(judge="ATCODER")]
                data = judgeAT(handles, problems, q.mxgrade)
                ignored = []
                evaled = 0
                for x in data:
                    try:
                        stu = OJHandle.objects.get(judge="ATCODER", handle=x['handle']).student
                        Answer.objects.create(
                            question=q,
                            student=stu,
                            text=".",
                            grade=x['total_points'],
                            grademsg="تصحیح با داوری خارجی"
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
                secret = Secret.objects.get(key="CF_API").value
                data = judgeCF(secret, q.text[3:], q.mxgrade)
                ignored = []
                evaled = 0
                for x in data:
                    try:
                        stu = OJHandle.objects.get(judge="CF", handle=x['handle']).student
                        Answer.objects.filter(question=q, student=stu).delete()
                        Answer.objects.create(
                            question=q,
                            student=stu,
                            text=".",
                            grade=x['total_points'],
                            grademsg="تصحیح با داوری خارجی"
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
    if not req.user.is_staff:
        return redirect("/users/login")
    yaroo = get_object_or_404(Student, user__username=user)
    q = get_object_or_404(Quiz, name=name)
    return render(req, "quiz/current.html", {
        'mode': 'check',
        'quiz': q,
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz=q), yaroo),
        'user': yaroo.user,
    })


def quizView(req, name):
    q = get_object_or_404(Quiz, name=name)
    if req.user.is_anonymous:
        return redirect("/users/login")
    if q.start > timezone.now():
        return render(req, "quiz/not_started.html", {
            'quiz': q,
            'desc': markdown(q.desc),
            'current': timezone.now(),
        })
    if req.user.is_staff:
        return redirect("/admin/quiz/quiz/"+str(q.id))
    stu = get_object_or_404(Student, user=req.user)
    if q.end < timezone.now():
        return render(req, "quiz/current.html", {
            'mode': 'visit',
            'quiz': q,
            'desc': markdown(q.desc),
            'current': timezone.now(),
            'problems': json_of_problems(Question.objects.filter(quiz=q), stu),
            'user': stu.user,
            'comment': json_of_root('/quiz/' + name + '/', req.user),
        })
    return render(req, "quiz/current.html", {
        'mode': 'current',
        'quiz': q,
        'desc': markdown(q.desc),
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz=q), stu),
        'user': stu.user,
    })
