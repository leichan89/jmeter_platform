# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 11:46
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import Tasks

class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tasks
        fields = "__all__"











