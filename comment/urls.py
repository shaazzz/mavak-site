from django.urls import path

from . import views

app_name = 'comment'
urlpatterns = [
  path('new/', views.newView, name='courseView'),
]