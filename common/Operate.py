# -*- coding: utf-8 -*-
# @Time    : 2020-09-02 17:56
# @Author  : OG·chen
# @File    : operate.py

from lxml import etree
import logging
import json
import time
from common.Tools import Tools

logger = logging.getLogger(__file__)

class ReadJmx():

    def __init__(self, jmxPath):
        self.jmxPath = jmxPath

    def analysis_jmx(self, upload=True):
        """
        解析jmx，获取sampler的信息
        :param jmxPath: jmx文件的绝对路径
        :return: (
            setup线程组名称，
            [
            "xpath": sampler的xpath路径
            "name": sampler名称
            "url": sampler的url
            "method": sampler请求方法
            "param_type": 判断请求参数是否是raw格式
            "params": [
                "paramname": 参数名称
                "paramvalue": 参数值
            ]
        ]
        )
        """
        try:
            add = ModifyJMX(self.jmxPath)
            # 添加setup线程组
            add.add_setup_thread()
            # 添加teardown线程组
            add.add_teardown_thread()
        except:
            logger.warning('为线程组添加setup和teardown线程组失败!')

        try:
            tree = etree.parse(self.jmxPath)
            # xpath路径错误的话，是不会报异常的，返回一个空[]
            ThreadGroup = tree.xpath('//ThreadGroup')
            if not ThreadGroup:
                logger.error('jmx文件没有线程组')
                return None
        except:
            logger.error('解析jmx错误')
            return None

        # thread线程组root节点
        thread_sapmler_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        thread_csv_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/CSVDataSet'

        # setup线程组root节点
        setup_sapmler_root_xpath = '//SetupThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        setup_csv_root_xpath = '//SetupThreadGroup[1]/following-sibling::hashTree[1]/CSVDataSet'

        # teardown线程组root节点
        teardown_sapmler_root_xpath = '//PostThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        teardown_csv_root_xpath = '//PostThreadGroup[1]/following-sibling::hashTree[1]/CSVDataSet'

        # 获取thread线程组的sampler和csv
        thread_sapmlers_info = self._read_sampler(tree, thread_sapmler_root_xpath, upload=upload)
        thread_csvs_info = self._read_csv(tree, thread_csv_root_xpath, upload=upload)

        # 获取setup线程组的sampler和csv
        setup_sapmlers_info = self._read_sampler(tree, setup_sapmler_root_xpath, thread_type='setup', upload=upload)
        setup_csvs_info = self._read_csv(tree, setup_csv_root_xpath, thread_type='setup', upload=upload)

        # 获取teardown线程组的sampler和csv
        teardown_sapmlers_info = self._read_sampler(tree, teardown_sapmler_root_xpath, thread_type='teardown', upload=upload)
        teardown_csvs_info = self._read_csv(tree, teardown_csv_root_xpath, thread_type='teardown', upload=upload)

        # 获取线程组的信息
        thread_info = self._read_thread_info(tree)

        sapmlers_info = thread_sapmlers_info + setup_sapmlers_info + teardown_sapmlers_info
        csvs_info = thread_csvs_info + setup_csvs_info + teardown_csvs_info


        return sapmlers_info, csvs_info, thread_info

    def _read_sampler(self, tree, sapmler_root_xpath, thread_type='thread', upload=True):
        """

        :param tree:
        :param sapmler_root_xpath: sampler的根节点
        :param thread_type: thread表示普通thread, setup表示setup线程组
        :return:
        """
        # 请求的节点信息
        samplers = tree.xpath(sapmler_root_xpath)

        # 保存所有sampler请求的信息
        sapmlers_info = []

        for sidx, sampler in enumerate(samplers):
            #单个sapmler的配置信息
            sampler_info = {}

            # sapmler所属线程组的类型
            sampler_info['thread_type'] = thread_type

            sampler_xpath = f'{sapmler_root_xpath}[{sidx + 1}]'

            sampler_url_xpath = f"{sampler_xpath}/stringProp[@name='HTTPSampler.path']"

            sampler_method_xpath = f"{sampler_xpath}/stringProp[@name='HTTPSampler.method']"

            param_type_xpath = f"{sampler_xpath}/boolProp[@name='HTTPSampler.postBodyRaw']"

            # jmx请求参数的节点，get请求的参数可能会有多个elementProp，一个参数一个
            sapmler_param_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/elementProp/collectionProp/elementProp"

            # 取样器名称
            old_name = sampler.attrib['testname']
            if upload:
                sampler_name = old_name + '.' + Tools.random_str(9)
                sampler.attrib['testname'] = sampler_name
                tree.write(self.jmxPath, encoding='utf-8')
            else:
                sampler_name = old_name
            sampler_info['name'] = old_name

            # 取样器xpath
            sampler_info['xpath'] = f'{sapmler_root_xpath}[@testname="{sampler_name}"]'

            # 取样器url
            sampler_url = tree.xpath(sampler_url_xpath)[0].text
            sampler_info['url'] = sampler_url

            # 取样器方法
            sampler_method = tree.xpath(sampler_method_xpath)[0].text
            sampler_info['method'] = sampler_method

            # 判断是否是raw格式的请求
            raw_param = tree.xpath(param_type_xpath)
            sampler_info['param_type'] = 'form'
            if raw_param:
                sampler_info['param_type'] = 'raw'

            sampler_info['params'] = []

            sampler_params = tree.xpath(sapmler_param_xpath)
            if sampler_params:
                for pidx, param in enumerate(sampler_params):
                    # param_value_xpath为参数具体的xpath路径，elementProp/stringProp
                    param_value_xpath = f"{sapmler_param_xpath}[{pidx + 1}]/stringProp"
                    param_value = tree.xpath(param_value_xpath)
                    for value in param_value:
                        if value.attrib['name'] == 'Argument.value':
                            if sampler_info['param_type'] == 'form':
                                # key,value格式的参数
                                # param.attrib['name']为参数的名称，value.text为参数的值
                                sampler_info['params'].append({"key": param.attrib['name'], "value": value.text})
                            else:
                                # raw格式的参数，没有Argument.name这个标签
                                sampler_info['params'] = value.text
            if sampler_info['param_type'] == 'form' and not sampler_info['params']:
                sampler_info['params'] = [{"key": "", "value": ""}]
            elif sampler_info['param_type'] == 'raw' and not sampler_info['params']:
                sampler_info['params'] = ''
            sapmlers_info.append(sampler_info)
            # 获取sampler的子元素信息
            sampler_info['children'] = self._read_sampler_children_info(tree, sampler_xpath, upload=upload)

        return sapmlers_info

    def _read_csv(self, tree, csv_root_xpath, thread_type='thread', upload=True):
        """

        :param tree:
        :param csv_root_xpath: csv的根节点
        :param thread_type: thread表示普通thread, setup表示setup线程组
        :return:
        """

        # csv的节点信息
        csvs = tree.xpath(csv_root_xpath)

        # csv信息集合
        csvs_info = []
        if csvs:
            for cinx, csv in enumerate(csvs):
                csv_info = {}

                # csv所属线程组的类型
                csv_info['thread_type'] = thread_type

                csv_xpath = f"{csv_root_xpath}[{cinx + 1}]"

                old_name = csv.attrib['testname']
                if upload:
                    csv_name = old_name + '.' + Tools.random_str(9)
                    csv.attrib['testname'] = csv_name
                    tree.write(self.jmxPath, encoding='utf-8')
                else:
                    csv_name = old_name
                csv_info['name'] = old_name
                csv_info['xpath'] = f'{csv_root_xpath}/[@testname="{csv_name}"]'
                filename_xpath = csv_xpath + '/stringProp[@name="filename"][1]'
                filename = tree.xpath(filename_xpath)[0].text
                csv_info['filename'] = filename

                ignoreFirstLine_xpath = csv_xpath + '/boolProp[@name="ignoreFirstLine"]'
                ignoreFirstLine = tree.xpath(ignoreFirstLine_xpath)[0].text
                csv_info['ignoreFirstLine'] = ignoreFirstLine

                recycle_xpath = csv_xpath + '/boolProp[@name="recycle"]'
                recycle = tree.xpath(recycle_xpath)[0].text
                csv_info['recycle'] = recycle

                stopThread_xpath = csv_xpath + '/boolProp[@name="stopThread"]'
                stopThread = tree.xpath(stopThread_xpath)[0].text
                csv_info['stopThread'] = stopThread

                variableNames_xpath = csv_xpath + '/stringProp[@name="variableNames"]'
                variableNames = tree.xpath(variableNames_xpath)[0].text
                csv_info['variableNames'] = variableNames

                csvs_info.append(csv_info)

        return csvs_info

    def _read_thread_info(self, tree):
        """
        获取第一个线程组的信息
        :param tree:
        :return:
        """

        thread_info = {}

        # thread_info['thread_type'] = thread_type

        thread_xpath = '//ThreadGroup[1]'

        # 线程数
        num_threads_xpath = thread_xpath + "/stringProp[@name='ThreadGroup.num_threads']"
        num_threads = tree.xpath(num_threads_xpath)[0].text
        thread_info['num_threads'] = num_threads

        # Ramp-UP时间
        ramp_time_xpath = thread_xpath + "/stringProp[@name='ThreadGroup.ramp_time']"
        ramp_time = tree.xpath(ramp_time_xpath)[0].text
        thread_info['ramp_time'] = ramp_time

        # 循环次数，-1表示永远
        loops_xpath = thread_xpath + "/elementProp/stringProp[@name='LoopController.loops']"
        loops = tree.xpath(loops_xpath)[0].text
        thread_info['loops'] = loops

        # 调度器配置，true or false
        scheduler_xpath = thread_xpath + "/boolProp[@name='ThreadGroup.scheduler']"
        scheduler = tree.xpath(scheduler_xpath)[0].text
        thread_info['scheduler'] = scheduler

        # 持续时间
        duration_xpath = thread_xpath + "/stringProp[@name='ThreadGroup.duration']"
        duration = tree.xpath(duration_xpath)[0].text
        if duration:
            thread_info['duration'] = duration
        else:
            thread_info['duration'] = ""

        return thread_info

    def _read_sampler_children_info(self, tree, sampler_xapth, upload=True):
        """
        读取sampler的子元素信息
        :param tree:
        :param sampler_xapth:
        :return:
        """

        # 所有子元素信息
        children = []

        # sampler子元素的hashTree
        hashTreeXpath = sampler_xapth + "/following-sibling::hashTree[1]"

        # 计数头信息
        header_count = 1

        # 响应断言计数器
        rsp_assert_count = 1

        # JSON断言计数器
        json_assert_count = 1

        # JSON提取器计数器
        json_extract_count = 1

        # 前置处理器计数器
        pre_beanshell_count = 1

        # 后置处理器计数器
        after_beanshell_count = 1

        hashTree = tree.xpath(sampler_xapth)[0].getnext()

        if hashTree is not None:
            for cd in hashTree:
                child = {}
                # 获取头信息
                if cd.tag == "HeaderManager":
                    child['child_type'] = 'header'
                    old_header_name = cd.attrib['testname']
                    if upload:
                        new_header_name = old_header_name + "." + Tools.random_str(9)
                        cd.attrib['testname'] = new_header_name
                        tree.write(self.jmxPath, encoding='utf-8')
                    else:
                        new_header_name = old_header_name
                    child['child_name'] = old_header_name
                    child['xpath'] = f'//HeaderManager[@testname="{new_header_name}"]'
                    header_temp_xpath = hashTreeXpath + f'/HeaderManager[{header_count}]/collectionProp/elementProp'
                    header_param_info = tree.xpath(header_temp_xpath)
                    params_list = []
                    for pidx, param in enumerate(header_param_info):
                        param_name_xpath = f"{header_temp_xpath}[{pidx + 1}]/stringProp[@name='Header.name']"
                        param_value_xpath = f"{header_temp_xpath}[{pidx + 1}]/stringProp[@name='Header.value']"
                        param_name = tree.xpath(param_name_xpath)[0].text
                        param_value = tree.xpath(param_value_xpath)[0].text
                        header_param = {"key": param_name, "value": param_value}
                        params_list.append(header_param)
                    if not params_list:
                        params_list = [{"key": "", "value": ""}]
                    child['params'] = params_list
                    header_count += 1
                if cd.tag == "ResponseAssertion":
                    child['child_type'] = 'rsp_assert'
                    old_rsp_assert_name = cd.attrib['testname']
                    if upload:
                        new_rsp_assert_name = old_rsp_assert_name + "." + Tools.random_str(9)
                        cd.attrib['testname'] = new_rsp_assert_name
                        tree.write(self.jmxPath, encoding='utf-8')
                    else:
                        new_rsp_assert_name = old_rsp_assert_name
                    child['child_name'] = old_rsp_assert_name
                    rsp_assert_xpath = f'/ResponseAssertion[@testname="{new_rsp_assert_name}"]'
                    child['xpath'] = rsp_assert_xpath
                    # 断言内容
                    rsp_assert_content_xpath = hashTreeXpath + f'/ResponseAssertion[{rsp_assert_count}]/collectionProp/stringProp'
                    # 断言方式
                    rsp_assert_type_xpath = hashTreeXpath + f'/ResponseAssertion[{rsp_assert_count}]/intProp'
                    rsp_assert_content = tree.xpath(rsp_assert_content_xpath)
                    rsp_assert_content_list = []
                    for rac in rsp_assert_content:
                        rsp_assert_content_list.append({'key': rac.text})
                    rsp_assert_type = tree.xpath(rsp_assert_type_xpath)[0].text
                    assert_type_dict = Tools.assert_type_dict()
                    for key, value in assert_type_dict.items():
                        if str(value) == rsp_assert_type:
                            child['params'] = {"rsp_assert_content": rsp_assert_content_list, "rsp_assert_type": list(key)}
                    rsp_assert_count += 1
                if cd.tag == "JSONPathAssertion":
                    child['child_type'] = 'json_assert'
                    old_json_assert_name = cd.attrib['testname']
                    if upload:
                        new_json_assert_name = old_json_assert_name + "." + Tools.random_str(9)
                        cd.attrib['testname'] = new_json_assert_name
                        tree.write(self.jmxPath, encoding='utf-8')
                    else:
                        new_json_assert_name = old_json_assert_name
                    child['child_name'] = old_json_assert_name
                    json_assert_xpath = f'/JSONPathAssertion[@testname="{new_json_assert_name}"]'
                    child['xpath'] = json_assert_xpath
                    json_assert_base_xpath = hashTreeXpath + f'/JSONPathAssertion[{json_assert_count}]'
                    json_assert_json_path_xpath = json_assert_base_xpath + '/stringProp[@name="JSON_PATH"]'
                    json_assert_expected_value_xpath = json_assert_base_xpath + '/stringProp[@name="EXPECTED_VALUE"]'
                    json_assert_expect_null_xpath = json_assert_base_xpath + '/boolProp[@name="EXPECT_NULL"]'
                    json_assert_is_regex_xpath = json_assert_base_xpath + '/boolProp[@name="ISREGEX"]'
                    expect_null = tree.xpath(json_assert_expect_null_xpath)[0].text
                    if expect_null == 'true':
                        expect_null = True
                    elif expect_null == 'false':
                        expect_null = False
                    invert = tree.xpath(json_assert_is_regex_xpath)[0].text
                    if invert == 'true':
                        invert = True
                    elif invert == 'false':
                        invert = False
                    child['params'] = {"json_path": tree.xpath(json_assert_json_path_xpath)[0].text,
                                       "expected_value": tree.xpath(json_assert_expected_value_xpath)[0].text,
                                       "expect_null": expect_null,
                                       "invert": invert}
                    json_assert_count += 1
                if cd.tag == "JSONPostProcessor":
                    child['child_type'] = 'json_extract'
                    old_json_extract_name = cd.attrib['testname']
                    if upload:
                        new_json_extract_name = old_json_extract_name + "." + Tools.random_str(9)
                        cd.attrib['testname'] = new_json_extract_name
                        tree.write(self.jmxPath, encoding='utf-8')
                    else:
                        new_json_extract_name = old_json_extract_name
                    child['child_name'] = old_json_extract_name
                    json_extract_xpath = f'/JSONPostProcessor[@testname="{new_json_extract_name}"]'
                    child['xpath'] = json_extract_xpath
                    json_extract_base_xpath = hashTreeXpath + f'/JSONPostProcessor[{json_extract_count}]'
                    json_extract_params_xpath = json_extract_base_xpath + '/stringProp[@name="JSONPostProcessor.referenceNames"]'
                    json_extract_express_xpath = json_extract_base_xpath + '/stringProp[@name="JSONPostProcessor.jsonPathExprs"]'
                    json_extract_match_num_xpath = json_extract_base_xpath + '/stringProp[@name="JSONPostProcessor.match_numbers"]'
                    child['params'] = {"params": tree.xpath(json_extract_params_xpath)[0].text,
                                       "express": tree.xpath(json_extract_express_xpath)[0].text,
                                       "match_num": tree.xpath(json_extract_match_num_xpath)[0].text}
                    json_extract_count += 1
                if cd.tag == "BeanShellPreProcessor":
                    child['child_type'] = 'pre_beanshell'
                    old_pre_beanshell_name = cd.attrib['testname']
                    if upload:
                        new_pre_beanshell_name = old_pre_beanshell_name + "." + Tools.random_str(9)
                        cd.attrib['testname'] = new_pre_beanshell_name
                        tree.write(self.jmxPath, encoding='utf-8')
                    else:
                        new_pre_beanshell_name = old_pre_beanshell_name
                    child['child_name'] = old_pre_beanshell_name
                    pre_beanshell_xpath = f'/BeanShellPreProcessor[@testname="{new_pre_beanshell_name}"]'
                    child['xpath'] = pre_beanshell_xpath
                    pre_beanshell_base_xpath = hashTreeXpath + f'/BeanShellPreProcessor[{pre_beanshell_count}]'
                    pre_beanshell_params_xpath = pre_beanshell_base_xpath + '/stringProp[@name="parameters"]'
                    pre_beanshell_express_xpath = pre_beanshell_base_xpath + '/stringProp[@name="script"]'
                    child['params'] = {"to_beanshell_param": tree.xpath(pre_beanshell_params_xpath)[0].text,
                                       "express": tree.xpath(pre_beanshell_express_xpath)[0].text}
                    pre_beanshell_count += 1
                if cd.tag == "BeanShellPostProcessor":
                    child['child_type'] = 'after_beanshell'
                    old_after_beanshell_name = cd.attrib['testname']
                    if upload:
                        new_after_beanshell_name = old_after_beanshell_name + "." + Tools.random_str(9)
                        cd.attrib['testname'] = new_after_beanshell_name
                        tree.write(self.jmxPath, encoding='utf-8')
                    else:
                        new_after_beanshell_name = old_after_beanshell_name
                    child['child_name'] = old_after_beanshell_name
                    after_beanshell_xpath = f'/BeanShellPostProcessor[@testname="{new_after_beanshell_name}"]'
                    child['xpath'] = after_beanshell_xpath
                    after_beanshell_base_xpath = hashTreeXpath + f'/BeanShellPostProcessor[{after_beanshell_count}]'
                    after_beanshell_params_xpath = after_beanshell_base_xpath + '/stringProp[@name="parameters"]'
                    after_beanshell_express_xpath = after_beanshell_base_xpath + '/stringProp[@name="script"]'
                    child['params'] = {"to_beanshell_param": tree.xpath(after_beanshell_params_xpath)[0].text,
                                       "express": tree.xpath(after_beanshell_express_xpath)[0].text}
                    after_beanshell_count += 1
                if child:
                    children.append(child)
            return children

