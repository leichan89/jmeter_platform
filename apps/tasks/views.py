from rest_framework.exceptions import UnsupportedMediaType
from jmeter_platform import settings
from .serializer import TaskSerializer, TasksDetailsSerializer, FlowTaskAggregateReportSerializer,\
    TasksListSerializer, TaskFlowSerializer, TasksBindJmxSerializer, RspResultSerializer
from .models import Tasks, TaskFlow, FlowTaskAggregateReport, TasksDetails, RspResult
from rest_framework import generics
from rest_framework.views import APIView
from jmxs.models import Jmxs
from common.Tools import Tools
from .tasks import run_task, kill_task
from rest_framework import status
from common.APIResponse import APIRsp
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
import logging

logger = logging.getLogger(__file__)

class TasksPagition(PageNumberPagination):
    page_size_query_param = 'size'
    page_query_param = 'num'

class TasksList(generics.ListAPIView):
    queryset = Tasks.objects.all().filter(task_type=0).order_by('-add_time')
    serializer_class = TasksListSerializer
    pagination_class = TasksPagition
    filter_backends = [filters.SearchFilter]

    search_fields = ['task_name']

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            data = rsp_data.data
            del data['next']
            del data['previous']
            return APIRsp(data=data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)

class TaskDetail(APIView):
    """
    任务详细
    """
    queryset = TasksDetails.objects.all()
    serializer_class = TasksDetailsSerializer
    def get(self, request, task_id):
        try:
            qs = TasksDetails.objects.all().filter(task_id=task_id)
            serializer = TasksDetailsSerializer(qs, many=True)
            return APIRsp(data=serializer.data)
        except Exception as e:
            logger.exception(f'获取任务列表异常\n{e}')
            return APIRsp(code=400, msg='获取任务列表异常', status=status.HTTP_400_BAD_REQUEST)

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
    serializer_class = TasksBindJmxSerializer

    def post(self, request, *args, **kwargs):
        try:
            self.create(request, *args, **kwargs)
            return APIRsp()
        except Exception as e:
            logger.exception(f'绑定失败\n{e}')
            return APIRsp(code=400, msg=str(e), status=status.HTTP_400_BAD_REQUEST)

class RunJmx(APIView):
    """
    运行当个jmx
    """
    def post(self, request, userid, jmxid):
        # 判断任务是否存在或者是否绑定了jmx
        task = TasksDetails.objects.filter(jmx_id=jmxid, task__task_type=1)
        if not task:
            try:
                task_name = Jmxs.objects.get(id=jmxid).jmx_alias
            except:
                return APIRsp(code=400, msg='无效的jmxid')
            # 创建任务
            t = Tasks(task_name=task_name, task_type=1, add_user_id=userid)
            t.save()
            taskid = t.id
            # 将jmx加入任务详情
            td = TasksDetails(task_id=taskid, jmx_id=jmxid)
            td.save()
        else:
            taskid = task[0].task_id
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

class RunTask(APIView):
    """
    运行任务，生成一个流水任务，一个任务只能有一个运行中的流水任务
    """
    def post(self, request, taskid):
        # 判断任务是否存在或者是否绑定了jmx
        task = TasksDetails.objects.filter(task_id=taskid)
        if not task:
            return APIRsp(code=400, msg='该任务不存在或未绑定jmx！', status=status.HTTP_200_OK)
        # 判断是否存在运行中的流水任务
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

class TaskDeleteJmx(generics.RetrieveDestroyAPIView):
    """
    删除任务
    """
    queryset = TasksDetails.objects.all()
    serializer_class = TasksBindJmxSerializer

    def delete(self, request, *args, **kwargs):
        rsp = self.destroy(request, *args, **kwargs)
        try:
            if rsp.status_code == 204:
                return APIRsp(code=200, msg='删除成功')
        except Exception as e:
            return APIRsp(code=400, msg=f'删除异常：{str(e)}')
        return rsp

class DeleteTask(generics.DestroyAPIView):
    """
    删除task，会集联删除
    """

    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

    def delete(self, request, *args, **kwargs):
        rsp = self.destroy(request, *args, **kwargs)
        try:
            if rsp.status_code == 204:
                return APIRsp(code=200, msg='删除成功')
        except Exception as e:
            return APIRsp(code=400, msg=f'删除异常：{str(e)}')
        return rsp

class FlowsList(generics.ListAPIView):
    """
    查询任务流水信息
    """
    queryset = TaskFlow.objects.all().order_by('-add_time')
    serializer_class = TaskFlowSerializer
    pagination_class = TasksPagition
    # 不设置search_fields的话，则在所有字段中搜索
    filter_backends = [filters.SearchFilter]
    # 通过外键对应的名字搜索
    search_fields = ['task__task_name']

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            data = rsp_data.data
            del data['next']
            del data['previous']
            return APIRsp(data=data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)

class RspResultList(APIView):
    """
    获取单个sampler的响应信息
    """
    def get(self, request, flow_id, sampler_id):
        try:
            qs = RspResult.objects.all().filter(flow_id=flow_id, sampler_id=sampler_id)
            serializer = RspResultSerializer(qs, many=True)
            return APIRsp(data=serializer.data)
        except Exception as e:
            logger.exception(f'获取任务列表异常\n{e}')
            return APIRsp(code=400, msg='获取任务列表异常', status=status.HTTP_400_BAD_REQUEST)





