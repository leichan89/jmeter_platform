# -*- coding: utf-8 -*-
# @Time    : 2020-08-17 17:29
# @Author  : OG·chen
# @File    : task.py

import os
import time
import django
import shutil
from common.Tools import Tools
from celery import shared_task
from jmeter_platform import settings
from celery.utils.log import get_task_logger

logger = get_task_logger('celery_task')


@shared_task
def run_task(taskid, task_flow_str, jmxs):
    """
    执行一个任务，并汇总生成的jtl文件，执行任务前会先插入一条任务的flow流水记录
    :param cmds: 一个字段，key是jtl文件路径，value是jmx执行命令
    :return:
    """
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
    django.setup()

    from jtls.models import JtlsSummary
    from tasks.models import TaskFlow, FlowTaskAggregateReport

    try:
        jmx_ids = []
        cmds = []
        temp_dir = settings.TEMP_URL + task_flow_str
        jtl = settings.JTL_URL + task_flow_str + '.jtl'
        logger.debug(f'创建临时目录{temp_dir}')
        os.makedirs(temp_dir)
        logger.debug('将jmx复制到临时目录下')
        for sjmx in jmxs:
            jmx = sjmx['jmx']
            jmx_ids.append(sjmx['id'])
            jmx_name = Tools.filename(jmx)
            shutil.copy(jmx, temp_dir)
            # 在这里查找替换变量{{}}
            temp_jmx = temp_dir + os.sep + jmx_name + '.jmx'
            cmd = f"{settings.JMETER} -n -t {temp_jmx} -l {jtl}"
            cmds.append(cmd)

        logger.debug('开始执行jmx')
        for cmd in cmds:
            os.system(cmd)

        try:
            flow_id = TaskFlow.objects.values('id').get(randomstr=task_flow_str)['id']
            js = JtlsSummary(task_id=taskid, flow_id=flow_id, jtl_url=jtl)
            js.save()
            logger.debug('jtl信息入库成功')
        except:
            logger.error('jtl信息入库失败')
            os.remove(jtl)
            raise

        # 更新流水任务的状态为3，完成状态
        logger.debug('更新流水任务状态为完成状态')
        TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=3)

        logger.debug('将jtl文件转换为csv文件')
        summary_csv = settings.TEMP_URL + task_flow_str + os.sep + 'temp.csv'
        to_csv_cmd = f'{settings.JMETER_PLUGINS_CMD} --generate-csv {summary_csv} --input-jtl {jtl} --plugin-type AggregateReport'
        os.system(to_csv_cmd)

        if os.path.exists(summary_csv):
            logger.info('jtl转为csv成功')
            csv_info = Tools.read_csv_info(summary_csv)
            for idx, info in enumerate(csv_info):
                if idx == 0:
                    continue
                try:
                    csv_to_db = FlowTaskAggregateReport(task_id=taskid, flow_id=flow_id, label=Tools.filename(info[0]),
                                                        samplers=info[1], average_req=info[2],median_req=info[3],
                                                        line90_req=info[4], line95_req=info[5], line99_req=info[6],
                                                        min_req=info[7], max_req=info[8], error_rate=info[9],
                                                        tps=str(float(info[10])), recieved_per=str(float(info[11])))
                    csv_to_db.save()
                except:
                    logger.error('保存聚合报告数据失败')
                    raise
            logger.debug('流水任务执行完成')
        else:
            logger.error('jtl转为csvs失败')
            raise
    except:
        # 更新流水任务的状态为2，运行异常
        TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=2)
        # 这里会自动打印异常信息
        logger.exception(f'执行流水任务失败')
    finally:
        try:
            logger.debug('删除任务流水目录')
            shutil.rmtree(settings.TEMP_URL + task_flow_str)
        except:
            logger.debug('任务流水目录不存在')



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
    # 更新流水任务的状态为1，已停止
    logger.info(f'更新流水任务状态为已停止:{celery_task_id}')
    TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=1)

    try:
        logger.debug('删除任务流水目录')
        shutil.rmtree(settings.TEMP_URL + task_flow_str)
    except:
        logger.debug('任务流水目录不存在')



if __name__ == "__main__":
    kill_task(1)





