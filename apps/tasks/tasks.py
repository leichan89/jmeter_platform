# -*- coding: utf-8 -*-
# @Time    : 2020-08-17 17:29
# @Author  : OG·chen
# @File    : task.py

import os
import time
import django
from celery import shared_task


@shared_task
def run_task(task):
    """
    :param cmds: 一个字段，key是jtl文件路径，value是jmx执行命令
    :return:
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
    django.setup()

    from jtls.models import JtlsDetails
    from tasks.models import TaskFlow

    for jtl, cmd in task[1].items():
        code = os.system(cmd)
        if os.path.exists(jtl) and code == 0:
            # 参数是数据库中的字段，不是模型中的字段
            flow_id = TaskFlow.objects.values('id').get(randomstr=task[2])['id']
            jtl = JtlsDetails(task_id=task[0], flow_id=flow_id, jtl_url=jtl)
            jtl.save()

@shared_task
def kill_task(celery_task_id, task_flow_str):
    """
    先干掉跑jmx的任务，然后再杀掉jmeter进程
    :param celery_task_id:
    :param task_flow_str:
    :return:
    """
    from jmeter_platform import celery_app
    from jmeter_platform import settings

    count = 0
    jtl_dir = settings.JTL_URL
    celery_app.control.revoke(celery_task_id, terminate=True)

    while True:
        time.sleep(1)
        pids = os.popen("ps -ef | grep -v grep | grep %s | awk -F ' ' '{print $2}'" % task_flow_str).readlines()
        if len(pids):
            for pid in pids:
                code = os.system(f"kill -9 {pid}")
                if code == 0:
                    print('killed')
        count += 1
        if count == 3:
            jtls = os.listdir(jtl_dir)
            for jtl in jtls:
                if jtl.find(task_flow_str) != -1:
                    os.remove(f'{jtl_dir}{jtl}')
            break



if __name__ == "__main__":
    kill_task(1)





