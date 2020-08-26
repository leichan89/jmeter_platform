from django.db import models
from tasks.models import Tasks, TaskFlow
from jmxs.models import Jmxs


class JtlsSummary(models.Model):
    """
    jtl汇总表，将多个jtl汇总生成一个jtl，通过在report表中查询是否存在这个jtl的信息来判断是否已经生成过报告
    """
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="关联的任务id")
    flow = models.ForeignKey(TaskFlow, on_delete=models.CASCADE)
    jtl_url = models.CharField("生成的汇总的jtl地址", max_length=500)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "jtl汇总表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task}:{self.jtl_url}"


