# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 13:47
# @Author  : OG·chen
# @File    : urls.py

from tasks import views
from django.urls import path

urlpatterns = [
    path('createtask', views.CreateTask.as_view()),
    path('runtask/<int:taskid>', views.RunTask.as_view()),
    path('jmxbindtask', views.JmxBindTask.as_view()),
]









