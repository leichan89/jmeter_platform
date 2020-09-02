# -*- coding: utf-8 -*-
# @Time    : 2020-09-02 17:56
# @Author  : OG·chen
# @File    : operate.py

from lxml import etree
import logging
import json
from common.Tools import Tools

logger = logging.getLogger('collect')

class ReadJmx():

    def __init__(self, jmxPath):
        self.jmxPath = jmxPath

    def analysis_jmx(self):
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
            "israw": 判断请求参数是否是raw格式
            "params": [
                "paramname": 参数名称
                "paramvalue": 参数值
            ]
        ]
        )
        """
        try:
            tree = etree.parse(self.jmxPath)
            ThreadGroup = tree.xpath('//ThreadGroup')
            if not ThreadGroup:
                logger.error('jmx文件没有线程组')
                return None
        except:
            logger.error('解析jmx错误')
            return None

        setup_thread_xpath = '//SetupThreadGroup'

        # thread线程组root节点
        thread_sapmler_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        thread_csv_root_xpath = '//ThreadGroup[1]/following-sibling::hashTree[1]/CSVDataSet'

        # setup线程组root节点
        setup_sapmler_root_xpath = '//SetupThreadGroup[1]/following-sibling::hashTree[1]/HTTPSamplerProxy'
        setup_csv_root_xpath = '//SetupThreadGroup[1]/following-sibling::hashTree[1]/CSVDataSet'

        # 获取setup线程组的名称
        setup_thread_name = ""
        setup_thread = tree.xpath(setup_thread_xpath)
        if setup_thread:
            setup_thread_name = setup_thread[0].attrib['testname']

        thread_sapmlers_info = self._read_sampler(tree, thread_sapmler_root_xpath)

        thread_csvs_info = self._read_csv(tree, thread_csv_root_xpath)

        setup_sapmlers_info = self._read_sampler(tree, setup_sapmler_root_xpath, thread_type='setup')

        setup_csvs_info = self._read_csv(tree, setup_csv_root_xpath, thread_type='setup')

        sapmlers_info = thread_sapmlers_info + setup_sapmlers_info
        csvs_info = thread_csvs_info + setup_csvs_info


        return setup_thread_name, sapmlers_info, csvs_info

    def _read_sampler(self, tree, sapmler_root_xpath, thread_type='thread'):
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

            param_israw_xpath = f"{sampler_xpath}/boolProp[@name='HTTPSampler.postBodyRaw']"

            # jmx请求参数的节点，get请求的参数可能会有多个elementProp，一个参数一个
            sapmler_param_xpath = f"{sapmler_root_xpath}[{sidx + 1}]/elementProp/collectionProp/elementProp"

            # 取样器xpath
            sampler_info['xpath'] = sampler_xpath

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
                            else:
                                # raw格式的参数，没有Argument.name这个标签
                                paramname = ""
                            paramvalue = value.text
                            sampler_info['params'].append({"paramname": paramname, "paramvalue": paramvalue})
            sapmlers_info.append(sampler_info)

        return sapmlers_info

    def _read_csv(self, tree, csv_root_xpath, thread_type='thread'):
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
                csv_info['xpath'] = csv_xpath

                csv_name = csv.attrib['testname']
                csv_info['name'] = csv_name

                delimiter_xpath = csv_xpath + '/stringProp[@name="delimiter"]'
                delimiter = tree.xpath(delimiter_xpath)[0].text
                csv_info['delimiter'] = delimiter

                fileEncoding_xpath = csv_xpath + '/stringProp[@name="fileEncoding"]'
                fileEncoding = tree.xpath(fileEncoding_xpath)[0].text
                csv_info['fileEncoding'] = fileEncoding

                filename_xpath = csv_xpath + '/stringProp[@name="filename"][1]'
                filename = tree.xpath(filename_xpath)[0].text
                csv_info['filename'] = filename

                ignoreFirstLine_xpath = csv_xpath + '/boolProp[@name="ignoreFirstLine"]'
                ignoreFirstLine = tree.xpath(ignoreFirstLine_xpath)[0].text
                csv_info['ignoreFirstLine'] = ignoreFirstLine

                quotedData_xpath = csv_xpath + '/boolProp[@name="quotedData"]'
                quotedData = tree.xpath(quotedData_xpath)[0].text
                csv_info['quotedData'] = quotedData

                recycle_xpath = csv_xpath + '/boolProp[@name="recycle"]'
                recycle = tree.xpath(recycle_xpath)[0].text
                csv_info['recycle'] = recycle

                shareMode_xpath = csv_xpath + '/stringProp[@name="shareMode"]'
                shareMode = tree.xpath(shareMode_xpath)[0].text
                csv_info['shareMode'] = shareMode

                stopThread_xpath = csv_xpath + '/boolProp[@name="stopThread"]'
                stopThread = tree.xpath(stopThread_xpath)[0].text
                csv_info['stopThread'] = stopThread

                variableNames_xpath = csv_xpath + '/stringProp[@name="variableNames"]'
                variableNames = tree.xpath(variableNames_xpath)[0].text
                csv_info['variableNames'] = variableNames

                csvs_info.append(csv_info)

        return csvs_info


class OperateJmx():

    def __init__(self, jmx):
        # 让添加的节点自动换行
        parser = etree.XMLParser(encoding="utf-8", strip_cdata=False, remove_blank_text=True)
        self.tree = etree.parse(jmx, parser=parser)
        self.jmx = jmx

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
        删除节点以及临近的节点，一般删除取样器等信息
        :param xpath:
        :return:
        """
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

    def __init__(self, jmx):
        # 在jmx的第一个ThreadGroup目录下操作
        self.accord_tag = '//ThreadGroup[1]/following-sibling::hashTree[1]'
        super().__init__(jmx)


    def add_form_data(self, xpath, params):
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

        if not isinstance(params, dict):
            logger.exception('参数必须是一个字典')
            raise
        for key, value in params.items():
            try:
                value = str(value)
            except:
                pass
            sub_elementProp = collectionProp + f'/elementProp[{count}]'
            self.add_sub_node(collectionProp, new_tag_name='elementProp', name=value, elementType='HTTPArgument')
            self.add_sub_node(sub_elementProp, new_tag_name='boolProp', text='false', name='HTTPArgument.always_encode')
            self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text=value, name='Argument.value')
            self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text='=', name='Argument.metadata')
            self.add_sub_node(sub_elementProp, new_tag_name='boolProp', text='true', name='HTTPArgument.use_equals')
            self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text=key, name='Argument.name')
            count += 1
        self.save_change()

    def add_json_data(self, xpath, raw):
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

        try:
            # 将raw格式转换为字符串
            raw = json.dumps(raw)
        except:
            logger.exception('无效的json格式')
            raise

        self.add_sub_node(elementProp, new_tag_name='collectionProp', name='Arguments.arguments')
        sub_elementProp = self.add_sub_node(collectionProp, new_tag_name='elementProp', name="", elementType='HTTPArgument')
        self.add_sub_node(sub_elementProp, new_tag_name='boolProp', text='false', name='HTTPArgument.always_encode')
        self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text=raw, name='Argument.value')
        self.add_sub_node(sub_elementProp, new_tag_name='stringProp', text='=', name='Argument.metadata')
        self.save_change()

    def add_sampler(self, xpath, name, url, method, param_type, param):
        """
        添加sampler，添加前可以先删除之前的，再添加
        :param name: sampler名称
        :param url: 接口地址
        :param method: 接口方法
        :param param_type: 参数类型，1是form，2是raw
        :param param: 参数
        :return:
        """

        self.remove_node_and_next(xpath)

        name = name + '-' + str(Tools.datetime2timestamp(to11=True))

        HTTPSamplerProxy = self.accord_tag + f'/HTTPSamplerProxy[@testname="{name}"]'

        # 在最后的位置插入sampler
        sp = self.add_sub_node(self.accord_tag, new_tag_name='HTTPSamplerProxy', guiclass="HttpTestSampleGui",
                          testclass="HTTPSamplerProxy", testname=name, enabled="true")

        # 添加hashTree
        self.add_sub_node(self.accord_tag, new_tag_name='hashTree')

        #
        # 1是form表单，2是raw
        if param_type == 1 and isinstance(param, dict):
            self.add_form_data(HTTPSamplerProxy, param)
        if param_type == 2:
            self.add_json_data(HTTPSamplerProxy, param)

        self._add_sampler_base(sp, url, method)

        self.save_change()


    def add_backendListener(self, influxdb_url, application_name, measurement_name='jmeter'):

        """
        添加后端监听器
        :param influxdb_url:
        :param application_name:
        :return:
        """

        BackendListener = self.accord_tag + '/BackendListener'

        self.remove_node_and_next(BackendListener)

        self.add_sub_node(self.accord_tag, new_tag_name='BackendListener', tag_idx=0, guiclass="BackendListenerGui",
                          testclass="BackendListener", testname="后端监听器", enabled="true")

        self.add_sub_node(self.accord_tag, new_tag_name='hashTree', tag_idx=1)

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
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.contentEncoding")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text=url, name="HTTPSampler.path")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text=method, name="HTTPSampler.method")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='true', name="HTTPSampler.follow_redirects")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='false', name="HTTPSampler.auto_redirects")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='true', name="HTTPSampler.use_keepalive")
        self.add_sub_node(parent_node, new_tag_name='stringProp', text='false', name="HTTPSampler.DO_MULTIPART_POST")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.embedded_url_re")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.connect_timeout")
        self.add_sub_node(parent_node, new_tag_name='stringProp', name="HTTPSampler.response_timeout")

if __name__ == '__main__':
    r = ReadJmx('/Users/chenlei/jmeter5/jmx_folder/django.jmx')
    s = r.analysis_jmx()
    print(json.dumps(s))




