# -*- coding: utf-8 -*-
# @Time    : 2020-08-01 17:35
# @Author  : OG·chen
# @File    : urls.py

from jmxs import views
from django.urls import path

urlpatterns = [
    # 上传接口
    path('jmxs/upload', views.JmxUpload.as_view()),
    # 查询所有jmx信息，不包括具体的请求信息
    path('jmxs', views.JmxListView.as_view()),
    # 查询单个jmx信息
    path('jmxs/<int:pk>', views.JmxView.as_view()),
    # 删除接口
    path('jmxs/delete/<int:pk>', views.JmxDestory.as_view())
]









