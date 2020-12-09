# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 13:47
# @Author  : OG·chen
# @File    : urls.py

from tasks import views
from django.urls import path

urlpatterns = [
    path('tasks', views.TasksList.as_view()),
    path('tasks/create', views.CreateTask.as_view()),
    # 删除创建的任务
    path('tasks/delete/<int:pk>', views.DeleteTask.as_view()),
    path('tasks/run/<int:taskid>', views.RunTask.as_view()),
    path('tasks/runjmx/<int:userid>/<int:jmxid>', views.RunJmx.as_view()),
    path('tasks/bindjmxs', views.JmxBindTask.as_view()),
    path('tasks/kill/<int:flowid>', views.KillTask.as_view()),
    path('tasks/queryAggregateReport/<int:flowid>', views.FlowTaskAggregateReportView.as_view()),
    # 删除任务中的jmx
    path('tasks/deletejmx/<int:pk>', views.TaskDeleteJmx.as_view()),
    path('tasks/flows', views.FlowsList.as_view()),
    # 任务详细
    path('tasks/details/<int:task_id>', views.TaskDetail.as_view())
]









