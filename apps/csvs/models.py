from django.db import models
from jmxs.models import Jmxs
from django.contrib.auth import get_user_model

Users = get_user_model()

class Csvs(models.Model):
    """
    csv文件
    """

    csv = models.CharField("csv文件路径", max_length=200)
    jmx = models.ForeignKey(Jmxs, on_delete=models.CASCADE)
    add_user = models.ForeignKey(Users, on_delete=models.CASCADE, verbose_name="用户名")
    add_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "CSV文件"
        verbose_name_plural = verbose_name

    def __str__(self):
        return f"{self.csv}"
