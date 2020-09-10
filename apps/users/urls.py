# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 13:47
# @Author  : OG·chen
# @File    : urls.py

from users import views
from django.urls import path

urlpatterns = [
    path('users/create', views.CreateUser.as_view()),
    path('menus', views.MenuList.as_view()),
]