class OperateJmx():

    def __init__(self, jmxPath):
        # 让添加的节点自动换行
        parser = etree.XMLParser(encoding="utf-8", strip_cdata=False, remove_blank_text=True)
        self.tree = etree.parse(jmxPath, parser=parser)
        self.jmx = jmxPath

    def node_exists(self, xpath):
        rst = self.tree.xpath(xpath)
        if rst:
            return True
        else:
            logger.debug(f"节点不存在：{xpath}")
            return False

    def single_tag_text(self, xpath):
        """
        获取单个节点的text
        :param xpath: 节点xpath
        :return:
        """
        try:
            return self.tree.xpath(xpath)[0].text
        except:
            logger.exception('未找到该节点，或者节点无数据')
            raise

    def change_single_tag_text(self, xpath, text):
        """
        修改单个节点的text
        :param xpath: 节点xpath
        :param text: 节点text
        :return:
        """
        try:
            self.tree.xpath(xpath)[0].text = text
            logger.debug('修改tag的text成功')
        except:
            logger.exception('未找到该节点')
            raise

    def remove_node(self, xpath):
        """
        删除节点
        :param xpath:
        :return:
        """
        try:
            nodes = self.tree.xpath(xpath)
            for node in nodes:
                node.getparent().remove(node)
            logger.debug(f'删除节点成功')
        except:
            logger.exception('未找到该节点')

    def remove_node_and_next(self, xpath, next_name='hashTree'):
        """
        先删除hashTree，再删除节点。删除节点以及临近的节点，一般删除取样器等信息
        :param xpath:
        :return:
        """
        if not xpath:
            return
        try:
            nodes = self.tree.xpath(xpath)
            for node in nodes:
                if next_name:
                    try:
                        next = node.getnext()
                        if next.tag == next_name:
                            node.getparent().remove(next)
                    except:
                        pass
                node.getparent().remove(node)
            logger.debug(f'删除节点成功')
        except:
            logger.exception('未找到该节点')

    def add_peer_node(self, xpath, new_tag_name, tag_idx=-1, text="", **kwargs):
        """
        在同层级添加节点
        :param xpath: 同层级节点路径
        :param tagname: 节点名称
        :param text: 节点text
        :param kwargs: 节点属性
        :return:
        """
        try:
            accord_tag = self.tree.xpath(xpath)[0]
            parent_tag = accord_tag.getparent()
            new_tag = etree.SubElement(parent_tag, new_tag_name)
            new_tag.text = text
            for key, value in kwargs.items():
                new_tag.attrib[key] = value
            # 将tag插入到指定索引位置
            parent_tag.insert(tag_idx, new_tag)
            logger.debug(f'添加同层级节点<{new_tag_name}>成功')
        except:
            logger.exception('未找到该节点')
            raise

    def add_sub_node(self, path, new_tag_name, tag_idx=-1, text=None, **kwargs):
        """
        在添加子节点
        :param xpath: 父节点路径
        :param tagname: 节点名称
        :param text: 节点text
        :param kwargs: 节点属性
        :return:
        """
        try:
            if isinstance(path, etree._Element):
                parent_tag = path
            else:
                parent_tag = self.tree.xpath(path)[0]
            tag = etree.SubElement(parent_tag, new_tag_name)
            if text:
                tag.text = text
            for key, value in kwargs.items():
                tag.attrib[key] = value
            parent_tag.insert(tag_idx, tag)
            logger.debug(f'添加子节点<{new_tag_name}>成功')
            return tag
        except:
            logger.exception('未找到该节点')
            raise

    def save_change(self):
        """
        保存修改后的节点
        :return:
        """
        # 让添加的节点自动换行：pretty_print=True, encoding='utf-8'
        try:
            self.tree.write(self.jmx, pretty_print=True, encoding='utf-8')
        except:
            logger.exception('保存jmx失败')
            raise

