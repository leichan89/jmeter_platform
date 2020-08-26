# # import asyncio
# # import time
# #
# #
# # async def shop(what):
# #     print(what)
# #     time.sleep(5)
# #     print("...出来了")
# #
# # async def main():
# #     # awit task1是shop函数返回的
# #     task1 = asyncio.create_task(shop('女朋友看衣服.'))
# #
# #     print(time.ctime(), "开始逛街")
# #     # 如果await task1，则需要等待task1执行完之后才会执行下一步的结束动作，awit需要有返回值
# #     # s = await task1
# #     # print(s)
# #     print(time.ctime(), "结束.")
# #
# #
# #
# # def myrun(func):
# #     asyncio.run(func())
# #     print('xxx')
# #
# #
# # def xx(t):
# #     time.sleep(t)
# #
# #
# # def aa():
# #     xx.delay(t=10)
# #     print('aa')
# #
# #
# # aa()
# #
# # """
# # 打印顺序：
# # 1、开始逛街
# # 2、结束
# # 3、打印女朋友看衣服
# # 4、等待5s
# # 5、打印出来了
# # """
# #
# # # https://docs.python.org/zh-cn/3.7/library/asyncio-task.html
#
# from jmeter_platform import celery_app
#
# celery_app.control.revoke('5c57090c-5a09-4da3-a2da-9bb0e2d84648', terminate=True)
#
# # print(s)
# #
# # from celery.result import AsyncResult
# # res = AsyncResult('0bbb2926-656b-4df8-a8e6-53941ba4793f')
# # res.ready()
#
# import os, sys
# #
# # BASE_DIR = os.path.dirname(__file__)
# #
# # sys.path.append(BASE_DIR)
# #
# # os.chdir(BASE_DIR)
# # os.env
# #
# # sys.path.insert(0, BASE_DIR)
# # sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
#
# import django
# django.setup()
#
# from jtls.models import JtlsDetails
#
#
# j = list(JtlsDetails.objects.select_related('jmx').filter(task_id=1, flow_id=34))
#
# for i in j:
#     print(i.jmx.add_time)
#
#
# # from common.Tools import Tools
# #
# # for i in range(1,5):
# #     print(Tools.random_str())
#
# # s = '/python-project/jmeter_platform/test.py'
#
#
#
# #
# # from tasks.models import TasksDetails
# # from jmxs.models import Jmxs
# # from tasks.models import Tasks, TaskFlow
# #
# # # m = TasksDetails.objects.values('jmx').filter(task_id=1)
# #
# # # j = Jmxs.objects.values('id').get(id=2)
# #
# # m = TaskFlow.objects.values('id').get(randomstr='uXSwdxgHZ63dSMAS3V')['id']
# #
# # print(type(m))
#
#
# # cmd = os.popen('ps -ef|grep xx|grep -v grep')
# #
# # s = cmd.readlines()
# #
# # print(s)
# #
#
import shutil

shutil.rmtree('/Users/chenlei/python-project/jmeter_platform/performance_files/temp/aaa')
