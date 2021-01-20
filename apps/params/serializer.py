# -*- coding: utf-8 -*-
# @Time    : 2021/1/20 下午4:02
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import UsersParams

class UserParamsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsersParams
        fields = "__all__"










