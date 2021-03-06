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
    path('jmxs/delete/<int:jmxId>', views.JmxDelete.as_view()),
    path('jmxs/create', views.JmxCreate.as_view()),
    path('jmxs/copy', views.JmxCopy.as_view()),
    path('jmxs/uploadcsv', views.CsvUpload.as_view()),
    path('jmxs/thread_num/<int:pk>', views.JmxThreadNumView.as_view()),
    # 修改线程组属性
    path('jmxs/update_thread_num', views.JmxThreadNumUpdate.as_view()),
    # 查询jmx的所有子元素
    path('jmxs/children/<int:jmx_id>', views.JmxChildrenList.as_view()),
    # 查询jmx文件的单个元素的信息
    path('jmxs/child/<int:pk>', views.JmxChildrenView.as_view()),
    # 删除jmx的子元素
    path('jmxs/child/delete/<int:childId>', views.JmxDeleteChild.as_view()),
    path('samplers/create_update', views.JmxCreateUpdateSapmler.as_view()),
    path('samplers/header/create_update', views.SamplerCreateUpdateHeader.as_view()),
    path('samplers/assert/create_update_rsp', views.SamplerCreateUpdateRSPAssert.as_view()),
    path('samplers/assert/create_update_json', views.SamplerCreateUpdateJsonAssert.as_view()),
    path('samplers/beanshell/create_update_pre', views.SamplerCreateUpdatePreBeanShell.as_view()),
    path('samplers/beanshell/create_update_after', views.SamplerCreateUpdateAfterBeanShell.as_view()),
    path('samplers/extract/create_update_json', views.SamplerCreateUpdateJsonExtract.as_view()),
    path('samplers/JSR223/create_update_JSR223', views.SamplerCreateUpdateJSR223.as_view()),
    # 查询sampler的所有子类信息
    path('samplers/children/<int:sampler_id>', views.SamplerChildrenList.as_view()),
    # 查询sampler的子元素的详细信息，url参数为子元素的id
    path('samplers/child/<int:pk>', views.SamplerChildrenView.as_view()),
    # 删除sampler的子元素
    path('samplers/delete/<int:samplerId>/<int:childId>', views.SamplerDeleteChild.as_view()),
    path('csvs', views.CsvListView.as_view()),
    # 更新csv信息
    path('csvs/update', views.CsvModify.as_view())
]









