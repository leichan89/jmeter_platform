# -*- coding: utf-8 -*-
# @Time    : 2020-08-02 15:46
# @Author  : OG·chen
# @File    : Tools.py

import time
from datetime import datetime
from lxml import etree

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

        tree = etree.parse(jmxPath)

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

            # 判断是否是raw格式的请求
            param_israw = tree.xpath(param_israw_xpath)
            sampler_info['israw'] = False
            if param_israw:
                sampler_info['israw'] = True

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


    def analysis_jmx2(self, jmxPath):

        tree = etree.parse(jmxPath)

        myxpath = '//SetupThreadGroup'

        s = tree.xpath(myxpath)

        for i in s:
            print(i.attrib)

if __name__ == "__main__":

    # print(Tools.datetime2timestamp())
    t = Tools()
    s = t.analysis_jmx('/Users/chenlei/jmeter5/jmx_folder/jjxt2.jmx')
    print(s)
    # print(s[3]['params'][0]['paramvalue'])



