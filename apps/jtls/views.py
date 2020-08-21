from rest_framework import generics
from .serializer import JtlsDetailsSerializer
from .models import JtlsDetails
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from common.Tools import Tools
from jmeter_platform import settings


class RecordJtl(generics.CreateAPIView):

    queryset = JtlsDetails.objects.all()
    serializer_class = JtlsDetailsSerializer


class SummaryJtls(APIView):

    def post(self, request, taskid, flowid):
        jtls_stnames = []
        try:
            qs = list(JtlsDetails.objects.select_related('jmx').filter(task_id=taskid, flow_id=flowid))
        except:
            return Response({'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        for q in qs:
            jtl = q.jtl_url
            stname = q.jmx.jmx_setup_thread_name
            jtls_stnames.append([jtl, stname])
        summary_jtl = settings.JTL_URL + Tools.random_str() + '.jtl'
        Tools.summary_jtls(summary_jtl, jtls_stnames)

        return Response({'data': jtls_stnames}, status=status.HTTP_200_OK)
