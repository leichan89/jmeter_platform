from django.db import models
from tasks.models import Tasks
from jmxs.models import Jmxs

class JtlsDetails(models.Model):
    """
    jtl详情表，开始跑的时候就插入一条数据，jtl_url不传，只传task和jmx
    在生成来jtl之后，更新这个表的jtl_url，通过判断jtl_url是否为空来判断是否生成来jtl
    """
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="关联的任务id")
    jmx = models.ForeignKey(Jmxs, on_delete=models.CASCADE,  verbose_name="jtl对应的jmx信息")
    jtl_url = models.CharField("单个jtl存放地址", default="", max_length=100)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "jtl详情表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task}:{self.jmx}"
