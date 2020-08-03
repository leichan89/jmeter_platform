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
