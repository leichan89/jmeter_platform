# -*- coding: utf-8 -*-
# @Time    : 2020-08-02 15:46
# @Author  : OG·chen
# @File    : Tools.py

import time
from datetime import datetime
from lxml import etree
import asyncio
import os
import threading

class Tools:

    @staticmethod
    def datetime2timestamp(dt=datetime.now(), to11=False):
        timetuple = dt.timetuple()
        second = time.mktime(timetuple)
        if to11:
            return int(second)
        microsecond = int(second * 1000 + dt.microsecond / 1000)
        return microsecond


    @staticmethod
    def analysis_jmx(jmxPath):
        """
        解析jmx，获取sampler的信息
        :param jmxPath: jmx文件的绝对路径
        :return: (
            setup线程组名称，
            [
            "name": sampler名称
            "url": sampler的url
            "method": sampler请求方法
            "israw": 判断请求参数是否是raw格式
            "params": [
                "paramname": 参数名称
                "paramvalue": 参数值
                "paramnameXpath": 参数名称xpath
                "paramvalueXpath": 参数值xpath
            ]
        ]
        )
        """
        try:
            tree = etree.parse(jmxPath)
        except:
            return ("", "")

        setup_thread_xpath = '//SetupThreadGroup'
        sapmler_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        # 请求的节点信息
        samplers = tree.xpath(f'{sapmler_root_xpath}')

        # 获取setup线程组的名称
        setup_thread = tree.xpath(setup_thread_xpath)
        if setup_thread:
            setup_thread_name = setup_thread[0].attrib['testname']
        else:
            setup_thread_name = ""

        # 保存所有sampler请求的信息
        sapmlers_info = []

        for sidx, sampler in enumerate(samplers):
            #单个sapmler的配置信息
            sampler_info = {}

            sampler_url_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/stringProp[@name='HTTPSampler.path']"

            sampler_method_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/stringProp[@name='HTTPSampler.method']"

            param_israw_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/boolProp[@name='HTTPSampler.postBodyRaw']"

            # jmx请求参数的节点，get请求的参数可能会有多个elementProp，一个参数一个
            sapmler_param_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/elementProp/collectionProp/elementProp"

            # 取样器名称
            sampler_name = sampler.attrib['testname']
            sampler_info['name'] = sampler_name

            # 取样器url
            sampler_url = tree.xpath(sampler_url_xpath)[0].text
            sampler_info['url'] = sampler_url

            # 取样器方法
            sampler_method = tree.xpath(sampler_method_xpath)[0].text
            sampler_info['method'] = sampler_method

            # 判断是否是raw格式的请求，0表示不是raw，1是raw
            param_israw = tree.xpath(param_israw_xpath)
            sampler_info['israw'] = 0
            if param_israw:
                sampler_info['israw'] = 1

            sampler_info['params'] = []

            sampler_params = tree.xpath(sapmler_param_xpath)
            if sampler_params:
                for pidx, param in enumerate(sampler_params):
                    # param_value_xpath为参数具体的xpath路径，elementProp/stringProp
                    param_value_xpath = f"{sapmler_param_xpath}[{pidx + 1}]/stringProp"
                    param_value = tree.xpath(param_value_xpath)
                    for value in param_value:
                        if value.attrib['name'] == 'Argument.value':
                            if not param_israw:
                                # key,value格式的参数
                                # param.attrib['name']为参数的名称，value.text为参数的值
                                paramname = param.attrib['name']
                                paramname_xpath = f'{param_value_xpath}[@name="Argument.name"]'
                            else:
                                # raw格式的参数，没有Argument.name这个标签
                                paramname = ""
                                paramname_xpath = ""
                            paramvalue = value.text
                            paramvalue_xpath = f'{param_value_xpath}[@name="Argument.value"]'
                            sampler_info['params'].append({"paramname": paramname, "paramvalue": paramvalue,
                                                           "paramnameXpath": paramname_xpath, "paramvalueXpath": paramvalue_xpath})
            sapmlers_info.append(sampler_info)

        return setup_thread_name, sapmlers_info


    def run_jmx(self, cmds):
        # 启动一个线程
        t = threading.Thread(target=self._run, args=(cmds,))
        t.start()
        # t.join()

    def _run(self, cmds):
        for jtl, cmd in cmds.items():
            os.popen(cmd)
            while True:
                time.sleep(15)
                if os.path.exists(jtl):
                    break
                elif self._check_jmx_process(jtl):
                    break


    def _check_jmx_process(self, process_name):
        """
        查询jmx进程是否存在，存在则返回False，不存在则返回True
        :param process_name:
        :return:
        """
        if process_name:
            check = os.popen(f"ps -ef|grep {process_name}|grep -v grep")
            for c in check:
                if c.find(process_name) != -1:
                    return True
        return False





if __name__ == "__main__":

    # print(Tools.datetime2timestamp())
    # t = Tools()
    # s = t.analysis_jmx('/Users/chenlei/jmeter5/jmx_folder/jjxt2.jmx')
    # import json
    # print(s)
    # sss = json.dumps(s[1])
    # a = json.loads(sss)
    # print(a)
    # # for i in s[1]:
    # #     print(json.dumps(i))
    # import os
    # s = os.popen("ps -ef|grep applessdstatistics | grep -v grep")
    # for i in s.readlines():
    #     print(i)
    t = Tools()
    s = t.check_jmx_process('applessdsttistics')
    print(s)

