
import allure
import pytest
from common.utils import resolve_variable
from common.process_response import get_json_value_by_path, assert_func


@allure.story("园区IOC")
@allure.description("查看IOC出入园")
@allure.title("宝山园区IOC出入园看板当日出入园为0")
@pytest.mark.parametrize("api,method,request_data,assert_data,headers,store_var,project", [("/s-park/statistics/api/vehicle/getTodayInout","POST",{'parkExternalId': '529'},{'success': True, 'result.enterParkVehicleNumber.total': '${>}0', 'result.inParkVehicleNumber.total': '${>}0', 'result.leaveParkVehicleNumber.total': '${>}0'},{'content_type': 'application/json;charset=UTF-8'},{},"asp")])
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


@allure.story("园区IOC")
@allure.description("查看IOC能耗")
@allure.title("宝山园区IOC能耗看板当日用电量为0")
@pytest.mark.parametrize("api,method,request_data,assert_data,headers,store_var,project", [("/statistics/iocLargeScreen/electricData","POST",{'parkExternalId': '529', 'isUseJoinCal': 0, 'meterCodeList': ['21088001959', '21088001958', '21088001963', '21088001964', '21088001966', '21088001967', '21088001970', '21088001971', '21088002270', '21088002271']},{'success': True, 'result.todayUse': '${>}0'},{'content_type': 'application/json;charset=UTF-8'},{},"asp")])
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

