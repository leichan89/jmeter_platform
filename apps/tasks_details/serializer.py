# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 14:04
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import TasksDetails

class TasksDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksDetails
        fields = "__all__"








