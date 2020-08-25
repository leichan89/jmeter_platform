from rest_framework.views import APIView
from rest_framework import status
from jtls.models import JtlsSummary
from .tasks import generate_report
from common.APIResponse import APIRsp
import logging

logger = logging.getLogger(__file__)


class GenerateReport(APIView):

    def post(self, request, taskid, flowid):
        try:
            # values中是数据库中的字段
            jtl_url = JtlsSummary.objects.values('jtl_url').get(task_id=taskid, flow_id=flowid)['jtl_url']
        except Exception as e:
            logger.exception(f'生成报告异常\n{e}')
            return APIRsp(code=400, msg='获取流水任务失败', status=status.HTTP_400_BAD_REQUEST)
        generate_report.delay(taskid, flowid, jtl_url)
        return APIRsp()
