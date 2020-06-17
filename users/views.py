from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as dlogin
from django.contrib.auth.models import User
import re
from .models import Student, Org
from django.db.models import Max

def is_valid_iran_code(input):
    if not re.search(r'^\d{10}$', input):
        return False

    check = int(input[9])
    s = sum([int(input[x]) * (10 - x) for x in range(9)]) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)

persiandigit='۱۲۳۴۵۶۷۸۹۰١٢٣٤٥٦٧٨٩٠'
englishdigit='12345678901234567890'
translation_table = str.maketrans(persiandigit, englishdigit)

def createAccountStudent(req):
    if (req.method == 'GET'):
        return render(req, 'users/createAccountStudent.html')
    nam = req.POST['nam']
    famil = req.POST['famil']
    kodemelli = req.POST['kodemelli'].translate(translation_table)
    ostan = req.POST['ostan']
    dore = req.POST['dore']
    shomare = req.POST['shomare']
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
        Student.objects.create(user= user, ostan= ostan, dore= dore, shomare= shomare)
        return redirect('/users/me')
    except:
        return render(req, 'users/createAccount.html', {
            'error': 'duplicate',
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
    Org.objects.create(user= user, ostan= ostan, goone= goone, shomare= shomare, title= title)
    return redirect('/users/me')
    

def me(req):
    if not req.user.is_authenticated:
        return redirect('/users/login')
    if Org.objects.filter(user= req.user).exists():
        return render(req, 'users/meOrg.html', {
            'user': req.user,
            'org': Org.objects.get(user= req.user),
        })
    return render(req, 'users/me.html', {
        'user': req.user,
    })

def login(req):
    if (req.method == 'GET'):
        return render(req, 'users/login.html')
    username = req.POST['username']
    password = req.POST['password']
    u = authenticate(req, username= username, password= password)
    if u is not None:
        dlogin(req, u)
        return redirect('/users/me')
    else:
        return render(req, 'users/login.html', {
            'error': 'yes',
        })