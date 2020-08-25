from .serializer import TaskSerializer, TasksDetailsSerializer, FlowTaskAggregateReportSerializer
from .models import Tasks, TaskFlow, FlowTaskAggregateReport
from rest_framework import generics
from rest_framework.views import APIView
from tasks.models import TasksDetails
from jmxs.models import Jmxs
from jmeter_platform import settings
from common.Tools import Tools
from .tasks import run_task, kill_task
from rest_framework import status
from common.APIResponse import APIRsp
import logging
logger = logging.getLogger(__file__)

class CreateTask(generics.CreateAPIView):
    """
    创建任务
    """
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return APIRsp()
        except Exception as e:
            logger.exception(f'创建失败\n{e}')
            return APIRsp(code=400, msg='创建失败', status=status.HTTP_400_BAD_REQUEST)

class JmxBindTask(generics.CreateAPIView):
    """
    将jmx关联上task
    """
    queryset = TasksDetails.objects.all()
    serializer_class = TasksDetailsSerializer

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return APIRsp()
        except Exception as e:
            logger.exception(f'绑定失败\n{e}')
            return APIRsp(code=400, msg=str(e), status=status.HTTP_400_BAD_REQUEST)


class RunTask(APIView):
    """
    运行任务，生成一个流水任务
    """
    def post(self, request, taskid):
        try:
            jmxs_id = TasksDetails.objects.values('jmx').filter(task_id=taskid)
            jmxs = Jmxs.objects.values('id', 'jmx').filter(id__in=jmxs_id)
        except Exception as e:
            logger.exception(f'获取任务信息失败\n{e}')
            return APIRsp(code=500, msg='获取任务信息失败', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        task_flow_str = Tools.random_str()
        cmds = {}
        for sj in jmxs:
            jmx = sj['jmx']
            jname = f"{Tools.filename(jmx)}-{task_flow_str}.jtl"
            jtl = f"{settings.JTL_URL + jname}"
            cmd = f"{settings.JMETER} -n -t {jmx} -l {jtl}"
            cmds[jtl] = [sj['id'], cmd]

        logger.info(task_flow_str)
        celery_task_id = run_task.delay(taskid, task_flow_str, cmds)
        flow = TaskFlow(task_id=taskid, celery_task_id=celery_task_id, randomstr=task_flow_str)
        flow.save()
        return APIRsp()


class KillTask(APIView):
    """
    查杀运行中的流水任务
    """
    def post(self, request, flowid):
        try:
            task_info = TaskFlow.objects.values('randomstr', 'celery_task_id').get(id=flowid)
            task_flow_str = task_info['randomstr']
            celery_task_id = task_info['celery_task_id']
        except Exception as e:
            logger.exception(f'查杀进行异常\n{e}')
            return APIRsp(code=500, msg='查杀进行异常', status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        kill_task.delay(celery_task_id, task_flow_str)
        return APIRsp()

class FlowTaskAggregateReportView(APIView):
    """
    查询聚合报告
    """
    def get(self, request, flowid):
        try:
            qs = FlowTaskAggregateReport.objects.all().filter(flow_id=flowid)
            serializer = FlowTaskAggregateReportSerializer(qs, many=True)
            return APIRsp(data=serializer.data)
        except Exception as e:
            logger.exception(f'生成聚合报告异常\n{e}')
            return APIRsp(code=500, msg='生成聚合报告异常', status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DestoryTask(generics.DestroyAPIView):
    """
    删除task，会集联删除
    """

    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

    def delete(self, request, *args, **kwargs):
        try:
            self.destroy(request, *args, **kwargs)
            return APIRsp()
        except:
            return APIRsp(code=404, msg='资源未找到', status=status.HTTP_404_NOT_FOUND)





