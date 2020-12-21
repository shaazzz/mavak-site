import copy
from json import dumps, loads

from django.db.models import Sum, Q
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.utils import timezone

from comment.json import json_of_root
from main.markdown import markdown
from users.models import Collection
from users.models import Student, OJHandle
from .models import Question, Answer, Secret, CollectionQuiz, RateColor, Quiz
from .oj.CodeforcesCrawl import add_friends
from .oj.OJHandler import getView as OJGetView, autoCheckerHandler
from .oj.OJHandler import pick


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
        'text': x.text if x.typ != "OJ" else OJGetView(x),
        'mxgrade': x.mxgrade,
        'order': x.order,
        'typ': x.typ,
        'answer': get_answer(x, stu),
    } for x in qs]))


def checkedView(req, collection, name, user):
    if not req.user.is_staff:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})
    yaroo = get_object_or_404(Student, user__username=user)
    ans = loads(req.POST['answers'])
    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    q = coll_quiz.quiz
    for x in ans:
        ano = get_object_or_404(
            Answer, student=yaroo, question__id=x['id'], question__quiz=q
        )
        ano.grade = x['grade']
        ano.grademsg = x['grademsg']
        ano.save()
    return JsonResponse({'ok': True})


def submitView(req, collection, name):
    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    q = coll_quiz.quiz
    if req.user.is_anonymous:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})
    if coll_quiz.start > timezone.now():
        return JsonResponse({'ok': False, 'reason': 'not started'})
    if coll_quiz.end < timezone.now():
        return JsonResponse({'ok': False, 'reason': 'finished'})
    stu = get_object_or_404(Student, user=req.user)
    Answer.objects.filter(question__quiz=q, student=stu).delete()
    ans = loads(req.POST['answers'])
    for x in ans:
        ques = get_object_or_404(Question, id=x['id'])
        Answer.objects.create(question=ques, student=stu, text=x['text'], grade=-1, grademsg="تصحیح نشده")
    return JsonResponse({'ok': True})


