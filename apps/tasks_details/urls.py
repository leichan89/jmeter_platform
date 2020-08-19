# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 14:08
# @Author  : OG·chen
# @File    : urls.py

from django.urls import path
from .views import JmxBindTask

urlpatterns = [
    path('jmxbindtask', JmxBindTask.as_view()),
]











