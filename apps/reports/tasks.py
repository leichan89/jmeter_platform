# -*- coding: utf-8 -*-
# @Time    : 2020-08-17 17:29
# @Author  : OG·chen
# @File    : task.py

import os
import django
from common.Tools import Tools
from celery import shared_task
from jmeter_platform import settings
import shutil
from celery.utils.log import get_task_logger
logger = get_task_logger(__file__)


@shared_task
def generate_report(taskid, flowid, jtl_url):
    """
    执行一个任务，并汇总生成的jtl文件，执行任务前会先插入一条任务的flow流水记录
    :param cmds: 一个字段，key是jtl文件路径，value是jmx执行命令
    :return:
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
    django.setup()

    from reports.models import Reports

    report_output = settings.OUTPUT_URL + Tools.filename(jtl_url)
    # 如果存在，则删除之前的，目录重新生成
    if os.path.exists(report_output):
        shutil.rmtree(report_output)
    cmd = f"{settings.JMETER} -g {jtl_url} -e -o {report_output}"
    logger.info(f'开始生成报告:{cmd}')
    os.system(cmd)
    if os.path.exists(report_output):
        report = Reports(task_id=taskid, flow_id=flowid, report_url=report_output)
        report.save()
        logger.info(f'[{taskid}:{flowid}]报告数据插入数据成功')
    else:
        logger.error(f'[{taskid}:{flowid}]生成报告失败')







