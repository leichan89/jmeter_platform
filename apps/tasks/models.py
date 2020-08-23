from django.db import models
from django.contrib.auth import get_user_model
from jmxs.models import Jmxs

Users = get_user_model()

class Tasks(models.Model):
    """
    任务表，查询任务的时候，调用taskdetails查询任务关联的jmx数量
    """
    task_name = models.CharField("任务名称", max_length=100)
    add_user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, verbose_name="用户名")
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "任务表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task_name}"


class TasksDetails(models.Model):
    """
    任务详情表，任务与jmx的关联表
    """
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE)
    jmx = models.ForeignKey(Jmxs, on_delete=models.CASCADE)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "任务详情表"
        verbose_name_plural = verbose_name
        # 设置联合主键，一个jmx和一个task是一对一关系，同一个taks只能有一个jmx
        unique_together = ['task', 'jmx']

    def __str__(self):
        return f"{self.task}"


class TaskFlow(models.Model):
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="任务流水id")
    randomstr = models.CharField("随机字符串", max_length=30)
    celery_task_id = models.CharField("celery任务的id", max_length=40)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "任务流水表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.randomstr}"
