from django.urls import path

from . import views

app_name = 'main'
urlpatterns = [
  path('', views.index, name='index'),
  path('update_oj/', views.update_oj, name='update_oj'),
  path('get_model/', views.get_model, name='get_model'),
  path('add_model/', views.add_model, name='add_model'),
]
