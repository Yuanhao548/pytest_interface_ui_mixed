import os

import pytest
from common.utils import Cache, load_ini
from common.request import RestClient, web_login
from main import project_path

cache = Cache()
setting_ini = load_ini(os.path.join(project_path, 'setting.ini'))
domin_name = setting_ini['host']['domin_name']
user_name = setting_ini['host']['user_name']
pass_word = setting_ini['host']['pass_word']
req = RestClient(domin_name)


@pytest.fixture(scope='session', autouse=True)
def session_fixture():
    web_login(domin_name, user_name, pass_word, req)
    yield
    print('执行后的存储数据为：', cache.get_cache_dict())

@pytest.fixture(scope='function')
def sample_fixture():
    yield req, cache
    if cache.get_cache('response_status_code') == 401:
        web_login(domin_name, user_name, pass_word, req)
    else:
        pass


def pytest_addoption(parser):
    parser.addoption("--myopt", action="store_true", help="Enable some specific feature")

@pytest.fixture
def myopt(request):
    return request.config.getoption("--myopt")