from django.db import models
from django.contrib.auth import get_user_model

Users = get_user_model()

class Jmxs(models.Model):
    """
    jmx文件模型
    在生成了jtl后需要更新JtlsDetails表中的jtl_url_created字段
    """

    jmx = models.CharField("jmx存放路径", max_length=500)
    jmx_alias = models.CharField('jmx中文别名',max_length=500)
    thread_base_info = models.TextField("线程组基本信息", default="")
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
        ('csv',  'CSV数据文件设置')
    )
    CHILD_THREAD = (
        ('thread', '普通线程组'),
        ('setup', 'setup线程组'),
        ('teardown', 'setup线程组'),
    )
    jmx = models.ForeignKey(Jmxs, on_delete=models.CASCADE)
    child_name = models.CharField("线程组子类的名称", max_length=500)
    child_type = models.CharField("子类的类型", choices=CHILD_TYPE, default="sampler", max_length=10)
    child_info = models.TextField("线程组子类的信息")
    child_thread = models.CharField("所在线程组类型", choices=CHILD_THREAD, default="thread", max_length=10)
    add_time = models.DateTimeField("添加时间", auto_now_add=True)

    class Meta:
        verbose_name = "线程组子元素信息"
        verbose_name_plural = verbose_name

class SamplersChildren(models.Model):
    """
    sampler的子元素，比如信息头，断言，提取响应信息等
    一个sampler不能出现同名的子类
    """
    CHILD_TYPE = (
        ('header', '请求头'),
        ('rsp_assert',  '响应断言'),
        ('json_assert', 'json断言'),
        ('re_extract', '正则提取器'),
        ('json_extract', 'json提取器'),
        ('beanshell_start', 'beanshell前置处理器'),
        ('beanshell_end', 'beanshell后置处理器')
    )
    sampler = models.ForeignKey(JmxThreadGroup, on_delete=models.CASCADE)
    child_name = models.CharField("子元素名称", max_length=500)
    child_type = models.CharField("子元素类型", choices=CHILD_TYPE, default="header", max_length=20)
    child_info = models.TextField("子元素信息", max_length=5000)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "sampler子元素信息"
        verbose_name_plural = verbose_name
        unique_together = ['sampler', 'child_name', 'child_type']

