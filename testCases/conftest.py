import os

import pytest
from common.utils import Cache, load_ini
from common.request import RestClient, web_login
from main import project_path

cache = Cache()
req_dict = dict()
request_infos_dict = dict()
setting_ini = load_ini(os.path.join(project_path, 'setting.ini'))
for k, v in setting_ini.items():
    rc = RestClient(v['domin_name'])
    request_infos_dict[k] = [v['domin_name'], v['user_name'], v['pass_word'], rc]
    req_dict[k] = rc

@pytest.fixture(scope='session', autouse=True)
def session_fixture():
    for v in request_infos_dict.values():
        web_login(v[0], v[1], v[2], v[3])
    yield
    print('执行后的存储数据为：', cache.get_cache_dict())

@pytest.fixture(scope='function')
def sample_fixture():
    yield req_dict, cache
    if cache.get_cache('response_status_code') == 401:
        request_info = request_infos_dict[cache.get_cache('project')]
        web_login(request_info[0], request_info[1], request_info[2], request_info[3])
    else:
        pass


def pytest_addoption(parser):
    parser.addoption("--myopt", action="store_true", help="Enable some specific feature")

@pytest.fixture
def myopt(request):
    return request.config.getoption("--myopt")