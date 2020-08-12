from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()



class Jmxs(models.Model):
    """
    jmx文件模型
    """

    jmx_name = models.CharField("jmx文件名称", max_length=100)
    jmx = models.CharField("jmx存放路径", max_length=200)
    jmx_setup_thread_name = models.CharField("setup线程组名称", max_length=200, null=True, blank=True)
    sample_url = models.CharField("线程组单sample请求的url地址", max_length=500, null=True, blank=True)
    sample_method = models.CharField("线程组单sample请求的method", max_length=10, null=True, blank=True)
    sample_params = models.CharField("线程组单sample请求的query参数", max_length=1000, null=True, blank=True)
    sample_raw = models.CharField("线程组单sample请求的raw参数", max_length=5000, null=True, blank=True)
    # add_user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    # add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "jmx文件信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.jmx_name}:{self.jmx}"
