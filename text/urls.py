from django.urls import path

from . import views

app_name = 'text'
urlpatterns = [
  path('<name>', views.renderText, name='renderText'),
]
