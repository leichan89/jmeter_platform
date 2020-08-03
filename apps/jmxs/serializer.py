# -*- coding: utf-8 -*-
# @Time    : 2020-08-01 16:28
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import Jmxs

class JmxsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Jmxs
        fields = "__all__"




