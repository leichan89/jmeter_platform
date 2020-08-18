# -*- coding: utf-8 -*-
# @Time    : 2020-08-17 17:48
# @Author  : OG·chen
# @File    : celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# 指定Django默认配置文件模块
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'jmeter_platform.settings')

# 为我们的项目jmeter_platform创建一个Celery实例。这里不指定broker容易出现错误。
app = Celery('jmeter_platform', broker='redis://127.0.0.1:6379/0')

# 这里指定从django的settings.py里读取celery配置
app.config_from_object('django.conf:settings')

# 自动从所有已注册的django app中加载任务
app.autodiscover_tasks()

# 用于测试的异步任务
@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))











