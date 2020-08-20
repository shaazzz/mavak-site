from django.urls import path

from . import views

app_name = 'quiz'
urlpatterns = [
  path('<name>/', views.quizView, name='quizView'),
  path('<name>/submit/', views.submitView, name='submitView'),
  path('<name>/scoreboard/', views.scoreBoardView, name='scoreBoardView'),
  path('<name>/check/<user>/', views.checkView, name='checkView'),
  path('<name>/check/<user>/checked/', views.checkedView, name='checkedView'),
  path('<name>/bulkcheck/', views.bulkCheckView, name='bulkCheckView'),
  path('<name>/oj/', views.pickAnswerFromOJView, name='pickAnswerFromOJView'),
]
