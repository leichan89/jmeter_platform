from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model
from users.serializer import UserSerializer, CreateUserSerializer
from django.db.models import Q
from rest_framework import generics
from users.models import UserProfile
from common.APIResponse import APIRsp
from jmeter_platform import settings
from rest_framework.views import APIView

User = get_user_model()

def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'code': 200,
        'msg': 'ok',
        'data': {'token': f"{settings.JWT_AUTH['JWT_AUTH_HEADER_PREFIX']} {token}",
                 'user': UserSerializer(user).data['id']}
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


class MenuList(APIView):

    def get(self, request):
        rsp = {
                "menuList":[
                    {
                        "id":101,
                        "authName":"JMX管理",
                        "path":"jmxs",
                        "children":[
                            {
                                "id":121,
                                "authName":"JMX列表",
                                "path":"jmxs",
                                "children":[

                                ],
                                "order":None
                            }
                        ],
                        "order":1
                    },
                    {
                        "id":103,
                        "authName":"任务管理",
                        "path":"tasks",
                        "children":[
                            {
                                "id":111,
                                "authName":"任务列表",
                                "path":"tasks",
                                "children":[

                                ],
                                "order":None
                            },
                            {
                                "id":112,
                                "authName":"任务流水",
                                "path":"tasks/flows",
                                "children":[

                                ],
                                "order":None
                            }
                        ],
                        "order":2
                    },
                    {
                        "id":145,
                        "authName":"报告管理",
                        "path":"reports",
                        "children":[
                            {
                                "id":146,
                                "authName":"报告列表",
                                "path":"reports",
                                "children":[

                                ],
                                "order":None
                            }
                        ],
                        "order":5
                    },
                    {
                        "id":102,
                        "authName":"参数管理",
                        "path":"params",
                        "children":[
                            {
                                "id":107,
                                "authName":"参数列表",
                                "path":"params",
                                "children":[

                                ],
                                "order":None
                            }
                        ],
                        "order":5
                    }
                ]
            }

        return APIRsp(data=rsp)




