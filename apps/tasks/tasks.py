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
    from tasks.models import TaskFlow, FlowTaskAggregateReport

    flow_id = TaskFlow.objects.values('id').get(randomstr=task_flow_str)['id']
    logger.debug('开始执行jmx文件')
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

    summary_name = Tools.random_str()
    summary_jtl = settings.JTL_URL + summary_name + '.jtl'
    Tools.summary_jtls(summary_jtl, jtls_stnames)
    try:
        js = JtlsSummary(task_id=taskid, flow_id=flow_id, jtl_url=summary_jtl)
        js.save()
        logger.debug('聚合jtl文件成功')
    except Exception as e:
        logger.exception(f'聚合jtl文件失败\n{e}')
        raise Exception

    # 更新流水任务的状态为2，完成状态
    TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=2)
    logger.debug('修改流水任务状态为完成状态成功')

    summary_csv = settings.CSV_URL + summary_name + '.csv'
    cmd = f'{settings.JMETER_PLUGINS_CMD} --generate-csv {summary_csv} --input-jtl {summary_jtl} --plugin-type AggregateReport'
    os.system(cmd)
    if os.path.exists(summary_csv):
        logger.info('jtl转为csv成功')
        csv_info = Tools.read_csv_info(summary_csv)
        for idx, info in enumerate(csv_info):
            if idx == 0:
                continue
            try:
                csv_to_db = FlowTaskAggregateReport(task_id=taskid, flow_id=flow_id, label=info[0], samplers=info[1], average_req=info[2],
                                  median_req=info[3], line90_req=info[4], line95_req=info[5], line99_req=info[6],
                                  min_req=info[7], max_req=info[8], error_rate=info[9],
                                  tps=str(float(info[10])), recieved_per=str(float(info[11])))
                csv_to_db.save()
                logger.info('保存csv到数据库成功')
                os.remove(summary_csv)
            except Exception as e:
                os.remove(summary_csv)
                logger.exception(f'保存csv到数据库失败\n{e}')
                raise Exception
    else:
        logger.error('jtl转为csvs失败')



@shared_task
def kill_task(celery_task_id, task_flow_str):
    """
    先干掉跑jmx的任务，然后再杀掉jmeter进程
    :param celery_task_id:
    :param task_flow_str:
    :return:
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
    django.setup()

    from tasks.models import TaskFlow
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
    logger.info(f'完成查杀流水任务:{celery_task_id}')
    # 更新流水任务的状态为1，已停止
    TaskFlow.objects.filter(celery_task_id=celery_task_id).update(task_status=1)
    logger.info(f'更新流水任务状态为已停止成功:{celery_task_id}')



if __name__ == "__main__":
    kill_task(1)





