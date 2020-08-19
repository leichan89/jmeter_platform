from django.db import models
from django.contrib.auth import get_user_model

Users = get_user_model()



class Jmxs(models.Model):
    """
    jmx文件模型
    在生成了jtl后需要更新JtlsDetails表中的jtl_url_created字段
    """

    jmx = models.CharField("jmx存放路径", max_length=200)
    jmx_setup_thread_name = models.CharField("setup线程组名称", default="", max_length=200, null=True, blank=True)
    is_mulit_samplers = models.BooleanField("判断是否是多个sampler的jmx", default=True)
    sampler_name = models.CharField("单sampler的名称", default="", max_length=1000, null=True, blank=True)
    sampler_url = models.CharField("单sample请求的url地址", default="", max_length=1000, null=True, blank=True)
    samplers_info = models.TextField("线程组下sampler请求和参数信息")
    add_user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="用户")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "jmx文件信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.jmx}"
