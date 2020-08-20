# -*- coding: utf-8 -*-
# @Time    : 2020-08-19 14:29
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import JtlsDetails

class JtlsDetailsSerializer(serializers.ModelSerializer):

    class Meta:
        model = JtlsDetails
        fields = "__all__"









