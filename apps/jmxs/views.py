from common.APIResponse import APIRsp
from common.Operate import ReadJmx
from common.Tools import Tools
from rest_framework.views import APIView
from .models import JmxThreadGroupChildren
from jmeter_platform import settings
from jmxs.serializer import JmxsSerializer, JmxListSerializer, JmxSerializer, JmxsRunSerializer
from .models import Jmxs
from rest_framework import status
from rest_framework import generics
import json
import os
import logging

logger = logging.getLogger(__file__)

class JmxUpload(APIView):
    """
    上传jmx文件，
    上传后，将jmx持久化
    在页面修改参数时，需要修改jmx文件，修改完后，重新获取参数信息，然后重新更新到数据库
    """


    def post(self, request):
        """
        :param request: {'jmx': 'name': , 'user': 1}
        :return:
        """
        data = {}
        jmx = request.FILES.get('jmx')
        jmx_alias = request.POST.get('name')
        user = request.POST.get('user')
        if jmx and user:
            jmx_name_ext = os.path.splitext(jmx.name)
            jmx_name = jmx_name_ext[0]
            jmx_ext = jmx_name_ext[1]
            if jmx_ext not in settings.JMX_ALLOWED_FILE_TYPE:
                return APIRsp(code=205, msg='无效的格式，请上传.jmx格式的文件', status=status.HTTP_205_RESET_CONTENT)
            jmxfile = jmx_name + "-" + str(Tools.datetime2timestamp()) + jmx_ext
            jmxpath = settings.JMX_URL + jmxfile

            with open(jmxpath, 'wb') as f:
                for i in jmx.chunks():
                    f.write(i)

            jmxinfo = ReadJmx(jmxpath).analysis_jmx()
            if not jmxinfo:
                return APIRsp(code=400, msg='添加失败，jmx文件错误', status=status.HTTP_400_BAD_REQUEST)

            samplers_info = jmxinfo[0]
            csvs_info = jmxinfo[1]

            # jmx路径
            data['jmx'] = jmxpath

            # jmx名称
            if jmx_alias:
                data['jmx_alias'] = jmx_alias
            else:
                data['jmx_alias'] = jmx_name

            # user的id不存在时，会校验失败
            data['add_user'] = user

            obj = JmxsSerializer(data=data)

            # 校验数据格式
            if obj.is_valid():
                obj.save()
                jmx_id = obj.data['id']
                for sampler in samplers_info:
                    # 保存sampler信息
                    s = JmxThreadGroupChildren(jmx_id=jmx_id, child_name=sampler['name'],
                                                  child_info=json.dumps(sampler), child_thread=sampler['thread_type'])
                    s.save()
                if csvs_info:
                    for csv in csvs_info:
                        # 保存csv信息
                        c = JmxThreadGroupChildren(jmx_id=jmx_id, child_name=csv['name'], child_type='csv',
                                                   child_info=json.dumps(csv), child_thread=csv['thread_type'])
                        c.save()
                return APIRsp()

            return APIRsp(code=400, msg='添加失败，参数校验未通过', status=status.HTTP_400_BAD_REQUEST)
        else:
            return APIRsp(code=400, msg='添加失败，未传入文件或用户id', status=status.HTTP_400_BAD_REQUEST)

class JmxListView(generics.ListAPIView):
    """
    查询jmx文件
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxListSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            return APIRsp(data=rsp_data.data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)

class JmxView(generics.RetrieveAPIView):
    """
    查询单独某个jmx信息
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxSerializer

    def get(self, request, *args, **kwargs):
        rsp = self.retrieve(request, *args, **kwargs)
        if rsp.status_code == 200:
            if rsp.data:
                id = rsp.data['id']
                children = []
                qs = JmxThreadGroupChildren.objects.values('id', 'child_name', 'child_type', 'child_info').filter(jmx_id=id)
                for q in qs:
                    q['child_info'] = json.loads(q['child_info'])
                    children.append(q)
                rsp.data = {'id': id, 'children': children}
                return APIRsp(data=rsp.data)
            return APIRsp(code='400', msg='无数据', status=rsp.status_code, data=rsp.data)
        else:
            return APIRsp(code='400', msg='无数据', status=rsp.status_code, data=rsp.data)


class JmxDestory(generics.DestroyAPIView):
    """
    删除指定jmx
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxsRunSerializer

    def delete(self, request, *args, **kwargs):
        try:
            self.destroy(request, *args, **kwargs)
            return APIRsp()
        except:
            return APIRsp(code=404, msg='资源未找到', status=status.HTTP_404_NOT_FOUND)


