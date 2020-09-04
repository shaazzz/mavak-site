from django.urls import path, re_path

from . import views

app_name = 'course'
urlpatterns = [
  path('<name>/', views.courseView, name='courseView'),
  path('<name>/<lesson>/', views.lessonView, name='lessonView'),
]
