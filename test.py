import asyncio
import time


async def shop(what):
    print(what)
    time.sleep(5)
    print("...出来了")

async def main():
    # awit task1是shop函数返回的
    task1 = asyncio.create_task(shop('女朋友看衣服.'))

    print(time.ctime(), "开始逛街")
    # 如果await task1，则需要等待task1执行完之后才会执行下一步的结束动作，awit需要有返回值
    # s = await task1
    # print(s)
    print(time.ctime(), "结束.")



def myrun(func):
    asyncio.run(func())
    print('xxx')


def xx(t):
    time.sleep(t)


def aa():
    xx.delay(t=10)
    print('aa')


aa()

"""
打印顺序：
1、开始逛街
2、结束
3、打印女朋友看衣服
4、等待5s
5、打印出来了
"""

# https://docs.python.org/zh-cn/3.7/library/asyncio-task.html
