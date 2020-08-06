from django.urls import path

from . import views

app_name = 'quiz'
urlpatterns = [
  path('<name>/', views.quizView, name='quizView'),
]
