# -*- coding: utf-8 -*-
# @Time    : 2020-08-25 00:19
# @Author  : OG·chen
# @File    : APIResponse.py

from rest_framework.response import Response
from rest_framework import status


class APIRsp(Response):

    def __init__(self, code=200, msg='ok', status=status.HTTP_200_OK, headers=None, exception=None, **kwargs):
        data = {
            'code': code,
            'msg': msg
        }
        if kwargs:
            data.update(kwargs)
        super().__init__(data=data, status=status, headers=headers, exception=exception)




