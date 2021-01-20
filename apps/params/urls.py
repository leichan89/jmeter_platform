# -*- coding: utf-8 -*-
# @Time    : 2021/1/20 下午4:02
# @Author  : OG·chen
# @File    : urls.py

from params import views
from django.urls import path

urlpatterns = [
    path('params/create', views.UserParamsCreate.as_view()),
    path('params', views.UsersParamsList.as_view()),
    path('params/details/<int:pk>', views.UsersParamsDetail.as_view()),
    path('params/delete/<int:pk>', views.UsersParamsDelete.as_view()),
    path('params/update/<int:pk>', views.UsersParamsUpdate.as_view()),
]










