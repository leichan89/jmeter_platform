from .serializer import TaskSerializer, TasksDetailsSerializer
from .models import Tasks
from rest_framework import generics
from rest_framework.views import APIView
from tasks.models import TasksDetails
from jmxs.models import Jmxs

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
        jtls = Jmxs.objects.filter()







