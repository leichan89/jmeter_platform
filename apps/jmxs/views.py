from common.APIResponse import APIRsp
from common.Operate import ReadJmx, ModifyJMX, OperateJmx
from common.Tools import Tools
from rest_framework.views import APIView
from .models import JmxThreadGroup, SamplersChildren
from jmeter_platform import settings
from jmxs.serializer import JmxsSerializer, JmxListSerializer, JmxSerializer, JmxsRunSerializer, JmxThreadGroupSerializer
from .models import Jmxs
from rest_framework import status
from rest_framework import generics
from rest_framework import filters
from rest_framework.pagination import PageNumberPagination
import json
import os
import logging
import shutil

logger = logging.getLogger(__file__)

class JmxsPagination(PageNumberPagination):
    """
    自定义分页
    """
    # 每页数量
    page_size_query_param = 'size'
    # 第几页
    page_query_param = 'num'

class JmxUpload(APIView):
    """
    上传jmx文件，
    上传后，将jmx持久化
    在页面修改参数时，需要修改jmx文件，修改完后，重新获取参数信息，然后重新更新到数据库
    """
    def post(self, request):
        """
        :param request: {'jmx': 'name': , 'add_user': 1}
        :return:
        """
        data = {}
        jmx = request.FILES.get('jmx')
        jmx_alias = request.POST.get('jmxName')
        user = request.POST.get('addUser')
        if jmx and user:
            jmx_name_ext = os.path.splitext(jmx.name)
            jmx_name = jmx_name_ext[0]
            jmx_ext = jmx_name_ext[1]
            if jmx_ext not in settings.JMX_ALLOWED_FILE_TYPE:
                return APIRsp(code=205, msg='无效的格式，请上传.jmx格式的文件', status=status.HTTP_205_RESET_CONTENT)
            jmxfile = jmx_name + "." + Tools.random_str(9) + jmx_ext
            jmxpath = settings.JMX_URL + jmxfile

            with open(jmxpath, 'wb') as f:
                for i in jmx.chunks():
                    f.write(i)

            jmxinfo = ReadJmx(jmxpath).analysis_jmx()
            if not jmxinfo:
                return APIRsp(code=400, msg='添加失败，jmx文件错误', status=status.HTTP_400_BAD_REQUEST)

            samplers_info = jmxinfo[0]
            csvs_info = jmxinfo[1]
            thread_info = jmxinfo[2]

            # jmx路径
            data['jmx'] = jmxpath

            # jmx名称
            if jmx_alias:
                data['jmx_alias'] = jmx_alias
            else:
                data['jmx_alias'] = jmx_name

            # user的id不存在时，会校验失败
            data['add_user'] = user

            # 线程组基础信息
            data['thread_base_info'] = json.dumps(thread_info)

            obj = JmxsSerializer(data=data)

            # 校验数据格式
            if obj.is_valid():
                obj.save()
                jmx_id = obj.data['id']
                for sampler in samplers_info:
                    # 保存sampler信息
                    sampler_children = sampler['children']
                    del sampler['children']

                    sp = JmxThreadGroup(jmx_id=jmx_id, child_name=sampler['name'],
                                                  child_info=json.dumps(sampler), child_thread=sampler['thread_type'])

                    sp.save()
                    # 获取保存后得到的id
                    sampler_id = sp.id
                    for child in sampler_children:
                        sc = SamplersChildren(sampler_id=sampler_id, child_name=child['child_name'],
                                          child_type=child['child_type'], child_info=json.dumps(child))
                        sc.save()
                if csvs_info:
                    for csv in csvs_info:
                        # 保存csv信息
                        c = JmxThreadGroup(jmx_id=jmx_id, child_name=csv['name'], child_type='csv',
                                                   child_info=json.dumps(csv), child_thread=csv['thread_type'])
                        c.save()
                return APIRsp()
            os.remove(jmxpath)
            return APIRsp(code=400, msg='添加失败，参数校验未通过', status=status.HTTP_400_BAD_REQUEST)
        else:
            return APIRsp(code=400, msg='添加失败，未传入文件或用户id', status=status.HTTP_400_BAD_REQUEST)

