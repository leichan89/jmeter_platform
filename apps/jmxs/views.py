from json import JSONDecodeError

from common.Tools import Tools
from rest_framework.views import APIView
from rest_framework.response import Response
from jmeter_platform import settings
from jmxs.serializer import JmxsSerializer, JmxListSerializer, JmxSerializer, JmxsRunSerializer
from .models import Jmxs
from rest_framework import status
from rest_framework import generics
import json
import os
from .tasks import run_jmx

class JmxUpload(APIView):
    """
    上传jmx文件，
    上传后，将jmx持久化
    在页面修改参数时，需要修改jmx文件，修改完后，重新获取参数信息，然后重新更新到数据库
    """


    def post(self, request):
        """
        :param request: {'jmx': , 'user': 1}
        :return:
        """
        data = {}
        user = request.POST.get('user')
        jmx = request.FILES.get('jmx')
        if jmx and user:
            jmx_name_ext = os.path.splitext(jmx.name)
            jmx_name = jmx_name_ext[0]
            jmx_ext = jmx_name_ext[1]
            if jmx_ext not in settings.JMX_ALLOWED_FILE_TYPE:
                return Response({
                    "code": 205,
                    "msg": "无效的格式，请上传.jmx格式的文件",
                    "data": ""
                }, status=status.HTTP_205_RESET_CONTENT)
            jmxfile = jmx_name + "-" + str(Tools.datetime2timestamp()) + jmx_ext
            jmxpath = settings.JMX_URL + jmxfile

            with open(jmxpath, 'wb') as f:
                for i in jmx.chunks():
                    f.write(i)

            jmxinfo = Tools.analysis_jmx(jmxpath)

            samplers_info = jmxinfo[1]
            if samplers_info:
                if len(samplers_info) == 1:
                    data['jmx_setup_thread_name'] = jmxinfo[0]
                    data['sampler_name'] = samplers_info[0]['name']
                    data['sampler_url'] = samplers_info[0]['url']
                    data['is_mulit_samplers'] = False
            else:
                return Response({
                    "code": 400,
                    "msg": "jmx文件未解析出任何信息",
                    "data": ""
                }, status=status.HTTP_400_BAD_REQUEST)


            data['jmx'] = jmxfile
            # 将list转为str
            data['samplers_info'] = json.dumps(samplers_info)
            # user的id不存在时，会校验失败
            data['add_user'] = user

            obj = JmxsSerializer(data=data)

            if obj.is_valid():
                obj.save()
                return Response({
                    "code": 200,
                    "msg": "上传成功",
                    "data": ""
                }, status=status.HTTP_200_OK)

            return Response({
                "code": 400,
                "msg": "添加失败，校验未通过",
                "data": ""
            }, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({
                "code": 400,
                "msg": "添加失败，未获取到文件或用户id",
                "data": ""
            }, status=status.HTTP_400_BAD_REQUEST)

class JmxListView(generics.ListAPIView):
    """
    查询jmx文件
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxListSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "", "data": rsp_data.data}
        else:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "error", "data": rsp_data.data}
        return rsp_data

class JmxView(generics.RetrieveAPIView):
    """
    查询单独某个jmx信息
    """
    # 查询指定列的数据，必须和Serializer中指定的指定相匹配
    queryset = Jmxs.objects.values('id', 'samplers_info')
    serializer_class = JmxSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.retrieve(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            if rsp_data.data:
                id = rsp_data.data['id']
                samplers_info = json.loads(rsp_data.data['samplers_info'])
                rsp_data.data = {'id': id, 'samplers_info': samplers_info}
            rsp_data.data = {"code": rsp_data.status_code, "msg": "", "data": rsp_data.data}
        else:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "error", "data": rsp_data.data}
        return rsp_data

class JmxRun(APIView):
    """
    查询jmx文件的路径
    """
    def post(self, request):
        # 获取到的空的参数也返回空
        ids = request.POST.get('ids')
        if ids:
            try:
                # 传入的是一个list，但是get到的是一个str，需要转换为list
                ids = json.loads(ids)
            except:
                return Response({
                    "code": 400,
                    "msg": "请传入一个list参数",
                    "data": ""
                }, status=status.HTTP_400_BAD_REQUEST)
            jmxs = Jmxs.objects.values('id', 'jmx').filter(pk__in=ids)
            cmds = {}
            for jmx in jmxs:
                jmx = jmx['jmx']
                jname = os.path.splitext(jmx)[0] + '-' + str(Tools.datetime2timestamp()) + '.jtl'
                jtl = f"{settings.JTL_URL + jname}"
                cmd = f"{settings.JMETER} -n -t {settings.JMX_URL + jmx} -l {jtl}"
                cmds[jtl] = cmd
            run_jmx.delay(cmds)
            ser = JmxsRunSerializer(jmxs, many=True)
            data = ser.data
            return Response(data, status=status.HTTP_200_OK)
        else:
            return Response({
                "code": 400,
                "msg": "ids不能为空",
                "data": ""
            }, status=status.HTTP_400_BAD_REQUEST)




