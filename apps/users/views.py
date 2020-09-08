from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from users.serializer import UserSerializer
from django.db.models import Q

User = get_user_model()

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'code': 200,
        'msg': 'ok',
        'data': {'token': token, 'user': UserSerializer(user).data['id']}
    }

class CustomBackend(ModelBackend):

    def authenticate(self, request, username=None, password=None, **kwargs):
        # 使用公共的exception捕获异常
        user = User.objects.get(Q(username=username))
        if user.check_password(password):
            return user
