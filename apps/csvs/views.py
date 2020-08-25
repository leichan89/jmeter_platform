from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import CsvSerializer
from jmeter_platform import settings
from common.Tools import Tools
from rest_framework import generics
from .models import Csvs
from rest_framework import status
from common.APIResponse import APIRsp
import os

class CsvUpload(APIView):

    def post(self, request):
        """
        :param request: :param request: {'csv': ,'jmx': , 'user': 1}
        :return:
        """
        data = {}
        csv = request.FILES.get('csv')
        jmx = request.POST.get('jmx')
        user = request.POST.get('user')
        if csv:
            csv_name_ext = os.path.splitext(csv.name)
            csv_name = csv_name_ext[0]
            csv_ext = csv_name_ext[1]
            if csv_ext not in settings.CSV_ALLOWED_FILE_TYPE:
                return APIRsp(code=205, msg='无效的格式，请上传.csv格式的文件', status=status.HTTP_205_RESET_CONTENT)
            csvfile = csv_name + "-" + str(Tools.datetime2timestamp()) + csv_ext
            path = settings.CSV_URL + csvfile

            with open(path, 'wb') as f:
                for i in csv.chunks():
                    f.write(i)

            data['csv'] = csvfile
            # csv不存在时，接口会报错
            data['jmx'] = jmx
            # user不存在时，接口会报错
            data['add_user'] = user

            obj = CsvSerializer(data=data)

            if obj.is_valid():
                obj.save()
                return APIRsp()

            return APIRsp(code=400, msg='添加失败，校验未通过', status=status.HTTP_400_BAD_REQUEST)
        else:
            return APIRsp(code=400, msg='添加失败，未获取到文件或用户id', status=status.HTTP_400_BAD_REQUEST)


class CsvListView(generics.ListAPIView):
    queryset = Csvs.objects.all()
    serializer_class = CsvSerializer

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            return APIRsp(data=rsp_data.data)
        else:
            return APIRsp(code='400', msg='无数据', status=rsp_data.status_code, data=rsp_data.data)
