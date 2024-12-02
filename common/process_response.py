import re


def get_json_value_by_path(data, path):
    """
    根据点路径获取 JSON 对象中的值，支持数组索引。

    :param data: JSON 对象
    :param path: 点路径字符串，例如 "user.addresses[0].street"
    :return: 路径对应的值，如果路径不存在则返回 None
    """
    keys = path.split('.')
    current = data
    for key in keys:
        if '[' in key and ']' in key:
            # 处理数组索引
            match = re.match(r"(\w+)\[(\d+)\]", key)
            if match:
                key, index = match.groups()
                index = int(index)
                if isinstance(current, dict) and key in current and isinstance(
                        current[key], list) and index < len(current[key]):
                    current = current[key][index]
                else:
                    return None
            else:
                return None
        elif isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return None
    return current

def assert_func(r_data, t_data):
    t_data, r_data = str(t_data), str(r_data)
    if not t_data.startswith('${'):
        return bool(r_data == t_data)
    t_label = re.search('(\$\{.*?\})', t_data).group(1)
    t_data = t_data.lstrip(t_label)
    if t_label == '${>}' and isinstance(eval(t_data), (int, float)):
        return bool(float(t_data) > float(r_data))
    elif t_label == '${<}' and isinstance(eval(t_data), (int, float)):
        return bool(float(t_data) < float(r_data))
    elif t_label == '${!}' or t_label == '${！}':
        return bool(t_data != r_data)
    elif t_label == '${in}':
        return bool(t_data in r_data)
    else:
        raise AssertionError('期望数据格式有误！')

