from django.urls import path, re_path, register_converter
from datetime import datetime
from . import views

app_name = 'content'


class DateConverter:
    regex = '\d{4}-\d{1,2}-\d{1,2}'

    def to_python(self, value):
        return datetime.strptime(value, '%Y-%m-%d')

    def to_url(self, value):
        return value


register_converter(DateConverter, 'yyyy')

urlpatterns = [
    path('', views.todayCourseView, name='todayCourseView'),
    path('syllabus/', views.syllabusView, name='syllabusView'),
    path('syllabus/<tag>/', views.syllabusWithTagView, name='syllabusWithTagView'),
    path('today/', views.todayCourseView, name='todayCourseView'),
    path('date/<yyyy:date>/', views.courseView, name='courseView'),
    path('date/<yyyy:date>/<lesson>/', views.lessonView, name='lessonView'),
]
