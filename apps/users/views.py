from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from users.serializer import UserSerializer, CreateUserSerializer
from django.db.models import Q
from rest_framework import generics
from users.models import UserProfile
from common.APIResponse import APIRsp

User = get_user_model()

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'code': 200,
        'msg': 'ok',
        'data': {'token': token, 'user': UserSerializer(user).data['id']}
    }

class CustomBackend(ModelBackend):
    """
    重写jwt验证
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 使用公共的exception捕获异常
        user = User.objects.get(Q(username=username))
        if user.check_password(password):
            return user


class CreateUser(generics.CreateAPIView):
    queryset = UserProfile.objects.all()
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        rsp_data = self.create(request, *args, **kwargs)

        if rsp_data.status_code == 201:
            return APIRsp()
        else:
            return APIRsp(code='400', msg='创建用户失败', status=rsp_data.status_code, data=rsp_data.data)




