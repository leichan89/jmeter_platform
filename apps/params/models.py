from django.db import models
from django.contrib.auth import get_user_model

Users = get_user_model()

class UersParams(models.Model):
    """
    用户变量，查询时，环境是必须项，编辑的时候，需要同步更新多个环境
    新增变量时候，可以一次性添加多个环境的
    """
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    env = models.CharField("环境信息", max_length=10)
    param_name = models.CharField("变量名称", max_length=100)
    param_value = models.CharField("变量值", default="", max_length=1000)
    param_content = models.CharField("变量备注", default="", max_length=1000)
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "用户添加的变量"
        verbose_name_plural = verbose_name
        # 创建人、环境和变量名称作为唯一约束，一个用户在一个环境不能创建同名的变量
        unique_together = ['user', 'env', 'param_name']

    def __str__(self):
        return f"{self.env}:{self.param_name}"
