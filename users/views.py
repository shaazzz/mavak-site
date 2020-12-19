import re

import requests
from django.contrib.auth import authenticate, login as dlogin
from django.contrib.auth.models import User
from django.db.models import Max, Count
from django.shortcuts import render, redirect, get_object_or_404

from quiz.models import Quiz
from .models import Student, Org, StudentGroup, OJHandle


def agreementView(req):
    if req.user.is_anonymous:
        return redirect("/users/login")
    stu = get_object_or_404(Student, user=req.user)
    if stu.verified < 1:
        return render(req, "users/rejected.html")
    if stu.verified > 1:
        return redirect("/users/me")
    if req.method == 'GET':
        return render(req, "users/agreement.html")
    print(req.FILES)
    if not 'shenasname' in req.FILES:
        return render(req, "users/agreement.html", {
            "error": "yes",
        })
    stu.shenasname = req.FILES['shenasname']
    stu.verified = 2
    stu.save()
    return redirect(".")


def is_valid_iran_code(input):
    if not re.search(r'^\d{10}$', input):
        return False

    check = int(input[9])
    s = sum([int(input[x]) * (10 - x) for x in range(9)]) % 11
    return (2 > s == check) or (s >= 2 and check + s == 11)


persiandigit = '۱۲۳۴۵۶۷۸۹۰١٢٣٤٥٦٧٨٩٠'
englishdigit = '12345678901234567890'
translation_table = str.maketrans(persiandigit, englishdigit)


def createAccountStudent(req):
    if req.method == 'GET':
        return render(req, 'users/createAccountStudent.html')
    nam = req.POST['nam']
    famil = req.POST['famil']
    kodemelli = req.POST['kodemelli'].translate(translation_table)
    ostan = req.POST['ostan']
    # dore = req.POST['dore']
    shomare = req.POST['shomare'].translate(translation_table)
    password = req.POST['password']
    email = req.POST['email']
    if not is_valid_iran_code(kodemelli):
        return render(req, 'users/createAccountStudent.html', {
            'error': 'bad',
        })

    try:
        user = User.objects.create_user(kodemelli, email, password)
        user.first_name = nam
        user.last_name = famil
        user.save()
        dlogin(req, user)
        Student.objects.create(user=user, ostan=ostan, dore=1, shomare=shomare)
        return redirect('/users/me')
    except:
        return render(req, 'users/createAccountStudent.html', {
            'error': 'duplicate',
        })


def verified(req):
    if (not req.user.is_staff):
        return redirect("/users/login")
    return render(req, "users/verified.html", {
        'data': Student.objects.filter(verified=3),
    })


def createAccountSchool(req):
    if (req.method == 'GET'):
        return render(req, 'users/createAccountSchool.html')
    nam = req.POST['nam']
    famil = req.POST['famil']
    title = req.POST['title']
    ostan = req.POST['ostan']
    goone = req.POST['goone']
    shomare = req.POST['shomare'].translate(translation_table)
    password = req.POST['password']
    email = req.POST['email']
    username = goone + str(Org.objects.all().aggregate(Max('id'))['id__max'])
    user = User.objects.create_user(username, email, password)
    user.first_name = nam
    user.last_name = famil
    user.save()
    dlogin(req, user)
    Org.objects.create(user=user, ostan=ostan, goone=goone, shomare=shomare, title=title)
    return redirect('/users/me')


def me(req):
    if not req.user.is_authenticated:
        return redirect('/users/login')
    if Org.objects.filter(user=req.user).exists():
        return render(req, 'users/meOrg.html', {
            'user': req.user,
            'org': Org.objects.get(user=req.user),
        })
    if Student.objects.filter(user=req.user).exists():
        return render(req, 'users/me.html', {
            'user': req.user,
            'student': Student.objects.get(user=req.user),
        })
    return render(req, 'users/me.html', {
        'user': req.user,
    })


def log(req):
    if not req.user.is_staff:
        return render(req, 'users/login.html')
    return render(req, 'users/log.html', {
        "data": Student.objects.values('ostan').annotate(count=Count('id')),
    })


def shomare(req):
    if not req.user.is_staff:
        return render(req, 'users/login.html')
    return render(req, "users/shomare.html", {
        "users": Student.objects.all(),
    })


