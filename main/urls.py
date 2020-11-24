from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
  path('', views.index, name='index'),
  path('get_model/', views.get_model, name='get_model'),
  path('add_model/', views.add_model, name='add_model'),
]