class JmxCreate(APIView):
    """
    创建jmx
    """
    def post(self, request):

        data = {}
        jmx_name = request.data.get('jmxName')
        sampler_name = request.data.get('samplerName')
        method = request.data.get('method')
        url = request.data.get('url')
        param_type = request.data.get('paramType')
        params = request.data.get('params')
        user = request.data.get('addUser')

        if not sampler_name or not method or not url:
            return APIRsp(code=400, msg='创建jmx失败，接口名称、方法、url必传', status=status.HTTP_400_BAD_REQUEST)

        template_path = settings.JMX_URL + 'template.jmx'

        new_jmxpath = settings.JMX_URL + jmx_name + "." + Tools.random_str(9) + '.jmx'

        shutil.copyfile(template_path, new_jmxpath)
        try:
            ModifyJMX(new_jmxpath).add_sampler(sampler_name, url, method, param_type=param_type, params=params)
        except:
            os.remove(new_jmxpath)
            return APIRsp(code=400, msg='创建jmx失败，参数错误！', status=status.HTTP_400_BAD_REQUEST)

        jmxinfo = ReadJmx(new_jmxpath).analysis_jmx(upload=False)
        if not jmxinfo:
            return APIRsp(code=400, msg='添加失败，jmx文件错误！', status=status.HTTP_400_BAD_REQUEST)

        sampler_info = jmxinfo[0][0]
        thread_info = jmxinfo[2]

        # jmx路径
        data['jmx'] = new_jmxpath

        # jmx名称
        data['jmx_alias'] = jmx_name

        # user的id不存在时，会校验失败
        data['add_user'] = user

        # 线程组基础信息
        data['thread_base_info'] = json.dumps(thread_info)

        obj = JmxsSerializer(data=data)

        # 校验数据格式
        if obj.is_valid():
            obj.save()
            jmx_id = obj.data['id']
            if sampler_info:
                # 保存sampler信息
                del sampler_info['children']
                s = JmxThreadGroup(jmx_id=jmx_id, child_name=sampler_info['name'],
                                              child_info=json.dumps(sampler_info), child_thread=sampler_info['thread_type'])
                s.save()
            return APIRsp(data={'sapmlerId': s.id}) # sampler的id
        os.remove(new_jmxpath)
        return APIRsp(code=400, msg='添加失败，参数校验未通过', status=status.HTTP_400_BAD_REQUEST)

class JmxCreateSamplerHeader(APIView):
    """
    创建sampler的header
    """
    def post(self, request):
        sapmler_id = request.data.get('sapmlerId')
        params = request.data.get('params')
        if not params:
            return APIRsp(msg='头参数为空，不创建头信息')
        elif not isinstance(params, list):
            return APIRsp(code=400, msg='参数应该是一个list')
        try:
            # 获取jmx的信息
            jmxInfo = JmxThreadGroup.objects.all().filter(id=sapmler_id)
            jmx_path = jmxInfo[0].jmx
            sampler_xpath = json.loads(jmxInfo[0].child_info)['xpath']
            ModifyJMX(str(jmx_path)).add_header(sampler_xpath, headers=params)
            return APIRsp()
        except:
            return APIRsp(code=400, msg='创建header失败，参数错误！')

class JmxCreateSamplerRSPAssert(APIView):
    """
    创建sampler的响应断言
    """
    def post(self, request):
        sapmler_id = request.data.get('sapmlerId')
        radioStr = request.data.get('radioStr')
        checkedFalseStr = request.data.get('checkedFalseStr')
        checkedOrStr = request.data.get('checkedOrStr')
        assert_content = request.data.get('assertContent')
        assert_str = radioStr + checkedFalseStr + checkedOrStr
        if not assert_str and not assert_content:
            return APIRsp(msg='断言参数为空，不创建响应断言')
        try:
            # 获取jmx的信息
            jmxInfo = JmxThreadGroup.objects.all().filter(id=sapmler_id)
            jmx_path = jmxInfo[0].jmx
            sampler_xpath = json.loads(jmxInfo[0].child_info)['xpath']
            ModifyJMX(str(jmx_path)).add_rsp_assert(sampler_xpath, assert_str=assert_str, assert_content=assert_content)
            return APIRsp()
        except:
            return APIRsp(code=400, msg='创建响应断言失败，参数错误！')

