from .serializer import TaskSerializer
from .models import Tasks
from rest_framework import generics

class CreateTask(generics.CreateAPIView):
    queryset = Tasks.objects.all()
    serializer_class = TaskSerializer