def getLastRates(name):
    col = get_object_or_404(Collection, name=name)
    stu = Student.objects.raw(
        'SELECT * FROM   (SELECT 0 as rate, quiz_answer.student_id, quiz_collectionquiz.expectedScore, '
        'quiz_collectionquiz.id as id, SUM(mxgrade*quiz_collectionquiz.multiple) as maxgrade, '
        'SUM(grade * quiz_collectionquiz.multiple) as nomre, (quiz_quiz.title || " | " || '
        'cast(SUM(grade * quiz_collectionquiz.multiple) as text) || "/" || '
        'cast(SUM(mxgrade * quiz_collectionquiz.multiple) as text) || " ریتینگ") as desc FROM quiz_answer '
        'INNER JOIN quiz_question ON question_id=quiz_question.id INNER JOIN quiz_quiz ON '
        'quiz_question.quiz_id=quiz_quiz.id INNER join users_studentgroup_students on '
        'users_studentgroup_students.student_id=quiz_answer.student_id INNER JOIN users_collection '
        'on users_collection.students_id=users_studentgroup_students.studentgroup_id '
        'INNER JOIN quiz_collectionquiz ON quiz_quiz.id=quiz_collectionquiz.quiz_id and quiz_collectionquiz.end<="'
        + str(timezone.now()) +
        '" WHERE users_collection.id=' + str(col.id) +
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
                                     + str(col.id) + ' and quiz_collectionquiz.end<="' + str(
        timezone.now()) + '" GROUP BY quiz_collectionquiz.id ORDER BY id')
    students = Student.objects.raw("SELECT users_student.id from users_student "
                                   "INNER join users_studentgroup_students on"
                                   " users_studentgroup_students.student_id=users_student.id "
                                   "INNER join users_collection on "
                                   "users_collection.students_id=users_studentgroup_students.studentgroup_id "
                                   "where users_collection.id=" + str(col.id))
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
    col = get_object_or_404(Collection, name=name)
    stu = Student.objects.raw(
        'SELECT * FROM '
        ' (SELECT quiz_answer.student_id as id, SUM(grade * quiz_collectionquiz.multiple) as nomre FROM quiz_answer'
        ' INNER JOIN quiz_question ON quiz_answer.question_id=quiz_question.id'
        ' INNER join quiz_collectionquiz on quiz_collectionquiz.quiz_id=quiz_question.quiz_id and '
        'quiz_collectionquiz.end<="' + str(timezone.now()) +
        '" INNER join users_collection on users_collection.id=quiz_collectionquiz.collection_id'
        ' INNER join users_studentgroup_students on quiz_answer.student_id=users_studentgroup_students.student_id '
        ' INNER join users_studentgroup on users_studentgroup_students.studentgroup_id=users_studentgroup.id'
        ' and users_collection.students_id=users_studentgroup.id'
        ' WHERE users_collection.id=' + str(
            col.id) + ' GROUP BY quiz_answer.student_id ORDER BY nomre DESC) WHERE nomre > 0;')

    acc = Student.objects.raw(
        'SELECT * FROM '
        ' (SELECT users_ojhandle.handle, quiz_answer.student_id as id, SUM(grade * quiz_collectionquiz.multiple) '
        ' as nomre FROM quiz_answer INNER JOIN quiz_question ON question_id=quiz_question.id '
        'INNER JOIN users_ojhandle ON users_ojhandle.student_id=quiz_answer.student_id AND users_ojhandle.judge="CF" '
        'INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id and '
        'quiz_collectionquiz.end<="' + str(timezone.now()) +
        '" WHERE quiz_collectionquiz.collection_id=' + str(
            col.id) + ' GROUP BY quiz_answer.student_id ORDER BY nomre DESC) WHERE nomre > 0;')

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
        'title': col.title,
        "collection_name": col.name,
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
    col = get_object_or_404(Collection, name=name)
    yaroo = get_object_or_404(Student, id=int(user))
    stu = Student.objects.raw(
        'SELECT * FROM   (SELECT 0 as rate, quiz_quiz.title as title, '
        'quiz_collectionquiz.expectedScore, quiz_collectionquiz.id as id, '
        'SUM(mxgrade*quiz_collectionquiz.multiple) as maxgrade, SUM(grade * quiz_collectionquiz.multiple) as nomre,'
        ' (quiz_quiz.title || " | " || cast(SUM(grade * quiz_collectionquiz.multiple) as text) || "/" || '
        'cast(SUM(mxgrade * quiz_collectionquiz.multiple) as text) || " امتیاز") as desc  FROM quiz_answer '
        'INNER JOIN quiz_question ON question_id=quiz_question.id '
        'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
        'INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
        'and quiz_collectionquiz.end<="' + str(timezone.now()) +
        '" WHERE quiz_collectionquiz.collection_id=' + str(
            col.id) + ' and student_id=' + str(
            yaroo.id) + ' GROUP BY quiz_collectionquiz.id ORDER BY id) WHERE nomre > 0;')
    quz = CollectionQuiz.objects.raw('SELECT *, '
                                     '(quiz_quiz.title || " | 0/" || cast(SUM(mxgrade * quiz_collectionquiz.multiple) '
                                     'as text) || " امتیاز") '
                                     'as desc, quiz_collectionquiz.expectedScore, SUM(multiple*mxgrade) '
                                     'as maxgrade FROM quiz_collectionquiz '
                                     'INNER JOIN quiz_question ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
                                     'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
                                     'WHERE quiz_collectionquiz.collection_id='
                                     + str(col.id) + ' and quiz_collectionquiz.end<="' + str(timezone.now()) +
                                     '" GROUP BY quiz_collectionquiz.id ORDER BY id')
    acc = Student.objects.raw(
        'SELECT * FROM '
        ' (SELECT users_ojhandle.handle, quiz_collectionquiz.expectedScore, quiz_answer.student_id as id, '
        'SUM(grade * quiz_collectionquiz.multiple) as nomre FROM quiz_answer '
        'INNER JOIN quiz_question ON question_id=quiz_question.id '
        'INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
        'INNER JOIN users_ojhandle ON users_ojhandle.student_id=quiz_answer.student_id AND users_ojhandle.judge="CF" '
        'INNER JOIN quiz_collectionquiz ON quiz_question.quiz_id=quiz_collectionquiz.quiz_id '
        'and quiz_collectionquiz.end<="' + str(timezone.now()) +
        '" WHERE quiz_collectionquiz.collection_id=' + str(
            col.id) + ' and quiz_answer.student_id=' + str(
            yaroo.id) + ' GROUP BY quiz_answer.student_id ORDER BY nomre DESC) WHERE nomre > 0;')

    rate_colors = RateColor.objects.raw('SELECT * from quiz_ratecolor')

    rates = []
    rt = 100
    sum_nomre = 0
    for qu in quz:
        for pers in stu:
            if pers.id == qu.id:
                pers.maxgrade = qu.maxgrade
                pers.desc = pers.title + ' | ' + str(pers.nomre) + '/' + str(pers.maxgrade) + " امتیاز"
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


