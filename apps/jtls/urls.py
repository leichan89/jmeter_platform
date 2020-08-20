# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 14:30
# @Author  : OG·chen
# @File    : urls.py

from django.urls import path
from .views import RecordJtl

urlpatterns = [
    path('recordjtl', RecordJtl.as_view())
]










