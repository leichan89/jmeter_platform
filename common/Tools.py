# -*- coding: utf-8 -*-
# @Time    : 2020-08-02 15:46
# @Author  : OG·chen
# @File    : Tools.py

import time
from datetime import datetime
from xml.dom.minidom import parse
import xml.dom.minidom
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

    def analysis_jmx2(self, jmxPath):

        tree = etree.parse(jmxPath)

        myxpath = "//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy[1]/elementProp/collectionProp/elementProp[1]/stringProp[@name='Argument.value']"

        s = tree.xpath(myxpath)

        for i in s:
            print(i.text)


        # sapmler_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        # 请求的节点信息
        # samplers = tree.xpath(f'{sapmler_root_xpath}')

        # samplers_params = {}
        #
        # for sidx, sampler in enumerate(samplers):
        #     param_israw_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/boolProp[@name='HTTPSampler.postBodyRaw']"
        #
        #     # jmx请求参数的节点，get请求的参数可能会有多个elementProp，一个参数一个
        #     sapmler_param_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/elementProp/collectionProp/elementProp"
        #
        #     # 判断是否是raw格式的请求
        #     param_israw = tree.xpath(param_israw_xpath)
        #     sampler_params = tree.xpath(sapmler_param_xpath)
        #
        #     sampler_name = sampler.attrib['testname']
        #
        #     samplers_params[sampler.attrib['testname']] = []
        #     if sampler_params:
        #         for pidx, param in enumerate(sampler_params):
        #             # param_value_xpath为参数具体的xpath路径，elementProp/stringProp
        #             param_value_xpath = f"{sapmler_param_xpath}[{pidx + 1}]/stringProp"
        #             param_value = tree.xpath(param_value_xpath)
        #             for value in param_value:
        #                 if value.attrib['name'] == 'Argument.value':
        #                     if not param_israw:
        #                         # key,value格式的参数
        #                         # param.attrib['name']为参数的名称
        #                         # value.text为参数的值
        #                         samplers_params[sampler.attrib['testname']].append({param_value_xpath: {param.attrib['name']: value.text}})
        #                     else:
        #                         # raw格式的参数
        #                         samplers_params[sampler.attrib['testname']].append({param_value_xpath: value.text})
        #
        # print(samplers_params)

    def analysis_jmx(self, jmxPath):

        tree = etree.parse(jmxPath)
        sapmler_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        # 请求的节点信息
        samplers = tree.xpath(f'{sapmler_root_xpath}')

        samplers_params = {}

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
                                # param.attrib['name']为参数的名称
                                # value.text为参数的值
                                paramname = param.attrib['name']
                                paramname_xpath = f'{param_value_xpath}[@name="Argument.name"]'
                            else:
                                # raw格式的参数
                                paramname = ""
                                # raw格式没有Argument.name这个标签
                                paramname_xpath = ""
                            paramvalue = value.text
                            paramvalue_xpath = f'{param_value_xpath}[@name="Argument.value"]'
                            sampler_info['params'].append({"paramname": paramname, "paramvalue": paramvalue,
                                                           "paramnameXpath": paramname_xpath, "paramvalueXpath": paramvalue_xpath})
            sapmlers_info.append(sampler_info)

        return sapmlers_info

if __name__ == "__main__":

    # print(Tools.datetime2timestamp())
    t = Tools()
    s = t.analysis_jmx2('/Users/chenlei/jmeter5/jmx_folder/study_api.jmx')
    print(s)



