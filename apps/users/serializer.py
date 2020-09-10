# -*- coding: utf-8 -*-
# @Time    : 2020-08-13 14:25
# @Author  : OG·chen
# @File    : serializer.py

from rest_framework import serializers
from .models import UserProfile

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = UserProfile
        fields = ['name', 'id']


class CreateUserSerializer(serializers.ModelSerializer):

    # #密码加密保存
    def create(self, validated_data):
        user = super(CreateUserSerializer, self).create(validated_data=validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user

    class Meta:
        model = UserProfile
        fields = ['name', 'username', 'password']









