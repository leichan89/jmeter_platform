# -*- coding: utf-8 -*-
# @Time    : 2020-08-17 17:29
# @Author  : OG·chen
# @File    : task.py

import os
import time
import django
from common.Tools import Tools
from celery import shared_task
from jmeter_platform import settings
from celery.utils.log import get_task_logger

logger = get_task_logger('cellect')


@shared_task
def run_task(taskid, task_flow_str, cmds):
    """
    执行一个任务，并汇总生成的jtl文件，执行任务前会先插入一条任务的flow流水记录
    :param cmds: 一个字段，key是jtl文件路径，value是jmx执行命令
    :return:
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
    django.setup()

    from jtls.models import JtlsDetails, JtlsSummary
    from tasks.models import TaskFlow

    flow_id = TaskFlow.objects.values('id').get(randomstr=task_flow_str)['id']
    for jtl, jmxcmd in cmds.items():
        code = os.system(jmxcmd[1])
        if os.path.exists(jtl) and code == 0:
            # 参数是数据库中的字段，不是模型中的字段
            jtl = JtlsDetails(task_id=taskid, jmx_id=jmxcmd[0], flow_id=flow_id, jtl_url=jtl)
            jtl.save()

    # 聚合jtl文件
    jtls_stnames = []
    qs = list(JtlsDetails.objects.select_related('jmx').filter(task_id=taskid, flow_id=flow_id))
    for q in qs:
        jtl = q.jtl_url
        stname = q.jmx.jmx_setup_thread_name
        jtls_stnames.append([jtl, stname])
    summary_jtl = settings.JTL_URL + Tools.random_str() + '.jtl'
    Tools.summary_jtls(summary_jtl, jtls_stnames)
    js = JtlsSummary(task_id=taskid, flow_id=flow_id, jtl_url=summary_jtl)
    js.save()

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
                    logger.info(f'{task_flow_str}:进程已被杀死')
        count += 1
        if count == 3:
            jtls = os.listdir(jtl_dir)
            for jtl in jtls:
                if jtl.find(task_flow_str) != -1:
                    os.remove(f'{jtl_dir}{jtl}')
            break



if __name__ == "__main__":
    kill_task(1)





