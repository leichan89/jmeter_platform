# -*- coding: utf-8 -*-
# @Time    : 2020-08-13 14:25
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['username']










