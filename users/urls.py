from django.urls import path

from . import views

app_name = 'users'
urlpatterns = [
  path('createAccount/', views.createAccount, name='createAccount'),
  path('me/', views.me, name='me'),
  path('login/', views.login, name='login'),
]
