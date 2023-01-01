"""xk URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, re_path
from . import views

urlpatterns = [
    re_path(r'^$', views.index),
    path('index/', views.index),
    path('login/', views.login),
    path('logout/', views.logout),
    path('me/', views.me),
    path('classinfo/', views.classinfo),
    path('classinfo/detail/', views.classinfo_detail),
    path('admin/', admin.site.urls),
    path('test/', views.test),
    path('classchoice/', views.classchoice),
    path('classchoice/drop_class/', views.drop_class),
    path('classchoice/add_class/', views.drop_class),
    path('program/',views.program)
]