def shomareEnglish(req):
    if not req.user.is_staff:
        return render(req, 'users/login.html')
    for stu in Student.objects.all():
        stu.shomare = stu.shomare.translate(translation_table)
        stu.save()
    return redirect("/users/shomare")


def login(req):
    if req.method == 'GET':
        return render(req, 'users/login.html')
    username = req.POST['username']
    password = req.POST['password']
    u = authenticate(req, username=username, password=password)
    if u is not None:
        dlogin(req, u)
        return redirect('/users/me')
    else:
        return render(req, 'users/login.html', {
            'error': 'yes',
        })


def profile(req, student_id):
    self_profile = False
    stu = get_object_or_404(Student, id=student_id)
    if req.user.is_authenticated and req.user.id == stu.user_id:
        self_profile = True
    qs = Quiz.objects.raw('SELECT qid as id, nomre,(SUM(quiz_question.mxgrade)) as maxgrade, '
                          '(quiz_quiz.title || " | " || cast(nomre as text) || "/" || '
                          'cast(SUM(mxgrade) as text) || " امتیاز") as desc FROM '
                          '(SELECT quiz_quiz.id as qid, SUM(grade) as nomre FROM quiz_quiz '
                          'INNER JOIN quiz_question ON quiz_question.quiz_id=quiz_quiz.id '
                          'INNER join quiz_answer on quiz_answer.question_id=quiz_question.id '
                          'and quiz_answer.student_id=' + student_id +
                          ' GROUP by quiz_quiz.id ORDER BY qid) '
                          'INNER JOIN quiz_quiz ON quiz_quiz.id=qid '
                          'INNER JOIN quiz_question ON quiz_question.quiz_id=qid '
                          'WHERE nomre > 0 GROUP by qid')
    acc = Student.objects.raw(
        'SELECT users_ojhandle.handle,* FROM users_student INNER JOIN users_ojhandle ON '
        'users_ojhandle.student_id=users_student.id '
        'AND users_ojhandle.judge="CF" where users_student.id=' + str(student_id))

    groups = StudentGroup.objects.raw('SELECT users_collection.* FROM users_collection INNER JOIN users_studentgroup '
                                      'ON users_collection.students_id=users_studentgroup.id INNER JOIN '
                                      'users_studentgroup_students on users_studentgroup_students.studentgroup_id='
                                      'users_studentgroup.id  and users_studentgroup_students.student_id=' +
                                      str(student_id) + ' group by users_collection.name')
    dore = "دهم"
    if stu.dore == 2:
        dore = "نهم"
    return render(req, 'users/profile.html', {
        'student': stu,
        'dore': dore,
        'groups': groups,
        "self_profile": self_profile,
        'cf_accounts': acc,
        'qs': qs
    })


def my_profile(req):
    if not req.user.is_authenticated:
        return redirect('/users/login')
    if req.user.is_staff:
        return me(req)
    stu = get_object_or_404(Student, user_id=req.user.id)
    return profile(req, stu.id)


def url_ok(url):
    r = requests.head(url)
    return r.status_code == 200


def validate_handle(judge, handle):
    if len(handle) < 3:
        return False
    if judge == 'CF':
        return url_ok("http://codeforces.com/api/user.info?handles=" + handle)
    return True


def accounts(req):
    if not req.user.is_authenticated:
        return redirect('/users/login')
    if req.user.is_staff:
        return redirect('/profile')
    stu = get_object_or_404(Student, user_id=req.user.id)
    handles = {"CF": None, "VJ": None, "ATCODER": None, "GEEKSFORGEEKS": None}
    success = False
    error = False
    error_desc = ""
    if req.method == 'POST':
        for h in handles:
            handles[h] = req.POST[h].lower()
            if not validate_handle(h, handles[h]):
                error = True
                error_desc += "مقدار {} برای {} صحیح نیست<br>".format(handles[h], h)
                continue
            OJHandle.objects.filter(judge=h, student=stu).delete()
            OJHandle.objects.create(judge=h, student=stu, handle=handles[h])
        if not error:
            success = True
    for h in handles:
        handles[h] = OJHandle.objects.filter(judge=h, student=stu).first()
        if handles[h] is None:
            handles[h] = ""
    return render(req, 'users/ojHandles.html', {
        'oj_handles': handles,
        "error": error,
        "success": success,
        "error_desc": error_desc
    })
