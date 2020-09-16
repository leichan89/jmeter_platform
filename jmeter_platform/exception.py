# -*- coding: utf-8 -*-
# @Time    : 2020-09-08 15:32
# @Author  : OG·chen
# @File    : exception.py


from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler  # drf提供的处理异常方法
from rest_framework import status
from rest_framework_jwt.views import ObtainJSONWebToken
from users.models import UserProfile
import logging

logger = logging.getLogger('collect')

#自定义的异常处理方法，处理没有处理的异常
def exception_handler(exc, context):

    response = drf_exception_handler(exc, context)

    try:
        obj = context['view']
        if isinstance(exc, UserProfile.DoesNotExist) and isinstance(obj, ObtainJSONWebToken):
            # 处理登陆获取token时的异常
            return Response({'code': 400, 'msg': '用户名或密码错误！'}, status=status.HTTP_200_OK)
    except:
        pass

    # drf没有提供处理的服务器异常
    if response is None:
        # 重点：有些异常信息需要记录日志文件
        # logging记录异常信息
        if exc:
            logger.error(f"服务内部错误：{exc}")
        return Response({'code': 500, 'msg': f'服务内部异常！{exc}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    try:
        response.data = {
            'code': response.status_code,
            'msg': response.data['detail']
        }
    except:
        response.data = {
            'code': response.status_code,
            'msg': response.data
        }
    return response









