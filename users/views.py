from django.shortcuts import render, redirect

def createAccount(request):
    if (request.method == 'GET'):
        return render(request, 'users/createAccount.html')
    return redirect('/users/me')

def me(request):
    return render(request, 'users/me.html', {
        'user': request.user,
    })