from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login as dlogin
from django.contrib.auth.models import User
import re

from quiz.models import Quiz
from .models import Student, Org, StudentGroup
from django.db.models import Max, Count


def agreementView(req):
    if (req.user.is_anonymous):
        return redirect("/users/login")
    stu = get_object_or_404(Student, user=req.user)
    if (stu.verified < 1):
        return render(req, "users/rejected.html")
    if (stu.verified > 1):
        return redirect("/users/me")
    if (req.method == 'GET'):
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
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)


persiandigit = '۱۲۳۴۵۶۷۸۹۰١٢٣٤٥٦٧٨٩٠'
englishdigit = '12345678901234567890'
translation_table = str.maketrans(persiandigit, englishdigit)


def createAccountStudent(req):
    if (req.method == 'GET'):
        return render(req, 'users/createAccountStudent.html')
    nam = req.POST['nam']
    famil = req.POST['famil']
    kodemelli = req.POST['kodemelli'].translate(translation_table)
    ostan = req.POST['ostan']
    dore = req.POST['dore']
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
        Student.objects.create(user=user, ostan=ostan, dore=dore, shomare=shomare)
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
    qs = Quiz.objects.raw('SELECT * FROM (SELECT quiz_quiz.id as id,'
                          ' SUM(mxgrade) as maxgrade, SUM(grade) as nomre,'
                          ' (quiz_quiz.title || " | " || cast(SUM(grade) as text) || "/" ||'
                          ' cast(SUM(mxgrade) as text) || " امتیاز") as desc  FROM quiz_answer'
                          ' INNER JOIN quiz_question ON question_id=quiz_question.id'
                          ' INNER JOIN quiz_quiz ON quiz_question.quiz_id=quiz_quiz.id '
                          ' WHERE student_id=' + str(
        student_id) + ' GROUP BY quiz_quiz.id ORDER BY id) WHERE nomre > 0;')
    acc = Student.objects.raw(
        'SELECT users_ojhandle.handle,* FROM users_student INNER JOIN users_ojhandle ON '
        'users_ojhandle.student_id=users_student.id '
        'AND users_ojhandle.judge="CF" where users_student.id=' + str(student_id))

    groups = StudentGroup.objects.raw('SELECT quiz_collection.* FROM quiz_collection INNER JOIN users_studentgroup '
                                      'ON quiz_collection.students_id=users_studentgroup.id INNER JOIN '
                                      'users_studentgroup_students on users_studentgroup_students.studentgroup_id='
                                      'users_studentgroup.id  and users_studentgroup_students.student_id=' +
                                      str(student_id) + ' group by quiz_collection.name')
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
