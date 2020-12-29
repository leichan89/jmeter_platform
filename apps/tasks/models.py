from django.db import models
from django.contrib.auth import get_user_model
from jmxs.models import Jmxs, JmxThreadGroup

Users = get_user_model()

class Tasks(models.Model):
    """
    任务表，查询任务的时候，调用taskdetails查询任务关联的jmx数量
    """
    task_name = models.CharField("任务名称", max_length=200)
    # 任务的类型，0是普通的任务，1是单个jmx的任务
    task_type = models.IntegerField('任务类型', default=0)
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
    randomstr = models.CharField("随机字符串", max_length=50)
    celery_task_id = models.CharField("celery任务的id", max_length=40)
    # 0:进行中，1:已停止，2:执行异常，3:已结束
    task_status = models.IntegerField('任务流水状态', default=0)
    task_flow_url = models.CharField("流水任务的url", max_length=500)
    add_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "任务流水表"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.task_flow_url}"

class FlowTaskAggregateReport(models.Model):
    """
    将csv报告数据存储到数据库
    """
    task = models.ForeignKey(Tasks, on_delete=models.CASCADE, verbose_name="任务id")
    flow = models.ForeignKey(TaskFlow, on_delete=models.CASCADE)
    sampler_id = models.IntegerField("取样器ID", default=-1)
    label = models.CharField("Label", max_length=1000)
    samplers = models.CharField("样本名称", max_length=500)
    average_req = models.CharField("平均值", max_length=100)
    median_req = models.IntegerField("中位数")
    line90_req = models.IntegerField("90%百分位")
    line95_req = models.IntegerField("95%百分位")
    line99_req = models.CharField("99%百分位", max_length=100)
    min_req = models.CharField("最小值", max_length=100)
    max_req = models.CharField("最大值", max_length=100)
    error_rate = models.CharField("异常比例", max_length=100)
    tps = models.CharField("吞吐量", max_length=100)
    recieved_per = models.CharField("每秒从服务器端接收到的数据量", max_length=100)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "jtl转换为csv聚合报告"
        verbose_name_plural = verbose_name
        # ordering = ['-line95_req']

    def __str__(self):
        return f"{self.task}:{self.flow}"

class RspResult(models.Model):
    """
    保存响应结果信息
    """
    sampler = models.ForeignKey(JmxThreadGroup, on_delete=models.CASCADE, verbose_name="取样器ID")
    flow = models.ForeignKey(TaskFlow, on_delete=models.CASCADE)
    response = models.TextField("响应信息")
    count = models.IntegerField("出现次数")

    class Meta:
        verbose_name = "保存响应结果信息"
        verbose_name_plural = verbose_name
