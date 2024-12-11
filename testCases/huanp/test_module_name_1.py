
import allure
import pytest
from common.utils import resolve_variable
from common.process_response import get_json_value_by_path, assert_func


@allure.story("西安园区IOC")
@allure.description("查看IOC昨日用电量")
@allure.title("西安环普园区IOC园区管理的昨日租户用电量与平时用电量相差过大")
@pytest.mark.parametrize("api,method,request_data,assert_data,headers,store_var,project", [("/ipark-ioc/electric/tenant/statistics","POST",{'parkCode': '23018'},{'success': True, 'result.yesterdayTenantElectricQuantity': '${>}10000'},{'content_type': 'application/json;charset=UTF-8'},{},"huanp")])
def test_case_1(sample_fixture, api, method, request_data, assert_data, headers, store_var, project):
    print('开始执行测试用例')
    req_dict, cache = sample_fixture
    cache_dict = cache.get_cache_dict()
    # 遍历替换参数中的变量
    variables = {'api': api, 'request_data': request_data}
    resolved_request_info = resolve_variable(variables, cache_dict)
    api, request_data = resolved_request_info['api'], resolved_request_info['request_data']
    req = req_dict[project]
    response = req.request(url=api, method=method, data=request_data, headers=headers)
    cache.set_cache('response_status_code', response.status_code)
    cache.set_cache('project', project)
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


@allure.story("西安园区IOC")
@allure.description("查看IOC今日车辆")
@allure.title("西安环普园区IOC园区运营中的今日车辆进、出、在园数量和以往相比相差过大")
@pytest.mark.parametrize("api,method,request_data,assert_data,headers,store_var,project", [("/ipark-ioc/inout/vehicleNumber","POST",{'parkCode': '23018'},{'success': None, 'result.enterParkVehicleNumber': '${>}100', 'result.inParkVehicleNumber': '${>}100', 'result.leaveParkVehicleNumber': '${>}100'},{'content_type': 'application/json;charset=UTF-8'},{},"huanp")])
def test_case_2(sample_fixture, api, method, request_data, assert_data, headers, store_var, project):
    print('开始执行测试用例')
    req_dict, cache = sample_fixture
    cache_dict = cache.get_cache_dict()
    # 遍历替换参数中的变量
    variables = {'api': api, 'request_data': request_data}
    resolved_request_info = resolve_variable(variables, cache_dict)
    api, request_data = resolved_request_info['api'], resolved_request_info['request_data']
    req = req_dict[project]
    response = req.request(url=api, method=method, data=request_data, headers=headers)
    cache.set_cache('response_status_code', response.status_code)
    cache.set_cache('project', project)
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