class JmxCreateUpdateSapmler(APIView):
    """
    创建或修改sampler
    """
    def post(self, request):

        jmx_id = request.POST.get('jmxId')
        # 修改的时候才需要传入childid信息
        child_id = request.POST.get('childId')
        thread_type = request.POST.get('threadType')
        sampler_name = request.POST.get('sapmplerName')
        method = request.POST.get('method')
        url = request.POST.get('url')
        param_type = request.POST.get('paramType')
        params = request.POST.get('params')

        jmx_path = Jmxs.objects.values('jmx').get(id=jmx_id)['jmx']

        if not jmx_path:
            return APIRsp(code=400, msg='无效的jmxID！', status=status.HTTP_400_BAD_REQUEST)

        if child_id:
            # 修改已有sampler
            try:
                child_info = JmxThreadGroup.objects.values('child_info').get(id=child_id, child_type='sampler')['child_info']
                child_xpath = json.loads(child_info)['xpath']
                rst = ModifyJMX(jmx_path).add_sampler(sampler_name, url, method, accord=thread_type,
                                                      param_type=param_type,
                                                      params=params, xpath=child_xpath)
                JmxThreadGroup.objects.filter(id=child_id).update(child_name=sampler_name,
                                          child_info=json.dumps(rst), child_thread=thread_type)
                return APIRsp(msg='修改sampler成功！')
            except:
                return APIRsp(code=400, msg='修改sampler失败，sampler参数有误！', status=status.HTTP_400_BAD_REQUEST)

        else:
            try:
                # 新增sampler
                rst = ModifyJMX(jmx_path).add_sampler(sampler_name, url, method, accord=thread_type, param_type=param_type,
                                                      params=params)
                # 保存sampler信息
                s = JmxThreadGroup(jmx_id=jmx_id, child_name=sampler_name,
                                              child_info=json.dumps(rst), child_thread=thread_type)
                s.save()
                return APIRsp(msg='新增sampler成功！')
            except:
                return APIRsp(code=400, msg='新增sapmler失败，sampler参数有误！', status=status.HTTP_400_BAD_REQUEST)

class JmxDeleteChild(APIView):
    """
    删除sampler或者csv
    """
    def post(self, request, child_id):
        try:
            qs = JmxThreadGroup.objects.get(id=child_id)
            if not qs:
                return APIRsp(code=400, msg='无效的id')
            jmx_path = str(qs.jmx)
            child_info = json.loads(qs.child_info)
            # 删除sampler或者csv
            op = OperateJmx(jmx_path)
            op.remove_node_and_next(child_info['xpath'])
            op.save_change()
            JmxThreadGroup.objects.filter(id=child_id).delete()
            return APIRsp()
        except:
            return APIRsp(code=500, msg='删除失败')

class JmxListView(generics.ListAPIView):
    """
    查询jmx文件
    """
    pagination_class = JmxsPagination
    # 按添加时间降序排序，最近的时间排在最上面
    queryset = Jmxs.objects.all().order_by('-add_time')
    serializer_class = JmxListSerializer
    filter_backends = [filters.SearchFilter]
    # 可以搜索的字段
    search_fields = ['jmx_alias']

    def get(self, request, *args, **kwargs):
        rsp_data = self.list(request, *args, **kwargs)
        if rsp_data.status_code == 200:
            data = rsp_data.data
            del data['next']
            del data['previous']
            return APIRsp(data=rsp_data.data)
        else:
            return APIRsp(code=400, msg='查询失败', status=rsp_data.status_code, data=rsp_data.data)

class JmxView(generics.RetrieveAPIView):
    """
    查询单独某个jmx信息
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxSerializer

    def get(self, request, *args, **kwargs):
        rsp = self.retrieve(request, *args, **kwargs)
        if rsp.status_code == 200:
            if rsp.data:
                id = rsp.data['id']
                children = []
                qs = JmxThreadGroup.objects.values('id', 'child_name', 'child_type', 'child_info').filter(jmx_id=id)
                for q in qs:
                    q['child_info'] = json.loads(q['child_info'])
                    children.append(q)
                rsp.data = {'id': id, 'children': children}
                return APIRsp(data=rsp.data)
            return APIRsp(code='400', msg='无数据', status=rsp.status_code, data=rsp.data)
        else:
            return APIRsp(code='400', msg='无数据', status=rsp.status_code, data=rsp.data)

class JmxDestory(generics.DestroyAPIView):
    """
    删除指定jmx
    """
    queryset = Jmxs.objects.all()
    serializer_class = JmxsRunSerializer

    def delete(self, request, *args, **kwargs):
        try:
            self.destroy(request, *args, **kwargs)
            return APIRsp()
        except:
            return APIRsp(code=404, msg='资源未找到', status=status.HTTP_404_NOT_FOUND)


