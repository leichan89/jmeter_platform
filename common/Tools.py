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
    def random_str(slen=30):
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


if __name__ == "__main__":

    # j = '/Users/chenlei/jmeter5/jmx_folder/django.jmx'
    #
    # print(Tools.analysis_jmx(j))

    p = '/Users/chenlei/jmeter5/jmx_folder/django.jmx'
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


