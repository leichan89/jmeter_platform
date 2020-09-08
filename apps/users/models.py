from django.db import models
from django.contrib.auth.models import AbstractUser

class UserProfile(AbstractUser):
    """
    用户信息
    """

    name = models.CharField("姓名", max_length=30, null=True, blank=True)

    class Meta:
        verbose_name = "用户信息"
        verbose_name_plural = verbose_name
        unique_together = ['username', 'id']

    def __str__(self):
        return self.username