class ModifyJMX(OperateJmx):

    def __init__(self, jmxPath):
        # 在jmx的第一个ThreadGroup目录下操作
        self.thread_accord_tag = '//ThreadGroup[1]/following-sibling::hashTree[1]'
        self.setup_accord_tag = '//SetupThreadGroup[1]/following-sibling::hashTree[1]'
        self.teardown_accord_tag = '//PostThreadGroup[1]/following-sibling::hashTree[1]'
        super().__init__(jmxPath)

    def modify_thread_num(self, num_threads, ramp_time, loops, scheduler, duration):
        """
        获取第一个线程组的信息
        :param tree:
        :return:
        """

        thread_xpath = '//ThreadGroup[1]'

        # 线程数
        num_threads_xpath = thread_xpath + "/stringProp[@name='ThreadGroup.num_threads']"
        self.tree.xpath(num_threads_xpath)[0].text = num_threads

        # Ramp-UP时间
        ramp_time_xpath = thread_xpath + "/stringProp[@name='ThreadGroup.ramp_time']"
        self.tree.xpath(ramp_time_xpath)[0].text = ramp_time


        # 循环次数，-1表示永远
        loops_xpath = thread_xpath + "/elementProp/stringProp[@name='LoopController.loops']"
        self.tree.xpath(loops_xpath)[0].text = loops


        # 调度器配置，true or false
        scheduler_xpath = thread_xpath + "/boolProp[@name='ThreadGroup.scheduler']"
        self.tree.xpath(scheduler_xpath)[0].text = scheduler

        if duration:
            # 持续时间
            duration_xpath = thread_xpath + "/stringProp[@name='ThreadGroup.duration']"
            self.tree.xpath(duration_xpath)[0].text = duration

        self.save_change()

    def add_setup_thread(self):
        """
        添加setup线程组
        :return:
        """
        root_xpath = "//jmeterTestPlan/hashTree/hashTree"
        SetupThreadGroup = root_xpath + '/SetupThreadGroup'
        rst = self.node_exists(SetupThreadGroup)
        if not rst:
            setup = self.add_sub_node(root_xpath, new_tag_name='SetupThreadGroup', guiclass="SetupThreadGroupGui",
                              testclass="SetupThreadGroup", testname="setUp线程组", enabled="true")
            self.add_sub_node(setup, new_tag_name='stringProp', text='continue', name="ThreadGroup.on_sample_error")
            elementProp = self.add_sub_node(setup, new_tag_name='elementProp', name="ThreadGroup.main_controller",
                              elementType="LoopController", guiclass="LoopControlPanel", testclass="LoopController",
                              testname="循环控制器", enabled="true")
            self.add_sub_node(elementProp, new_tag_name='boolProp', text='false', name="LoopController.continue_forever")
            self.add_sub_node(elementProp, new_tag_name='stringProp', text='1', name="LoopController.loops")
            self.add_sub_node(setup, new_tag_name='stringProp', text='1', name="ThreadGroup.num_threads")
            self.add_sub_node(setup, new_tag_name='stringProp', text='1', name="ThreadGroup.ramp_time")
            self.add_sub_node(setup, new_tag_name='boolProp', text='false', name="ThreadGroup.scheduler")
            self.add_sub_node(setup, new_tag_name='stringProp', name="ThreadGroup.duration")
            self.add_sub_node(setup, new_tag_name='stringProp', name="ThreadGroup.delay")

            # 添加hashTree
            self.add_sub_node(root_xpath, new_tag_name='hashTree')

            self.save_change()

    def add_teardown_thread(self):
        """
        添加setup线程组
        :return:
        """
        root_xpath = "//jmeterTestPlan/hashTree/hashTree"
        PostThreadGroup = root_xpath + '/PostThreadGroup'
        rst = self.node_exists(PostThreadGroup)
        if not rst:
            setup = self.add_sub_node(root_xpath, new_tag_name='PostThreadGroup', guiclass="PostThreadGroupGui",
                              testclass="PostThreadGroup", testname="tearDown线程组", enabled="true")
            self.add_sub_node(setup, new_tag_name='stringProp', text='continue', name="ThreadGroup.on_sample_error")
            elementProp = self.add_sub_node(setup, new_tag_name='elementProp', name="ThreadGroup.main_controller",
                              elementType="LoopController", guiclass="LoopControlPanel", testclass="LoopController",
                              testname="循环控制器", enabled="true")
            self.add_sub_node(elementProp, new_tag_name='boolProp', text='false', name="LoopController.continue_forever")
            self.add_sub_node(elementProp, new_tag_name='stringProp', text='1', name="LoopController.loops")
            self.add_sub_node(setup, new_tag_name='stringProp', text='1', name="ThreadGroup.num_threads")
            self.add_sub_node(setup, new_tag_name='stringProp', text='1', name="ThreadGroup.ramp_time")
            self.add_sub_node(setup, new_tag_name='boolProp', text='false', name="ThreadGroup.scheduler")
            self.add_sub_node(setup, new_tag_name='stringProp', name="ThreadGroup.duration")
            self.add_sub_node(setup, new_tag_name='stringProp', name="ThreadGroup.delay")

            # 添加hashTree
            self.add_sub_node(root_xpath, new_tag_name='hashTree')

            self.save_change()

    def add_sampler(self, name, url, method, accord='thread', param_type='form', params=None, xpath=None):
        """
        添加取样器，可以在thread或者setup中添加
        :param name: 取样器名称
        :param url: url
        :param method: 方法
        :param accord: 在thread或者setup中添加
        :param param_type: 参数类型
        :param param: 参数
        :param xpath: 取样器地址，可以先删除之前的取样器，再重新添加
        :return:
        """
        params_info = []
        sampler_info = {}
        try:
            # 如果是form格式，就需要转换为字典
            if params and isinstance(params, list):
                params_info = params
        except:
            logger.error('参数格式错误！')
            raise

        if accord == 'thread':
            accord_tag = self.thread_accord_tag
        elif accord == 'setup':
            accord_tag = self.setup_accord_tag
        elif accord == 'teardown':
            accord_tag = self.teardown_accord_tag
        else:
            logger.error('accord参数错误')
            raise

        name = name + "." + Tools.random_str(9)

        if xpath:
            # 如果是修改，则删除所有子节点，重新添加参数
            sampler = self.tree.xpath(xpath)[0]
            sampler_children = sampler.getchildren()
            for child in sampler_children:
                child.getparent().remove(child)
            sampler.attrib['testname'] = name
            HTTPSamplerProxy = accord_tag + f"/HTTPSamplerProxy[@testname='{name}']"
        else:
            HTTPSamplerProxy = accord_tag + f"/HTTPSamplerProxy[@testname='{name}']"

            # 在最后的位置插入sampler
            self.add_sub_node(accord_tag, new_tag_name='HTTPSamplerProxy', guiclass="HttpTestSampleGui",
                              testclass="HTTPSamplerProxy", testname=name, enabled="true")

            # 添加hashTree
            self.add_sub_node(accord_tag, new_tag_name='hashTree')

        sampler_info['params'] = ''
        if param_type == 'form':
            self._add_form_data(HTTPSamplerProxy, params_info)
            sampler_info['params'] = params_info
        elif param_type == 'raw':
            self._add_raw_data(HTTPSamplerProxy, params)
            sampler_info['params'] = params

        self._add_sampler_base(HTTPSamplerProxy, url, method)
        self.save_change()
        sampler_info['thread_type'] = accord
        sampler_info['name'] = name
        sampler_info['xpath'] = HTTPSamplerProxy
        sampler_info['url'] = url
        sampler_info['method'] = method
        sampler_info['param_type'] = param_type
        return sampler_info

    def add_csv(self, name, filename, variableNames, delimiter, ignoreFirstLine, recycle, stopThread, accord, xpath=None):
        """
        添加csv数据文件设置
        :param filename: 文件路径
        :param paramname: 参数名称，以逗号隔开
        :param ignoreFirstLine: 是否忽略首行数据，首行数据可能包含表头
        :param recycle: 遇到文件结束符是否再次循环
        :param stopThread: 遇到文件结束符是否结束线程
        :param accord: 父路径，决定是setup,thread,teardown中添加
        :param xpath: 已存在的csv路径，修改时候，先删除，再添加
        :return:
        """

        if accord == 'thread':
            accord_tag = self.thread_accord_tag
        elif accord == 'setup':
            accord_tag = self.setup_accord_tag
        elif accord == 'teardown':
            accord_tag = self.teardown_accord_tag
        else:
            logger.error('accord参数错误')
            raise

        self.remove_node_and_next(xpath)

        csvname = name + '.' + Tools.random_str(9)

        CSVDataSet = accord_tag + f"/CSVDataSet[@testname='{csvname}']"

        # 在最后的位置插入sampler
        csv = self.add_sub_node(accord_tag, new_tag_name='CSVDataSet', guiclass="TestBeanGUI",
                               testclass="CSVDataSet", testname=csvname, enabled="true")

        # 添加hashTree
        self.add_sub_node(accord_tag, new_tag_name='hashTree')

        self.add_sub_node(csv, new_tag_name='stringProp', text=delimiter, name="delimiter")
        self.add_sub_node(csv, new_tag_name='stringProp', name="fileEncoding")
        self.add_sub_node(csv, new_tag_name='stringProp', text=filename, name="filename")
        self.add_sub_node(csv, new_tag_name='boolProp', text=ignoreFirstLine, name="ignoreFirstLine")
        self.add_sub_node(csv, new_tag_name='boolProp', text='false', name="c")
        self.add_sub_node(csv, new_tag_name='boolProp', text=recycle, name="recycle")
        self.add_sub_node(csv, new_tag_name='stringProp', text='shareMode.all', name="shareMode")
        self.add_sub_node(csv, new_tag_name='boolProp', text=stopThread, name="stopThread")
        self.add_sub_node(csv, new_tag_name='stringProp', text=variableNames, name="variableNames")

        self.save_change()

        csv_info = {}

        csv_info['thread_type'] = accord
        csv_info['name'] = name
        csv_info['xpath'] = CSVDataSet
        csv_info['filename'] = filename
        csv_info['ignoreFirstLine'] = ignoreFirstLine
        csv_info['recycle'] = recycle
        csv_info['stopThread'] = stopThread
        csv_info['delimiter'] = delimiter
        csv_info['variableNames'] = variableNames

        return csv_info

    def add_backendListener(self, influxdb_url, application_name, measurement_name='jmeter'):

        """
        添加后端监听器
        :param influxdb_url:
        :param application_name:
        :return:
        """

        BackendListener = self.thread_accord_tag + '/BackendListener'

        self.remove_node_and_next(BackendListener)

        self.add_sub_node(self.thread_accord_tag, new_tag_name='BackendListener', tag_idx=0, guiclass="BackendListenerGui",
                          testclass="BackendListener", testname="后端监听器", enabled="true")

        self.add_sub_node(self.thread_accord_tag, new_tag_name='hashTree', tag_idx=1)

        elementProp = self.add_sub_node(BackendListener, new_tag_name='elementProp', name="arguments", elementType="Arguments",
                          guiclass="ArgumentsPanel", testclass="Arguments", enabled="true")

        collectionProp = self.add_sub_node(elementProp, new_tag_name='collectionProp', name="Arguments.arguments")

        # influxdbMetricsSender
        influxdbMetricsSender = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="influxdbMetricsSender", elementType="Argument")
        self._add_param(influxdbMetricsSender, param_name='influxdbMetricsSender',
                        param_value='org.apache.jmeter.visualizers.backend.influxdb.HttpMetricsSender')

        # influxdbUrl
        influxdbUrl = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="influxdbUrl", elementType="Argument")
        self._add_param(influxdbUrl, param_name='influxdbUrl', param_value=influxdb_url)

        # application
        application = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="application", elementType="Argument")
        self._add_param(application, param_name='application', param_value=application_name)

        # measurement
        measurement = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="measurement", elementType="Argument")
        self._add_param(measurement, param_name='measurement', param_value=measurement_name)

        # summaryOnly
        summaryOnly = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="summaryOnly", elementType="Argument")
        self._add_param(summaryOnly, param_name='summaryOnly', param_value='False')

        # samplersRegex
        samplersRegex = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="samplersRegex", elementType="Argument")
        self._add_param(samplersRegex, param_name='samplersRegex',param_value='.*')

        # percentiles
        percentiles = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="percentiles", elementType="Argument")
        self._add_param(percentiles, param_name='percentiles', param_value='99;95;90')

        # testTitle
        testTitle = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="testTitle", elementType="Argument")
        self._add_param(testTitle, param_name='testTitle', param_value='Test name')

        # eventTags
        eventTags = self.add_sub_node(collectionProp, new_tag_name='elementProp',
                                                  name="eventTags", elementType="Argument")
        self._add_param(eventTags, param_name='eventTags', param_value='')

        self.add_sub_node(BackendListener, new_tag_name='stringProp',
                          text='org.apache.jmeter.visualizers.backend.influxdb.InfluxdbBackendListenerClient',
                          name='classname')

        self.save_change()

    def add_header(self, sampler_xpath, name, headers, header_xpath=None):
        """
        添加请求头信息，一个sampler只允许添加一个
        :param sampler_xpath: sampler的xpath路径
        :param headers: 信息头字典
        :param header_name: 信息头名称
        :return:
        """
        hashTree = self._remove_sampler_child(sampler_xpath, header_xpath)
        header_name = name + "." + Tools.random_str(9)
        header = self.add_sub_node(hashTree, new_tag_name='HeaderManager', guiclass="HeaderPanel",
                                   testclass="HeaderManager",
                                   testname=header_name, enabled="true")
        # 添加hashTree
        self.add_sub_node(hashTree, new_tag_name="hashTree")
        collectionProp = self.add_sub_node(header, new_tag_name="collectionProp", name="HeaderManager.headers")
        for item in headers:
            try:
                self._add_headers_param(collectionProp, item['key'], item['value'])
            except:
                logger.exception("参数错误，找不到键【key，value】！")
                raise

        new_header_xpath = f'//HeaderManager[@testname="{header_name}"]'
        self.save_change()
        child_info = {}
        child_info['child_type'] = "header"
        child_info['xpath'] = new_header_xpath
        child_info['params'] = headers
        return child_info

    def add_rsp_assert(self, sampler_xpath, name, assert_str, assert_content, rsp_assert_xpath=None):
        """
        添加响应信息断言
        :param sampler_xpath: 目标取样器
        :param rsp_assert_xpath: 断言的xpath路径，方便后续修改，先删除，再修改
        :param rsp_assert_name: 断言名称
        :param assert_content: 断言内容
        :return:
        """
        hashTree = self._remove_sampler_child(sampler_xpath, rsp_assert_xpath)
        assert_type = self._to_assert_type(assert_str)
        rsp_assert_name = name + "." + Tools.random_str(9)
        rsp_assert = self.add_sub_node(hashTree, new_tag_name="ResponseAssertion", guiclass="AssertionGui",
                                       testclass="ResponseAssertion", testname=rsp_assert_name, enabled="true")
        self.add_sub_node(hashTree, new_tag_name="hashTree")
        collectionProp = self.add_sub_node(rsp_assert, new_tag_name="collectionProp", name="Asserion.test_strings")
        for ac in assert_content:
            if ac['key']:
                self.add_sub_node(collectionProp, new_tag_name="stringProp", text=ac['key'], name=str(time.time()))
        self.add_sub_node(rsp_assert, new_tag_name="stringProp", name="Assertion.custom_message")
        self.add_sub_node(rsp_assert, new_tag_name="stringProp", text="Assertion.response_data", name="Assertion.test_field")
        self.add_sub_node(rsp_assert, new_tag_name="boolProp", text="false", name="Assertion.assume_success")
        self.add_sub_node(rsp_assert, new_tag_name="intProp", text=assert_type, name="Assertion.test_type")

        new_rsp_assert_xpath = f'//ResponseAssertion[@testname="{rsp_assert_name}"]'
        self.save_change()

        child_info = {}
        child_info['child_type'] = "rsp_assert"
        child_info['xpath'] = new_rsp_assert_xpath
        child_info['params'] = {"rsp_assert_content": assert_content, "rsp_assert_type": list(assert_str)}
        return child_info

    def add_json_extract(self, sampler_xpath, name, params, express, match_num, json_extract_xpath=None):
        """
        添加json提取器
        :param sampler_xpath: sampler的路径
        :param name: json提取器名称，匹配多个以分号隔开
        :param params: json提取器参数，匹配多个以分号隔开
        :param json_extract_xpath: json提取器路径，如果传了，则删除原有的，如果没有，则新增
        :return:
        """
        hashTree = self._remove_sampler_child(sampler_xpath, json_extract_xpath)
        json_extract_name = name + "." + Tools.random_str(9)
        json_extract = self.add_sub_node(hashTree, new_tag_name="JSONPostProcessor", guiclass="JSONPostProcessorGui",
                                       testclass="JSONPostProcessor", testname=json_extract_name, enabled="true")
        self.add_sub_node(hashTree, new_tag_name="hashTree")
        self.add_sub_node(json_extract, new_tag_name="stringProp", text=params, name="JSONPostProcessor.referenceNames")
        self.add_sub_node(json_extract, new_tag_name="stringProp", text=express, name="JSONPostProcessor.jsonPathExprs")
        self.add_sub_node(json_extract, new_tag_name="stringProp", text=str(match_num), name="JSONPostProcessor.match_numbers")

        new_json_extract_xpath = f'//JSONPostProcessor[@testname="{json_extract_name}"]'
        self.save_change()

        child_info = {}
        child_info['child_type'] = "json_extract"
        child_info['xpath'] = new_json_extract_xpath
        child_info['params'] = {"params": params, "express": express, "match_num": match_num}
        return child_info

    def add_after_beanshell(self, sampler_xpath, name, to_beanshell_param, express, after_beanshell_xpath=None):
        """
        添加后置处理器
        :param sampler_xpath:
        :param name:
        :param to_beanshell_param:
        :param express:
        :param after_beanshell_xpath:
        :return:
        """

        hashTree = self._remove_sampler_child(sampler_xpath, after_beanshell_xpath)
        after_beanshell_name = name + "." + Tools.random_str(9)

        after_beanshell = self.add_sub_node(hashTree, new_tag_name="BeanShellPostProcessor", guiclass="TestBeanGUI",
                                       testclass="BeanShellPostProcessor", testname=after_beanshell_name, enabled="true")
        self.add_sub_node(hashTree, new_tag_name="hashTree")
        self.add_sub_node(after_beanshell, new_tag_name="stringProp", name="filename")
        self.add_sub_node(after_beanshell, new_tag_name="stringProp", text=to_beanshell_param, name="parameters")
        self.add_sub_node(after_beanshell, new_tag_name="boolProp", text="false", name="resetInterpreter")
        self.add_sub_node(after_beanshell, new_tag_name="stringProp", text=express, name="script")

        new_after_beanshell_xpath = f'//BeanShellPostProcessor[@testname="{after_beanshell_name}"]'
        self.save_change()

        child_info = {}
        child_info['child_type'] = "json_extract"
        child_info['xpath'] = new_after_beanshell_xpath
        child_info['params'] = {"to_beanshell_param": to_beanshell_param, "express": express}
        return child_info

    def add_pre_beanshell(self, sampler_xpath, name, to_beanshell_param, express, pre_beanshell_xpath=None):
        """
        添加前置处理器
        :param sampler_xpath:
        :param name:
        :param to_beanshell_param:
        :param express:
        :param pre_beanshell_xpath:
        :return:
        """

        hashTree = self._remove_sampler_child(sampler_xpath, pre_beanshell_xpath)
        pre_beanshell_name = name + "." + Tools.random_str(9)

        pre_beanshell = self.add_sub_node(hashTree, new_tag_name="BeanShellPreProcessor", guiclass="TestBeanGUI",
                                       testclass="BeanShellPreProcessor", testname=pre_beanshell_name, enabled="true")
        self.add_sub_node(hashTree, new_tag_name="hashTree")
        self.add_sub_node(pre_beanshell, new_tag_name="stringProp", name="filename")
        self.add_sub_node(pre_beanshell, new_tag_name="stringProp", text=to_beanshell_param, name="parameters")
        self.add_sub_node(pre_beanshell, new_tag_name="boolProp", text="false", name="resetInterpreter")
        self.add_sub_node(pre_beanshell, new_tag_name="stringProp", text=express, name="script")

        new_pre_beanshell_name_xpath = f'//BeanShellPreProcessor[@testname="{pre_beanshell_name}"]'
        self.save_change()

        child_info = {}
        child_info['child_type'] = "json_extract"
        child_info['xpath'] = new_pre_beanshell_name_xpath
        child_info['params'] = {"to_beanshell_param": to_beanshell_param, "express": express}
        return child_info

    def add_json_assert(self, sampler_xpath, name, json_path, expected_value, expect_null, invert, json_aassert_xpath=None):
        """
        json断言
        :param sampler_xpath: 取样器的路径
        :param name: json断言名称
        :param json_path: json断言路径
        :param expected_value: 期望值
        :param expect_null: 取值为空
        :param invert: 断言结果取反
        :return:
        """

        hashTree = self._remove_sampler_child(sampler_xpath, json_aassert_xpath)
        json_assert_name = name + "." + Tools.random_str(9)

        json_assert = self.add_sub_node(hashTree, new_tag_name="JSONPathAssertion", guiclass="JSONPathAssertionGui",
                                       testclass="JSONPathAssertion", testname=json_assert_name, enabled="true")
        self.add_sub_node(hashTree, new_tag_name="hashTree")
        self.add_sub_node(json_assert, new_tag_name="stringProp", text=json_path, name="JSON_PATH")
        self.add_sub_node(json_assert, new_tag_name="stringProp", text=expected_value, name="EXPECTED_VALUE")
        self.add_sub_node(json_assert, new_tag_name="boolProp", text="true", name="JSONVALIDATION")
        self.add_sub_node(json_assert, new_tag_name="boolProp", text="false", name="EXPECT_NULL")
        self.add_sub_node(json_assert, new_tag_name="boolProp", text="false", name="INVERT")
        self.add_sub_node(json_assert, new_tag_name="boolProp", text="true", name="ISREGEX")

        new_json_assert_name_xpath = f'//JSONPathAssertion[@testname="{json_assert_name}"]'
        self.save_change()

        child_info = {}
        child_info['child_type'] = "json_extract"
        child_info['xpath'] = new_json_assert_name_xpath
        child_info['params'] = {"json_path": json_path, "expected_value": expected_value, "expect_null": expect_null, "invert": invert}
        return child_info

    def _add_param(self, parent_node, param_name, param_value):
        """
        常规参数
        :param parent_node:
        :param param_name:
        :param param_value:
        :return:
        """
        self.add_sub_node(parent_node, new_tag_name='stringProp', text=param_name, name="Argument.name")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text=param_value, name="Argument.value")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='=', name="Argument.metadata")

    def _add_sampler_base(self, parent_node, url, method):
        """
        sapmpler基础参数
        :param parent_node:
        :param url:
        :param method:
        :return:
        """
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.domain")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.port")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.protocol")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.contentEncoding", text="utf-8")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text=url, name="HTTPSampler.path")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text=method, name="HTTPSampler.method")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='true', name="HTTPSampler.follow_redirects")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='false', name="HTTPSampler.auto_redirects")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='true', name="HTTPSampler.use_keepalive")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='false', name="HTTPSampler.DO_MULTIPART_POST")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.embedded_url_re")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.connect_timeout")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.response_timeout")

    def _add_headers_param(self, parent_node, param_name, param_value):
        """
        添加headers参数
        :param parent_node:
        :param param_name:
        :param param_value:
        :return:
        """
        elementProp = self.add_sub_node(parent_node, new_tag_name='elementProp', name="", elementType="Header")
        self.add_sub_node(elementProp, new_tag_name='stringProp', text=param_name, name="Header.name")
        self.add_sub_node(elementProp, new_tag_name='stringProp', text=param_value, name="Header.value")

    def _add_form_data(self, xpath, params):
        """
        添加form表单数据，传入一个字典
        :param xpath: sampler的路径
        :param params:
        :return:
        """
        count = 1
        # xpath为sampler的路径
        # elementProp为collectionProp的父路径
        elementProp = xpath + '/elementProp'
        collectionProp = elementProp + '/collectionProp'

        self.remove_node(elementProp)

        # 重新添加xpath/elementProp
        self.add_sub_node(xpath, 'elementProp', name="HTTPsampler.Arguments", elementType="Arguments")

        # 在elementProp节点下添加collectionProp节点
        self.add_sub_node(elementProp, new_tag_name='collectionProp', name='Arguments.arguments')

        if not isinstance(params, list):
            logger.exception('参数必须是一个列表')
            raise
        for param in params:
            sub_elementProp = collectionProp + f'/elementProp[{count}]'
            self.add_sub_node(collectionProp, new_tag_name='elementProp', name=param['key'], elementType='HTTPArgument')
            self.add_sub_node(sub_elementProp, new_tag_name='boolProp', text='false', name='HTTPArgument.always_encode')
            self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text=param['value'], name='Argument.value')
            self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text='=', name='Argument.metadata')
            self.add_sub_node(sub_elementProp, new_tag_name='boolProp', text='true', name='HTTPArgument.use_equals')
            self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text=param['key'], name='Argument.name')
            count += 1
        self.save_change()

    def _add_raw_data(self, xpath, raw):
        """
        添加raw格式的json
        :param xpath: sampler的路径
        :param raw:
        :return:
        """

        elementProp = xpath + '/elementProp'
        collectionProp = elementProp + '/collectionProp'

        # 先删除boolProp节点，xpath为sampler的路径
        self.remove_node(xpath + '/boolProp[@name="HTTPSampler.postBodyRaw"]')

        # 重新添加boolProp节点
        self.add_sub_node(xpath, new_tag_name='boolProp', tag_idx=0, text='true', name='HTTPSampler.postBodyRaw')
        # 删除elementProp
        self.remove_node(elementProp)

        # 重新添加xpath/elementProp
        self.add_sub_node(xpath, 'elementProp', name="HTTPsampler.Arguments", elementType="Arguments")

        self.add_sub_node(elementProp, new_tag_name='collectionProp', name='Arguments.arguments')
        sub_elementProp = self.add_sub_node(collectionProp, new_tag_name='elementProp', name="", elementType='HTTPArgument')
        self.add_sub_node(sub_elementProp, new_tag_name='boolProp', text='false', name='HTTPArgument.always_encode')
        self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text=raw, name='Argument.value')
        self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text='=', name='Argument.metadata')
        self.save_change()

    def _to_assert_type(self, assert_str):
        """
        生成断言代码
        :param assert_str: 断言的字符
        :return:
        """
        try:
            assert_type_dict = Tools.assert_type_dict()
            return str(assert_type_dict[assert_str])
        except:
            logger.exception("无效的断言字符参数")
            raise

    def _remove_sampler_child(self, sampler_xpath, child_xpath):
        """
        移除sampler子元素
        :param sampler_xpath:
        :param child_xpath:
        :return:
        """
        try:
            if child_xpath:
                self.remove_node_and_next(child_xpath)
            hashTree = self.tree.xpath(sampler_xpath)[0].getnext()
            return hashTree
        except:
            logger.exception("获取sampler信息失败")
            raise

if __name__ == '__main__':
    # r = ModifyJMX('/Users/chenlei/jmeter5/jmx_folder/django.jmx')
    # s = r.add_sampler(name='sampler', url='http://www.baidu.com', method="GET")
    # print(s)
    jmx = '/Users/chenlei/python-project/jmeter_platform/performance_files/jmx/新增jmx-1600051758672.jmx'
    # o = ModifyJMX(jmx)
    # xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy[@testname="xxx"]'
    # o.add_header(sampler_xpath=xpath, headers={'aaaa': 'bbaa'}, header_name="aaaaaaa")
    r = ReadJmx(jmx)
    s = r.analysis_jmx()
    print(json.dumps(s))






