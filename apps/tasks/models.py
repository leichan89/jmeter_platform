from django.db import models
from django.contrib.auth import get_user_model

Users = get_user_model()

class Tasks(models.Model):
    """
    任务表
    """
    task_name = models.CharField("任务名称", max_length=100)
    jmxs_count = models.IntegerField("任务关联的jmx数量", default=0)
    add_user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="用户名")
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "任务表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task_name}"
