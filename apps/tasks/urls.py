# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 13:47
# @Author  : OG·chen
# @File    : urls.py

from tasks import views
from django.urls import path

urlpatterns = [
    path('tasks/create', views.CreateTask.as_view()),
    path('tasks/run/<int:taskid>', views.RunTask.as_view()),
    path('tasks/bindjmxs', views.JmxBindTask.as_view()),
    path('tasks/kill/<int:flowid>', views.KillTask.as_view()),
    path('tasks/queryAggregateReport/<int:flowid>', views.FlowTaskAggregateReportView.as_view()),
    path('tasks/delete/<int:pk>', views.DestoryTask.as_view())
]









