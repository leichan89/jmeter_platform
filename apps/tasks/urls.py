# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 13:47
# @Author  : OG·chen
# @File    : urls.py

from tasks import views
from django.urls import path

urlpatterns = [
    path('createtask', views.CreateTask.as_view()),
]