def scoreBoardView(req, collection, name):
    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    q = coll_quiz.quiz
    if not req.user.is_staff:
        return redirect("/users/login")
    stu = Student.objects.annotate(
        nomre=Sum("answer__grade", filter=Q(answer__question__quiz=q))
    ).filter(~Q(nomre=None)).order_by("-nomre")
    return render(req, "quiz/scoreboard.html", {
        'students': stu,
    })


def pickAnswerFromJson(req, collection, name):
    if not req.user.is_staff:
        return redirect("/users/login")
    if req.method == 'GET':
        return render(req, "quiz/pickjson.html")
    n = req.POST['order']
    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    qu = get_object_or_404(Question, quiz=coll_quiz.quiz, order=n)
    data = loads(req.POST['answer'])
    Answer.objects.filter(question=qu).delete()
    for x in data:
        try:
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



def autoCheckerView(req, collection, name):
    mode = "strict"
    if "mode" in req.GET:
        mode = req.GET["mode"]
    if not req.user.is_staff:
        return redirect("/users/login")

    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    autoCheckerHandler(coll_quiz.quiz, mode)
    return redirect("../scoreboard/")


def pickAnswerFromOJView(req, collection, name):
    if not req.user.is_staff:
        return redirect("/users/login")

    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    qu = Question.objects.filter(quiz=coll_quiz.quiz, typ="OJ")
    qs = []
    for q in qu:
        pick(q.id)
    return render(req, "quiz/oj.html", {
        "questions": qs,
    })


def checkView(req, collection, name, user):
    if not req.user.is_staff:
        return redirect("/users/login")
    yaroo = get_object_or_404(Student, user__username=user)
    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    q = coll_quiz.quiz
    return render(req, "quiz/current.html", {
        'mode': 'check',
        'quiz': q,
        'coll_quiz': coll_quiz,
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz=q), yaroo),
        'user': yaroo.user,
    })


def quizView(req, collection, name):
    # is_staff  condition is necessary!!!!!! important !!!!!!!!!!!!!!!
    if collection == 'admin' and req.user.is_staff:
        stu = get_object_or_404(Student, id=1)
        q = get_object_or_404(Quiz, name=name)
        return render(req, "quiz/current.html", {
            'mode': 'visit',
            'quiz': q,
            'desc': markdown(q.desc),
            'current': timezone.now(),
            'problems': json_of_problems(Question.objects.filter(quiz=q), stu),
            'user': stu.user,
            'comment': json_of_root('/quiz/' + collection + "/" + name + '/', req.user),
        })
    coll_quiz = get_object_or_404(CollectionQuiz, collection__name=collection, quiz__name=name)
    q = coll_quiz.quiz
    if req.user.is_anonymous:
        return redirect("/users/login")
    if req.user.is_staff:
        return redirect("/quiz/{}/{}/scoreboard".format(collection, name))
    stu = get_object_or_404(Student, user=req.user)
    if coll_quiz.end < timezone.now():
        return render(req, "quiz/current.html", {
            'mode': 'visit',
            'quiz': q,
            'coll_quiz': coll_quiz,
            'desc': markdown(q.desc),
            'current': timezone.now(),
            'problems': json_of_problems(Question.objects.filter(quiz=q), stu),
            'user': stu.user,
            'comment': json_of_root('/quiz/' + collection + "/" + name + '/', req.user),
        })
    if coll_quiz.start > timezone.now():
        return render(req, "quiz/not_started.html", {
            'quiz': q,
            'coll_quiz': coll_quiz,
            'desc': markdown(q.desc),
            'current': timezone.now(),
        })
    return render(req, "quiz/current.html", {
        'mode': 'current',
        'quiz': q,
        'coll_quiz': coll_quiz,
        'desc': markdown(q.desc),
        'current': timezone.now(),
        'problems': json_of_problems(Question.objects.filter(quiz=q), stu),
        'user': stu.user,
    })


def addCFFriends(req):
    if not req.user.is_staff:
        return JsonResponse({'ok': False, 'reason': 'anonymous'})
    try:
        handles = [ojh.handle for ojh in OJHandle.objects.filter(judge="CF")]
        print(handles)
        secret = Secret.objects.get(key="CF_LOGIN").value
        add_friends(secret, handles)
        return JsonResponse({'ok': True, "handles": handles})
    except Exception as e:
        return JsonResponse({'ok': False, "reason": str(e)})
