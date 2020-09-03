# -*- coding: utf-8 -*-
# @Time    : 2020-08-01 16:28
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import Jmxs
from users.serializer import UserSerializer

class JmxsSerializer(serializers.ModelSerializer):
    """
    post请求的数据
    """
    class Meta:
        model = Jmxs
        fields = "__all__"


class JmxListSerializer(serializers.ModelSerializer):
    """
    jmx列表查询
    """
    add_user = UserSerializer()
    class Meta:
        model = Jmxs
        exclude = ['jmx']


class JmxSerializer(serializers.ModelSerializer):
    """
    单个jmx的数据
    """
    class Meta:
        model = Jmxs
        fields = ['id']


class JmxsRunSerializer(serializers.ModelSerializer):
    """
    单个jmx的数据
    """
    class Meta:
        model = Jmxs
        fields = ['id']
