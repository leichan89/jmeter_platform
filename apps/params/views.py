from .models import UsersParams
from .serializer import UserParamsSerializer
from rest_framework import generics, filters
from common.APIResponse import APIRsp
from rest_framework.exceptions import UnsupportedMediaType
from rest_framework import status
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__file__)

class UsersParamsPagition(PageNumberPagination):
    page_size_query_param = 'size'
    page_query_param = 'num'

class UsersParamsList(generics.ListAPIView):
    queryset = UsersParams.objects.all().order_by('-add_time')
    serializer_class = UserParamsSerializer
    pagination_class = UsersParamsPagition
    filter_backends = [filters.SearchFilter]

    search_fields = ['param_name']

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            data = rsp_data.data
            del data['next']
            del data['previous']
            return APIRsp(data=data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)

class UserParamsCreate(generics.CreateAPIView):
    """
    创建参数
    """
    queryset = UsersParams.objects.all()
    serializer_class = UserParamsSerializer

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return APIRsp()
        except UnsupportedMediaType as e:
            logger.exception(f'创建失败\n{e}')
            return APIRsp(code=400, msg='不支持的mediaType', status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.exception(f'创建失败\n{e}')
            return APIRsp(code=400, msg='创建失败', status=status.HTTP_400_BAD_REQUEST)

class UsersParamsDetail(generics.RetrieveAPIView):
    """
    参数详细信息
    """
    queryset = UsersParams.objects.all()
    serializer_class = UserParamsSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.retrieve(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            return APIRsp(data=rsp_data.data)
        else:
            return APIRsp(code='400', msg='无数据', status=rsp_data.status_code, data=rsp_data.data)

class UsersParamsUpdate(generics.RetrieveUpdateAPIView):
    """
    修改参数，其实可以将查询方法也写到一起
    修改请求：http://192.168.62.131:8000/params/update/7
    修改方法：put
    修改参数：所有参数
    """
    queryset = UsersParams.objects.all()
    serializer_class = UserParamsSerializer

    def put(self, request, *args, **kwargs):
        rsp_data = self.update(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            return APIRsp()
        else:
            return APIRsp(code='400', msg='修改数据失败', status=rsp_data.status_code, data=rsp_data.data)

class UsersParamsDelete(generics.DestroyAPIView):
    """
    修改参数
    """
    queryset = UsersParams.objects.all()
    serializer_class = UserParamsSerializer

    def delete(self, request, *args, **kwargs):
        rsp_data = self.destroy(request, *args, **kwargs)
        try:
            if rsp_data.status_code == 204:
                return APIRsp(code=200, msg='删除成功')
        except Exception as e:
            return APIRsp(code=400, msg=f'删除异常：{str(e)}')
        return rsp_data
