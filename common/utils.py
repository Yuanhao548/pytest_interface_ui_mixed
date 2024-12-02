import os
import re
import time
from configparser import ConfigParser
from main import project_path


class Cache:
    cache_dict = dict()

    def set_cache(self, key, value):
        self.cache_dict[key] = value

    def get_cache(self, key):
        return self.cache_dict.get(key, None)

    def get_cache_dict(self):
        return self.cache_dict


class MyConfigParser(ConfigParser):
    # 重写 configparser 中的 optionxform 函数，解决 .ini 文件中的 键option 自动转为小写的问题
    def __init__(self, defaults=None):
        ConfigParser.__init__(self, defaults=defaults)

    def optionxform(self, optionstr):
        return optionstr


def load_ini(file_path):
    config = MyConfigParser()
    config.read(file_path, encoding="utf-8")
    data = dict(config._sections)
    return data


def replace_placeholders(obj, variables, i):
    if isinstance(obj, dict):
        return {k: replace_placeholders(v, variables, i) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_placeholders(item, variables, i) for item in obj]
    elif isinstance(obj, str):
        return re.sub(r'\$\{(.*?)\}', lambda m: str(
            variables.get(m.group(1), m.group(0))) if m.group(1) != 'time' else str(round(time.time())), obj)
    else:
        return obj

def resolve_variable(source, var_dict, i=0):
    resolved_dict = {}
    if source:
        for k, v in source.items():
            new_v = replace_placeholders(v, var_dict, i)
            resolved_dict[k] = new_v
    return resolved_dict
