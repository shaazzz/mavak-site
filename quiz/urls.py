from django.urls import path

from . import views

app_name = 'quiz'
urlpatterns = [
  path('add_cf_friends/', views.addCFFriends, name='quizView'),
  path('<collection>/<name>/', views.quizView, name='quizView'),
  path('<collection>/<name>/virtual', views.virtualQuizView, name='virtualQuizView'),
  path('<collection>/<name>/submit/', views.submitView, name='submitView'),
  path('<collection>/<name>/scoreboard/', views.scoreBoardView, name='scoreBoardView'),
  path('<collection>/<name>/check/<user>/', views.checkView, name='checkView'),
  path('<collection>/<name>/check/<user>/checked/', views.checkedView, name='checkedView'),
  path('<collection>/<name>/autocheck/', views.autoCheckerView, name='autoCheckerView'),
  path('<collection>/<name>/pickjson/', views.pickAnswerFromJson, name='pickAnswerFromJson'),
  path('<collection>/<name>/oj/', views.pickAnswerFromOJView, name='pickAnswerFromOJView'),
]
