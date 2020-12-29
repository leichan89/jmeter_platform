# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 11:46
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import Tasks, TasksDetails, FlowTaskAggregateReport, TaskFlow, RspResult
from users.serializer import UserSerializer
from jmxs.serializer import JmxNameSerializer


class TaskSerializer(serializers.ModelSerializer):
    """
    获取任务全部信息
    """
    class Meta:
        model = Tasks
        fields = "__all__"

class TaskNameSerializer(serializers.ModelSerializer):
    """
    只获取任务的id和名称
    """
    class Meta:
        model = Tasks
        fields = ['id', 'task_name']

class TasksBindJmxSerializer(serializers.ModelSerializer):
    """
    绑定jmx到任务
    """
    class Meta:
        model = TasksDetails
        fields = "__all__"

class TasksDetailsSerializer(serializers.ModelSerializer):
    """
    获取任务绑定的jmx信息
    """
    # 将jmx_id替换成jmx的别名
    jmx = JmxNameSerializer()
    class Meta:
        model = TasksDetails
        fields = "__all__"


class FlowTaskAggregateReportSerializer(serializers.ModelSerializer):
    """
    获取流水任务报告信息
    """
    class Meta:
        model = FlowTaskAggregateReport
        exclude = ['id', 'task']

class TaskFlowSerializer(serializers.ModelSerializer):
    """
    获取流水任务信息
    """
    # task是TaskFLow模型中的字段
    task = TaskNameSerializer()
    class Meta:
        model = TaskFlow
        exclude = ['randomstr']


class TasksListSerializer(serializers.ModelSerializer):

    # add_user是Tasks模型中的字段
    add_user = UserSerializer()

    class Meta:
        model = Tasks
        fields = "__all__"

class RspResultSerializer(serializers.ModelSerializer):
    """
    获取响应信息
    """
    class Meta:
        model = RspResult
        fields = ['response', 'count']







