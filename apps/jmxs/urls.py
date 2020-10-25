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
    path('jmxs/delete/<int:pk>', views.JmxDestory.as_view()),
    path('jmxs/create', views.JmxCreate.as_view()),
    path('jmxs/uploadcsv', views.CsvUpload.as_view()),
    # 查询jmx的所有子元素
    path('jmxs/children/<int:jmx_id>', views.JmxChildrenList.as_view()),
    # 查询jmx文件的单个元素的信息
    path('jmxs/child/<int:pk>', views.JmxChildrenView.as_view()),
    path('samplers/create_update', views.JmxCreateUpdateSapmler.as_view()),
    path('samplers/header/create_update', views.SamplerCreateUpdateHeader.as_view()),
    path('samplers/assert/create_update_rsp', views.SamplerCreateUpdateRSPAssert.as_view()),
    path('samplers/delete/<int:child_id>', views.JmxDeleteChild.as_view()),
    # 查询sampler的所有子类信息
    path('samplers/children/<int:sampler_id>', views.SamplerChildrenList.as_view()),
    # 查询sampler的子元素的详细信息，url参数为子元素的id
    path('samplers/child/<int:pk>', views.SamplerChildrenView.as_view()),
    path('csvs', views.CsvListView.as_view())
]









