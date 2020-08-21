import os
from .serializer import TaskSerializer, TasksDetailsSerializer
from .models import Tasks, TaskFlow
from rest_framework import generics
from rest_framework.views import APIView
from tasks.models import TasksDetails
from jmxs.models import Jmxs
from jmeter_platform import settings
from common.Tools import Tools
from .tasks import run_task, kill_task
from rest_framework.response import Response
from rest_framework import status

class CreateTask(generics.CreateAPIView):
    """
    创建任务
    """
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer

class JmxBindTask(generics.CreateAPIView):
    """
    将jmx关联上task
    """
    queryset = TasksDetails.objects.all()
    serializer_class = TasksDetailsSerializer

class RunTask(APIView):

    def post(self, request, taskid):
        try:
            jmxs_id = TasksDetails.objects.values('jmx').filter(task_id=taskid)
            jmxs = Jmxs.objects.values('id', 'jmx').filter(id__in=jmxs_id)
        except:
            return Response({'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        task = []
        cmds = {}
        task_flow_str = Tools.random_str()
        for sj in jmxs:
            jmx = sj['jmx']
            jname = f"{Tools.filename(jmx)}-{task_flow_str}.jtl"
            jtl = f"{settings.JTL_URL + jname}"
            cmd = f"{settings.JMETER} -n -t {jmx} -l {jtl}"
            cmds[jtl] = [sj['id'], cmd]
        task.append(taskid)
        task.append(cmds)
        task.append(task_flow_str)
        celery_task_id = run_task.delay(task)
        flow = TaskFlow(task_id=taskid, celery_task_id=celery_task_id, randomstr=task_flow_str)
        flow.save()

        return Response({'code': 200}, status=status.HTTP_200_OK)


class KillTask(APIView):

    def post(self, request, flowid):
        try:
            task_info = TaskFlow.objects.values('randomstr', 'celery_task_id').get(id=flowid)
            task_flow_str = task_info['randomstr']
            celery_task_id = task_info['celery_task_id']
        except:
            return Response({'code': 400}, status=status.HTTP_400_BAD_REQUEST)
        kill_task.delay(celery_task_id, task_flow_str)
        return Response({'code': 200}, status=status.HTTP_200_OK)





