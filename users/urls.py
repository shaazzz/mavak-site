from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
  path('createAccount/student/', views.createAccountStudent, name='createAccountStudent'),
  path('createAccount/school/', views.createAccountSchool, name='createAccountSchool'),
  path('me/', views.me, name='me'),
  path('login/', views.login, name='login'),
  path('log/', views.log, name='log'),
  path('shomare/', views.shomare, name='shomare'),
]
