from rest_framework.exceptions import UnsupportedMediaType
from jmeter_platform import settings
from .serializer import TaskSerializer, TasksDetailsSerializer, FlowTaskAggregateReportSerializer, TasksListSerializer, TaskFlowSerializer
from .models import Tasks, TaskFlow, FlowTaskAggregateReport
from rest_framework import generics
from rest_framework.views import APIView
from tasks.models import TasksDetails
from jmxs.models import Jmxs
from common.Tools import Tools
from .tasks import run_task, kill_task
from rest_framework import status
from common.APIResponse import APIRsp
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__file__)

class TasksPagition(PageNumberPagination):
    page_size_query_param = 'size'
    page_query_param = 'num'

class TasksList(generics.ListAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TasksListSerializer
    pagination_class = TasksPagition

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            return APIRsp(data=rsp_data.data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)


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
        except UnsupportedMediaType as e:
            logger.exception(f'创建失败\n{e}')
            return APIRsp(code=400, msg='不支持的mediaType', status=status.HTTP_400_BAD_REQUEST)
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

        running = TaskFlow.objects.filter(task_id=taskid, task_status=0)
        if running:
            return APIRsp(code=400, msg='存在运行中的流水任务，请稍后重试！', status=status.HTTP_200_OK)
        try:
            jmxs_id = TasksDetails.objects.values('jmx').filter(task_id=taskid)
            rsp = Jmxs.objects.values('id', 'jmx').filter(id__in=jmxs_id)
            jmxs = []
            for jmx in rsp:
                jmxs.append(jmx)
        except Exception as e:
            logger.exception(f'获取任务信息失败\n{e}')
            return APIRsp(code=500, msg='获取任务信息失败', status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        task_flow_str = Tools.random_str()
        celery_task_id = run_task.delay(taskid, task_flow_str, jmxs)
        url = settings.GRAFANA_ENNDPOINT + f'&var-application={task_flow_str}'
        flow = TaskFlow(task_id=taskid, celery_task_id=celery_task_id, randomstr=task_flow_str, task_flow_url=url)
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

class FlowsList(generics.ListAPIView):
    """
    查询任务流水信息
    """
    queryset = TaskFlow.objects.all()
    serializer_class = TaskFlowSerializer
    pagination_class = TasksPagition

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            return APIRsp(data=rsp_data.data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)





