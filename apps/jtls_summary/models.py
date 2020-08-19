from django.db import models
from tasks.models import Tasks

class JtlsSummary(models.Model):
    """
    jtl汇总表，将多个jtl汇总生成一个jtl
    """
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="关联的任务id")
    jtl_url = models.CharField("生成的汇总的jtl地址", max_length=100)
    report_created = models.BooleanField("是否已经通过汇总的jtl生成了报告", default=False)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "jtl汇总表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task}:{self.jtl_url}"
