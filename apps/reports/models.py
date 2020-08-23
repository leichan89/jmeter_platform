from django.db import models
from tasks.models import Tasks, TaskFlow
from jtls.models import JtlsSummary

class Reports(models.Model):
    """
    jtl汇总表，将多个jtl汇总生成一个jtl
    报告生成成功后，更新jtls_summary表中report_created字段
    """
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="关联的任务id")
    flow = models.ForeignKey(TaskFlow, on_delete=models.CASCADE, verbose_name="流水id")
    report_url = models.CharField("报告地址", max_length=100)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "报告表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task}:{self.report_url}"
