# # # # import asyncio
# # # # import time
# # # #
# # # #
# # # # async def shop(what):
# # # #     print(what)
# # # #     time.sleep(5)
# # # #     print("...出来了")
# # # #
# # # # async def main():
# # # #     # awit task1是shop函数返回的
# # # #     task1 = asyncio.create_task(shop('女朋友看衣服.'))
# # # #
# # # #     print(time.ctime(), "开始逛街")
# # # #     # 如果await task1，则需要等待task1执行完之后才会执行下一步的结束动作，awit需要有返回值
# # # #     # s = await task1
# # # #     # print(s)
# # # #     print(time.ctime(), "结束.")
# # # #
# # # #
# # # #
# # # # def myrun(func):
# # # #     asyncio.run(func())
# # # #     print('xxx')
# # # #
# # # #
# # # # def xx(t):
# # # #     time.sleep(t)
# # # #
# # # #
# # # # def aa():
# # # #     xx.delay(t=10)
# # # #     print('aa')
# # # #
# # # #
# # # # aa()
# # # #
# # # # """
# # # # 打印顺序：
# # # # 1、开始逛街
# # # # 2、结束
# # # # 3、打印女朋友看衣服
# # # # 4、等待5s
# # # # 5、打印出来了
# # # # """
# # # #
# # # # # https://docs.python.org/zh-cn/3.7/library/asyncio-task.html
# # #
# # # from jmeter_platform import celery_app
# # #
# # # celery_app.control.revoke('5c57090c-5a09-4da3-a2da-9bb0e2d84648', terminate=True)
# # #
# # # # print(s)
# # # #
# # # # from celery.result import AsyncResult
# # # # res = AsyncResult('0bbb2926-656b-4df8-a8e6-53941ba4793f')
# # # # res.ready()
# # #
# # # import os, sys
# # # #
# # # # BASE_DIR = os.path.dirname(__file__)
# # # #
# # # # sys.path.append(BASE_DIR)
# # # #
# # # # os.chdir(BASE_DIR)
# # # # os.env
# # # #
# # # # sys.path.insert(0, BASE_DIR)
# # # # sys.path.insert(0, os.path.join(BASE_DIR, 'apps'))
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jmeter_platform.settings")
import django
django.setup()
#
# from tasks.models import TaskFlow
# from datetime import datetime
#
# # TaskFlow.objects.filter(id=118).update(add_time=datetime.now())
# # # #
# from tasks.models import TasksDetails
#
#
# j = list(TasksDetails.objects.select_related('task').filter(jmx_id=77))
#
# for i in j:
#     print(i.task.task_type)
# from jmxs.models import JmxThreadGroup
#
# s = JmxThreadGroup.objects.get(jmx_id=76)
# print(s.jmx)
# for i in s:
#     print(i.jmx)


# # #
# # #
# # # # from common.Tools import Tools
# # # #
# # # # for i in range(1,5):
# # # #     print(Tools.random_str())
# # #
# # # # s = '/python-project/jmeter_platform/test.py'
# # #
# # #
# # #
# # # #
# # from tasks.models import Tasks
# # from tasks.serializer import TaskSerializer
# #
# # from jmxs.models import JmxThreadGroupChildren
# #
# # s = JmxThreadGroupChildren.objects.values().filter(jmx_id=23)
# #
# # for i in s:
# #     print(i)
# #
# # # data = {"task_name": 'xxx', 'add_user': 1}
# # # m = TaskSerializer(data=data)
# # # if m.is_valid():
# # #     m.save()
# # #     print(m.data)
# #
# #
# # # m = TasksDetails.objects.values('jmx').filter(task_id=1)
# #
# # # j = Jmxs.objects.values('id').get(id=2)
# # # #
# # # # m = TaskFlow.objects.values('id').get(randomstr='uXSwdxgHZ63dSMAS3V')['id']
# # # #
# # # # print(type(m))
# # #
# # #
# # # # cmd = os.popen('ps -ef|grep xx|grep -v grep')
# # # #
# # # # s = cmd.readlines()
# # # #
# # # # print(s)
# # # #
# # #
# #
#
#
# s = [


# ]
#
#
#
#
#
# m = []
# for i in s:
#     m.append(i)
#     if len(m) == 50:
#         m = [str(i) for i in m]
#         print(','.join(m)+";")
#         m = []
#
#
#
#

# s = {"aa": 1, "bb": 2}
#
# m = s['aa']
#
# del s['aa']
#
# print(m)
# print(s)

#
# m = s['aa']
#
# del s['aa']
#
# print(m)
# print(s)#
# # m = s['aa']
# #
# # del s['aa']
# #
# # print(m)
# # print(s)#
# # m = s['aa']
# #
# # del s['aa']
# #
# # print(m)
# # print(s)#
# # m = s['aa']
# #
# # del s['aa']
# #
# # print(m)
# # print(s)#
# # m = s['aa']
# #
# # del s['aa']
# #
# # print(m)
# # print(s)#
# # m = s['aa']
# #
# # del s['aa']
# #
# # print(m)
# # print(s)
# # print(s)#
# # m = s['aa']
# #
# # del s['aa']
# #
# # print(m)
# # print(s)

# # print(s)

# import random
# import copy
#
#
#
# for i in range(100):
#     s = f"""
# 【试题类型】单项选择题
# 2.甲公司2×14年12月20日上市与乙公司签订商品销售合{random.randint(1000000,20000000)}同，合同约定：甲公司应于2×15年5月20日前将合同标的商品运抵乙公司并经验收，在商品运抵乙公司前灭失、毁损、价值变动等风险由甲公司承担。甲公司该项合同中所售商品为库存w商品，2×14年12月30日，甲公司根据合同向乙公司开具了增值税专ss用发票并于当日确认了商品销售收入。W商品于2×15年5月10日发出并于5月15日运抵乙公司验收合格。对于甲公司2×14年W商品销售收入确认的恰当性判断，除考虑与会计准则规定的收入确认条件的符合性以外，还应考虑可能违背的会计基本假设是（ )。
# A.会计主体
# B.会计分期
# C.持续经营
# D.货币计量
# 【答案】B
# 【解析】在会计分期假设下，企业应当划分会计期间，分期结算账目和编制财务报表。
# 【难度】易
# 【考点】128257
# 【试题类型】单项选择题
# """
#     print(s)

s = {"": ""}

print(s)
