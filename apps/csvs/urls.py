# -*- coding: utf-8 -*-
# @Time    : 2020-08-02 16:35
# @Author  : OG·chen
# @File    : urls.py

from csvs import views
from django.urls import path

urlpatterns = [
    path('uploadcsv', views.CsvUpload.as_view()),
    path('listcsvs', views.CsvListView.as_view()),
]
