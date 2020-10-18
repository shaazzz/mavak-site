"""mavaksite URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles import views
from django.urls import path, include

from quiz import views as quiz_views
from users import views as users_views

urlpatterns = [path('^searchableselect/', include('searchableselect.urls')),
               path('admin/', admin.site.urls),
               path('users/', include('users.urls')),
               path('texts/', include('text.urls')),
               path('courses/', include('course.urls')),
               path('content/', include('content.urls')),
               path('quiz/', include('quiz.urls')),
               path('comments/', include('comment.urls')),
               path('static/', views.serve),
               path('media/', views.serve),
               path('', include('main.urls')),
               path('ranking/<name>/', quiz_views.collectionScoreBoardView, name='collectionScoreBoardView'),
               path('profile/<name>/<user>/', quiz_views.collectionProfileView, name='collectionProfileView'),
               path('profile/', users_views.my_profile, name='my_profile'),
               path('profile/<student_id>', users_views.profile, name='profile'),
               ] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
