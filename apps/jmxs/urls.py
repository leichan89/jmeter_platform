# -*- coding: utf-8 -*-
# @Time    : 2020-08-01 17:35
# @Author  : OG·chen
# @File    : urls.py

from jmxs import views
from django.urls import path

urlpatterns = [
    path('uploadjmx', views.JmxUpload.as_view()),
    path('jmxs', views.JmxListView.as_view()),
    path('jmx/<int:pk>', views.JmxView.as_view())
]









