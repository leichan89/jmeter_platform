from django.db import models
from jmxs.models import Jmxs
from django.contrib.auth import get_user_model

Users = get_user_model()

class Csvs(models.Model):
    """
    csv文件模型
    """

    csv_name = models.CharField("csv文件名称", max_length=100)
    csv = models.CharField("csv文件路径", max_length=200)
    jmx = models.ForeignKey(Jmxs, on_delete=models.CASCADE)
    # add_user = models.ForeignKey(Users, on_delete=models.CASCADE)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "CSV文件"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.csv_name}:{self.csv}"





# -*- coding: utf-8 -*-
# @Time    : 2020-08-02 16:01
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import Csvs

class CsvSerializer(serializers.ModelSerializer):

    class Meta:
        model = Csvs
        fields = "__all__"








from csvs import views
from django.urls import path

urlpatterns = [
    path('uploadcsv', views.CsvViews.as_view()),
]




from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import CsvSerializer
from jmeter_platform import settings
from common.Tools import Tools

class CsvViews(APIView):

    def post(self, request):

        data = {
            "csv_name": "1"
        }

        csv = request.FILES.get('csv')
        if csv:
            csv_name = csv.name.split('.')[0]
            csv_ext = csv.name.split('.')[-1]
            if csv_ext not in settings.ALLOWED_FILE_TYPE:
                return Response({
                    "code": 205,
                    "msg": "无效的格式，请上传.jmx或.csv格式的文件",
                    "data": ""
                })
            csvfile = csv_name + "-" + str(Tools.datetime2timestamp()) + '.' + csv_ext
            path = settings.CSV_URL + csvfile

            with open(path, 'wb') as f:
                for i in csv.chunks():
                    f.write(i)

            data['csv'] = csvfile

            obj = CsvSerializer(data=data)

            print(data)

            if obj.is_valid():
                obj.save()
                return Response({
                    "code": 200,
                    "msg": "上传成功",
                    "data": ""
                })

            return Response({
                "code": 201,
                "msg": "添加失败",
                "data": ""
            })

