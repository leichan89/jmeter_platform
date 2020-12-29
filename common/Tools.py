# -*- coding: utf-8 -*-
# @Time    : 2020-08-02 15:46
# @Author  : OG·chen
# @File    : Tools.py

import time
from datetime import datetime
import random
import os
import csv
import logging
import hashlib
from collections import Counter

logger = logging.getLogger('collect')

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
    def random_str(slen=20):
        stime = str(time.time()).split('.')[0]
        seed = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
        sa = []
        for i in range(slen):
          sa.append(random.choice(seed))
        return f"{''.join(sa)}{stime}"

    @staticmethod
    def filename(filepath):
        try:
            file = os.path.basename(filepath)
            name = os.path.splitext(file)[0]
            return name
        except:
            return filepath

    # @staticmethod
    # def count_rsp(rsp_path):
    #     # 可能会丢消息
    #     md5list = []
    #     md5dict = {}
    #     filelist = os.listdir(rsp_path)
    #     for file in filelist:
    #         with open(os.path.join(rsp_path, file), 'rb') as f:
    #             data = f.read()
    #         if not data:
    #             data = "[接口未返回响应数据]"
    #         md5 = hashlib.md5(data).hexdigest()
    #         md5dict[md5] = [bytes.decode(data)]
    #         md5list.append(md5)
    #     for key in md5dict.keys():
    #         md5dict[key].append(md5list.count(key))
    #     for value in md5dict.values():
    #         return {value[0]: value[1]}

    @staticmethod
    def count_rsp(rsp_path):
        """
        统计返回的响应数据，计算不同响应出现的次数
        :param rsp_path:
        :return:
        """
        md5list = []
        filelist = os.listdir(rsp_path)
        for file in filelist:
            with open(os.path.join(rsp_path, file), 'rb') as f:
                data = bytes.decode(f.read())
            if not data:
                data = "[接口未返回响应数据]"
            md5list.append(data)
        # 返回的是一个字典
        return Counter(md5list)

    # @staticmethod
    # def summary_jtl(temp_jtl, summary_jtl, stnames):
    #     with open(temp_jtl, 'r') as r:
    #         lines = r.readlines()
    #         if not lines:
    #             return
    #         with open(summary_jtl, 'w') as w:
    #             for line in lines:
    #                 write_tag = True
    #                 if stnames:
    #                     for st in stnames:
    #                         if line.find(st) != -1:
    #                             write_tag = False
    #                             continue
    #                 if write_tag:
    #                     w.write(line)

    @staticmethod
    def read_csv_info(filepath):
        logging.debug(f'读取文件：{filepath}')
        info = []
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                reader = csv.reader(f)
                # 逐行读取csv文件
                for i in reader:
                    info.append(i)
            if info:
                return info
            else:
                raise Exception("文件数据为空")
        else:
            raise FileNotFoundError

    @staticmethod
    def assert_type_dict():
        """
        生成断言代码
        :param assert_str: 断言的字符
        :return:
        """
        assert_dict = {}
        assert_dict['Aef'] = 2
        assert_dict['Bef'] = 1
        assert_dict['Cef'] = 8
        assert_dict['Def'] = 16

        assert_dict['AEf'] = 6
        assert_dict['BEf'] = 5
        assert_dict['CEf'] = 12
        assert_dict['DEf'] = 20

        assert_dict['AEF'] = 38
        assert_dict['BEF'] = 37
        assert_dict['CEF'] = 44
        assert_dict['DEF'] = 52

        assert_dict['AeF'] = 34
        assert_dict['BeF'] = 33
        assert_dict['CeF'] = 40
        assert_dict['DeF'] = 48

        return assert_dict

    @staticmethod
    def boolToStr(param):
        if param == True or param == False:
            return str(param).lower()
        return param

    @staticmethod
    def strToBool(param):
        if param == 'true':
            return True
        elif param == 'false':
            return False
        return param


if __name__ == "__main__":

    # j = '/Users/chenlei/jmeter5/jmx_folder/django.jmx'
    #
    # print(Tools.analysis_jmx(j))

    # p = '/Users/chenlei/jmeter5/jmx_folder/django.jmx'
    # s = Tools.md5sum('/Users/chenlei/mytemp/rsp/xx.text1.unknown')
    # print(s)

    #
    # s = Tools.count_rsp('/Users/chenlei/mytemp/rsp')
    # for i in s:
    #     print(i)

    xpath = '"//SetupThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy[@testname="登陆.9CUb0Q3BP1607434958"]"'
    s =  xpath.split('@testname="')[1].split('"]"')[0]


    # s = Tools.analysis_jmx(p)
    import json
    # print(json.dumps(s))
    # s = p.single_tag_text('//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy[last()]')
    # print(s)
    # accord_tag = '//ThreadGroup[1]/following-sibling::hashTree[1]'
    # s = p.single_tag_text(accord_tag + f'/HTTPSamplerProxy[@testname="我是一个测试sampler"][-1]')
    # print(s)
    # p.add_sampler(name="我是一个测试sampler", url='http://www.baidu.com', method="GET", param_type=1, param={'aa':'vbbb'})
    #
    # p.add_backendListener('aaaaa', 'nnnnn')

    # # # p.add_form_data(xpath, {'aa': 'bb', 'cc': 'dd'})
    # # p.add_backendListener(influxdb_url='cccccccc', application_name='fffffffff', measurement_name='xxx')
    # # # p.change_node_text(xpath, 'aaaa')
    # # # m = p.remove_single_node(xpath)
    # # # p.save_change()
    # # # xx = p.add_sub_node(xpath, new_tag_name='aaaa')
    # # # print(type(xx))
    # # # xx.text = 'aaaa'
    # # # xx.attrib['aa'] = 'nbb'
    # # # p.save_change()
    # # # print(type([]))
    # # # p.add_backendListener('aaaa','bbbbbb')
    # # # p.add_get_param(xpath, aa='bbbbb', bb='bbbbbbb')
    # #
    # # # s = p.add_get_param(xpath, aa='aaaaaaaaaaaaa')
    # # # print(s)
    # # #
    # # # p.remove_single_node(xpath)
    # # # p.single_node_text(xpath)


