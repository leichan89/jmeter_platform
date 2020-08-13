from common.Tools import Tools
from rest_framework.views import APIView
from rest_framework.response import Response
from jmeter_platform import settings
from jmxs.serializer import JmxsSerializer
from .models import Jmxs
from rest_framework import status
from rest_framework import generics
import json

class JmxUpload(APIView):
    """
    上传jmx文件，
    上传后，将jmx持久化
    在页面修改参数时，需要修改jmx文件，修改完后，重新获取参数信息，然后重新更新到数据库
    """


    def post(self, request):
        data = {}
        user = request.POST.get('user')
        jmx = request.FILES.get('jmx')
        if jmx:
            jmx_name = jmx.name.split('.')[0]
            jmx_ext = jmx.name.split('.')[-1]
            if jmx_ext not in settings.ALLOWED_FILE_TYPE:
                return Response({
                    "code": 205,
                    "msg": "无效的格式，请上传.jmx或.csv格式的文件",
                    "data": ""
                }, status=status.HTTP_205_RESET_CONTENT)
            jmxfile = jmx_name + "-" + str(Tools.datetime2timestamp()) + '.' + jmx_ext
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
                "msg": "添加失败，未获取到文件",
                "data": ""
            }, status=status.HTTP_400_BAD_REQUEST)


class JmxListView(generics.ListAPIView):
    """
    查询jmx文件
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxsSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "", "data": rsp_data.data}
        else:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "error", "data": rsp_data.data}
        return rsp_data
