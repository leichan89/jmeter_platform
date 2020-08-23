from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from jtls.models import JtlsSummary
from .tasks import generate_report
import logging

logger = logging.getLogger('collect')


class GenerateReport(APIView):

    def post(self, request, taskid, flowid):
        logger.info(f'{taskid}:{flowid}')
        try:
            # values中是数据库中的字段
            jtl_url = JtlsSummary.objects.values('jtl_url').get(task_id=taskid, flow_id=flowid)['jtl_url']
        except Exception as e:
            return Response({'code': 400}, status=status.HTTP_400_BAD_REQUEST)

        generate_report.delay(taskid, flowid, jtl_url)
        return Response({'code': 200}, status=status.HTTP_200_OK)
