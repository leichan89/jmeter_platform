# -*- coding: utf-8 -*-
# @Time    : 2020-08-17 17:29
# @Author  : OG·chen
# @File    : task.py

import time
import os
from celery import shared_task


@shared_task
def run_jmx(cmds):
    """
    1.检查jtl文件是否生成，生成了则退出检查
    2.检查运行jmx的进程是否还存在，不存在了则退出检查
    :param cmds: 一个字段，key是jtl文件路径，value是jmx执行命令
    :return:
    """
    import django
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
    django.setup()

    # from csvs.models import Csvs
    #
    # print(Csvs.objects.all())

    for jtl, cmd in cmds.items():
        os.popen(cmd)
        while True:
            time.sleep(15)
            if os.path.exists(jtl):
                print('yes！！！')
                break
            elif _check_jmx_process(jtl):
                print('yes2！！！')
                break


def _check_jmx_process(process_name):
    """
    查询jmx进程是否存在，存在则返回False，不存在则返回True
    :param process_name: 进程名称
    :return:
    """
    if process_name:
        check = os.popen(f"ps -ef|grep {process_name}|grep -v grep")
        for c in check:
            if c.find(process_name) != -1:
                return True
    return False









