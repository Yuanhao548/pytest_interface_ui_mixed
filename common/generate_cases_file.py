import os
import shutil

import yaml

def read_yaml_data(path):
    with open(path, mode='r', encoding='utf-8') as file:
        config = yaml.safe_load(file)
    return config

def del_cases_dir(directory_path):
    # 检查目录是否存在
    if os.path.exists(directory_path):
        for item in os.listdir(directory_path):
            item_path = os.path.join(directory_path, item)
            if os.path.isdir(item_path):
                # 递归删除子目录及其所有内容
                shutil.rmtree(item_path)
                print(f"子目录 {item_path} 及其所有测试用例已成功删除。")
    else:
        print(f"目录 {directory_path} 不存在。")

def generate_case(project_path):
    data_dir= os.path.join(project_path, 'data')
    case_dir = os.path.join(project_path, 'testCases')
    del_cases_dir(case_dir)
    try:
        for root, dirs, files in os.walk(data_dir):
            # 计算相对路径
            relative_path = os.path.relpath(root, data_dir)
            # 构建目标目录路径并创建__init__文件
            dest_subdir = os.path.join(case_dir, relative_path)
            if not os.path.exists(dest_subdir):
                os.mkdir(dest_subdir)
                init_file_path = os.path.join(dest_subdir, '__init__.py')
                with open(init_file_path, mode='w', encoding='utf-8') as wi:
                    wi.write('')
            for mode_i, file in enumerate(files):
                mode_i += 1
                src_file = os.path.join(root, file)
                dest_file = os.path.join(dest_subdir, file)
                yaml_data = read_yaml_data(src_file)
                module_info = yaml_data.get('module_info', None)
                module_name = eval(module_info.get('module_name', None)) + '.py'
                case_infos = module_info.get('case_infos', None)
                if not case_infos:
                    raise Exception('测试数据格式有误')
                cases_file_info = '''
import allure
import pytest
from common.utils import resolve_variable
from common.process_response import get_json_value_by_path, assert_func

'''
                for case_i, case_info in enumerate(case_infos):
                    case_i += 1
                    info = f'''
@allure.story("{case_info['allure_info']['story']}")
@allure.description("{case_info['allure_info']['description']}")
@allure.title("{case_info['allure_info']['title']}")
@pytest.mark.parametrize("api,method,request_data,assert_data,headers,store_var", [("{case_info['api']}","{case_info['method']}",{case_info['request_data']},{case_info['assert_data']},{case_info['headers']},{case_info['store_var']})])
def test_case_{case_i}(sample_fixture, api, method, request_data, assert_data, headers, store_var):
    print('开始执行测试用例')
    req, cache = sample_fixture
    cache_dict = cache.get_cache_dict()
    # 遍历替换参数中的变量
    variables = ''' + '''{'api': api, 'request_data': request_data}
    resolved_request_info = resolve_variable(variables, cache_dict)
    api, request_data = resolved_request_info['api'], resolved_request_info['request_data']
    response = req.request(url=api, method=method, data=request_data, headers=headers)
    cache.set_cache('response_status_code', response.status_code)
    print(response.status_code)
    response_data = response.json()
    assert response.status_code == 200
    # 断言
    for ass_i, ass_v in assert_data.items():
        current_value = get_json_value_by_path(response_data, ass_i)
        try:
            assert assert_func(current_value, ass_v)
        except AssertionError as e:
            print(e)
    # 处理需要保存的变量
    for store_i, store_v in store_var.items():
        current_value = get_json_value_by_path(response_data, store_v)
        cache.set_cache(store_i, current_value)

'''
                    cases_file_info += info
                case_file_path = os.path.join(dest_subdir, module_name)
                with open(case_file_path, mode='w', encoding='utf8') as w:
                    w.write(cases_file_info)
    except FileNotFoundError as e:
        print(e)
    except Exception as e:
        print(e)
