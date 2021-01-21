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
from common.Operate import ModifyJMX
from celery.utils.log import get_task_logger
from datetime import datetime
import json

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
    from tasks.models import TaskFlow, FlowTaskAggregateReport, RspResult, PngResult
    from jmxs.models import JmxThreadGroup, Jmxs

    try:
        cmds = []
        save_path_dict = {}
        sampler_id_name_dict = {}
        temp_dir = settings.TEMP_URL + task_flow_str
        jtl = settings.JTL_URL + task_flow_str + '.jtl'
        logger.debug(f'创建临时目录{temp_dir}')
        os.makedirs(temp_dir)
        logger.debug('将jmx复制到临时目录下')
        for sjmx in jmxs:
            jmx = sjmx['jmx']
            jmx_id = sjmx['id']
            thread_base_info = Jmxs.objects.get(id=jmx_id).thread_base_info
            num_threads = json.loads(thread_base_info)['num_threads']
            samplers_info = JmxThreadGroup.objects.values('id', 'child_info').filter(jmx_id=jmx_id, child_type="sampler")
            jmx_name = Tools.filename(jmx)
            shutil.copy(jmx, temp_dir)
            # 在这里查找替换变量{{}}
            temp_jmx = temp_dir + os.sep + jmx_name + '.jmx'
            ModifyJMX(temp_jmx).add_backendListener(influxdb_url=settings.INFLUXDB_URL, application_name=task_flow_str)
            for sampler in samplers_info:
                sampler_id = sampler['id']
                sampler_info = json.loads(sampler['child_info'])
                sampler_xpath = sampler_info['xpath']
                # 提取ID和实际名称的对于关系
                sampler_id_name_dict[sampler_xpath.split('@testname="')[1].split('"]')[0]] = sampler_id
                # 创建保存取样器响应的目录
                save_path = temp_dir + os.sep + str(sampler_id)
                os.makedirs(save_path)
                save_path_dict[sampler_id] = save_path
                if str(num_threads) == '1':
                    # 线程是1时，保存错误和异常日志
                    ModifyJMX(temp_jmx).save_rsp_data(sampler_xpath, save_path)
                else:
                    # 线程不为1时，只保存错误日志
                    ModifyJMX(temp_jmx).save_rsp_data(sampler_xpath, save_path, errorsonly=True)
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

        logger.debug('将jtl文件转换为csv文件')
        summary_csv = settings.TEMP_URL + task_flow_str + os.sep + 'temp.csv'
        rt_png = settings.PIC_URL + f"{task_flow_str}_ResponseTimesOverTime.png"
        tps_png = settings.PIC_URL+ f"{task_flow_str}_TransactionsPerSecond.png"
        to_csv_cmd = f'{settings.JMETER_PLUGINS_CMD} --generate-csv {summary_csv} --input-jtl {jtl} --plugin-type AggregateReport'
        to_rt_png = f'{settings.JMETER_PLUGINS_CMD} --generate-png {rt_png} --input-jtl {jtl} --plugin-type ResponseTimesOverTime'
        to_tps_png = f'{settings.JMETER_PLUGINS_CMD} --generate-png {tps_png} --input-jtl {jtl} --plugin-type TransactionsPerSecond'
        os.system(to_csv_cmd)
        os.system(to_rt_png)
        os.system(to_tps_png)

        if os.path.exists(summary_csv):
            logger.info('jtl转为csv成功')
            csv_info = Tools.read_csv_info(summary_csv)
            try:
                for idx, info in enumerate(csv_info):
                    if idx == 0:
                        continue
                    try:
                        sampler_id = sampler_id_name_dict[info[0]]
                    except KeyError:
                        sampler_id = -1
                    try:
                        tps = str(float(info[10]))
                    except:
                        tps = '0/sec'
                    csv_to_db = FlowTaskAggregateReport(task_id=taskid, flow_id=flow_id, sampler_id=sampler_id, label=Tools.filename(info[0]),
                                                        samplers=info[1], average_req=info[2],median_req=info[3],
                                                        line90_req=info[4], line95_req=info[5], line99_req=info[6],
                                                        min_req=info[7], max_req=info[8], error_rate=info[9],
                                                        tps=tps, recieved_per=str(float(info[11])))
                    csv_to_db.save()
                for sampler_id, save_path in save_path_dict.items():
                    count_rsp = Tools.count_rsp(save_path)
                    for key, value in count_rsp.items():
                        rr = RspResult(sampler_id=sampler_id, flow_id=flow_id, response=key, count=value)
                        rr.save()
                png = PngResult(flow_id=flow_id, rt_png_url=os.sep + rt_png, tps_png_url=os.sep + tps_png)
                png.save()
                # 更新流水任务的状态为3，完成状态
                logger.debug('更新流水任务状态为完成状态')
                TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=3, end_time=datetime.now())
                logger.debug('流水任务执行完成')
            except:
                logger.error('保存数据失败')
                raise
        else:
            logger.error('jtl转为csvs失败')
            raise
    except:
        # 更新流水任务的状态为2，运行异常
        TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=2, end_time=datetime.now())
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
    TaskFlow.objects.filter(randomstr=task_flow_str).update(task_status=1, end_time=datetime.now())

    try:
        logger.debug('删除任务流水目录')
        shutil.rmtree(settings.TEMP_URL + task_flow_str)
    except:
        logger.debug('任务流水目录不存在')



if __name__ == "__main__":
    kill_task(1)





