from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
  path('createAccount/student/', views.createAccountStudent, name='createAccountStudent'),
  path('createAccount/school/', views.createAccountSchool, name='createAccountSchool'),
  path('me/', views.my_profile, name='me'),
  path('handles/', views.accounts, name='accounts'),
  path('login/', views.login, name='login'),
  path('log/', views.log, name='log'),
  path('verified/', views.verified, name='verified'),
  path('shomare/', views.shomare, name='shomare'),
  path('shomare/english/', views.shomareEnglish, name='shomareEnglish'),
  path('agreement/', views.agreementView, name='agree'),
  path('group/<name>', views.studentGroupView, name='studentGroupView'),
]
