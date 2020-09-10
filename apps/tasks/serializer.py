# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 11:46
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import Tasks, TasksDetails, FlowTaskAggregateReport
from users.serializer import UserSerializer


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tasks
        fields = "__all__"



class TasksDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = TasksDetails
        fields = "__all__"


class FlowTaskAggregateReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlowTaskAggregateReport
        exclude = ['id', 'task', 'flow']


class TasksListSerializer(serializers.ModelSerializer):

    add_user = UserSerializer()

    class Meta:
        model = Tasks
        fields = "__all__"







