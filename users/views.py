from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login as dlogin
from django.contrib.auth.models import User
import re
from .models import Student

def is_valid_iran_code(input):
    if not re.search(r'^\d{10}$', input):
        return False

    check = int(input[9])
    s = sum([int(input[x]) * (10 - x) for x in range(9)]) % 11
    return (s < 2 and check == s) or (s >= 2 and check + s == 11)

persiandigit='۱۲۳۴۵۶۷۸۹۰١٢٣٤٥٦٧٨٩٠'
englishdigit='12345678901234567890'
translation_table = str.maketrans(persiandigit, englishdigit)

def createAccount(req):
    if (req.method == 'GET'):
        return render(req, 'users/createAccount.html')
    nam = req.POST['nam']
    famil = req.POST['famil']
    kodemelli = req.POST['kodemelli'].translate(translation_table)
    ostan = req.POST['ostan']
    password = req.POST['password']
    email = req.POST['email']
    if not is_valid_iran_code(kodemelli):
        return render(req, 'users/createAccount.html', {
            'error': 'bad',
        })

    try:
        user = User.objects.create_user(kodemelli, email, password)
        user.first_name = nam
        user.last_name = famil
        user.save()
        dlogin(req, user)
        Student.objects.create(user= user, ostan= ostan)
        return redirect('/users/me')
    except:
        return render(req, 'users/createAccount.html', {
            'error': 'duplicate',
        })

def me(req):
    if not req.user.is_authenticated:
        return redirect('/users/login')
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
