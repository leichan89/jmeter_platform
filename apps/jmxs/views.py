from common.Tools import Tools
from rest_framework.views import APIView
from rest_framework.response import Response
from jmeter_platform import settings
from jmxs.serializer import JmxsSerializer
from .models import Jmxs
from rest_framework import status
from rest_framework import generics

class JmxUpload(APIView):
    """
    上传jmx文件
    """

    def post(self, request):
        data = {
        'jmx_name': "1",
        'jmx_setup_thread_name': "1",
        'sample_url': "1",
        'sample_method': "1",
        'sample_params': "1",
        'sample_raw': "1"
        }

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
            path = settings.JMX_URL + jmxfile

            with open(path, 'wb') as f:
                for i in jmx.chunks():
                    f.write(i)

            data['jmx'] = jmxfile

            obj = JmxsSerializer(data=data)

            print(data)

            if obj.is_valid():
                obj.save()
                return Response({
                    "code": 200,
                    "msg": "上传成功",
                    "data": ""
                }, status=status.HTTP_200_OK)

            return Response({
                "code": 400,
                "msg": "添加失败",
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
