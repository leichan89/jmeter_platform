from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import CsvSerializer
from jmeter_platform import settings
from common.Tools import Tools
from rest_framework import generics
from .models import Csvs
from rest_framework import status

class CsvUpload(APIView):

    def post(self, request):

        data = {
            "csv_name": "1",
            'add_user': 1,
            "jmx": 1
        }

        csv = request.FILES.get('csv')
        if csv:
            csv_name = csv.name.split('.')[0]
            csv_ext = csv.name.split('.')[-1]
            if csv_ext not in settings.ALLOWED_FILE_TYPE:
                return Response({
                    "code": 205,
                    "msg": "无效的格式，请上传.jmx或.csv格式的文件",
                    "data": ""
                }, status=status.HTTP_205_RESET_CONTENT)
            csvfile = csv_name + "-" + str(Tools.datetime2timestamp()) + '.' + csv_ext
            path = settings.CSV_URL + csvfile

            with open(path, 'wb') as f:
                for i in csv.chunks():
                    f.write(i)

            data['csv'] = csvfile

            obj = CsvSerializer(data=data)

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


class CsvListView(generics.ListAPIView):
    queryset = Csvs.objects.all()
    serializer_class = CsvSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "", "data": rsp_data.data}
        else:
            rsp_data.data = {"code": rsp_data.status_code, "msg": "error", "data": rsp_data.data}
        return rsp_data
