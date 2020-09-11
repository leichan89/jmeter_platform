from django.db import models
from django.contrib.auth import get_user_model

Users = get_user_model()



class Jmxs(models.Model):
    """
    jmx文件模型
    在生成了jtl后需要更新JtlsDetails表中的jtl_url_created字段
    """

    jmx = models.CharField("jmx存放路径", max_length=200)
    jmx_alias = models.CharField('jmx中文别名',max_length=200)
    add_user = models.ForeignKey(Users, on_delete=models.DO_NOTHING, verbose_name="用户")
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "jmx文件信息"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.jmx}"

class JmxThreadGroup(models.Model):
    """
    线程组子类的信息
    """
    CHILD_TYPE = (
        ('sampler', 'http请求'),
        ('csv',  'CSV数据文件设置'),
        ('thread', '普通线程组信息'),
    )
    CHILD_THREAD = (
        ('thread', '普通线程组'),
        ('setup', 'setup线程组'),
        ('teardown', 'setup线程组'),
    )
    jmx = models.ForeignKey(Jmxs, on_delete=models.CASCADE)
    child_name = models.CharField("线程组子类的名称", max_length=100)
    child_type = models.CharField("子类的类型", choices=CHILD_TYPE, default="sampler", max_length=10)
    child_info = models.TextField("线程组子类的信息")
    child_thread = models.CharField("所在线程组类型", choices=CHILD_THREAD, default="thread", max_length=10)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

