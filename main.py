# This is a sample Python script.
import os.path
import pathlib
import re
import sys
import time
from datetime import datetime

import pytest
import xml.etree.ElementTree as ET
from common.generate_cases_file import generate_case
from common.request import send_message_to_feishu

# from common.generate_cases_file import generate_case

project_path = pathlib.Path(__file__).parents[0].resolve()
feishu_hook_url = 'https://open.feishu.cn/open-apis/bot/v2/hook/c8ea4ee8-d1ce-4d09-b95c-865cfc3d2aae'

# Press the green button in the gutter to run the script.
def parse_test_results(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    skipped_tests = 0
    failed_tests_info = []

    for testsuite in root.findall('testsuite'):
        total_num = eval(testsuite.get('tests', '0'))
        failed_num = eval(testsuite.get('failures', '0'))
        skipped_num = eval(testsuite.get('skipped', '0'))
        error_num = eval(testsuite.get('errors', '0'))
        passed_num = total_num - failed_num - skipped_num - error_num
        total_tests += total_num
        failed_tests += failed_num
        skipped_tests += skipped_num
        passed_tests += passed_num
        for testcase in testsuite.findall('testcase'):
            for failure in testcase.findall('failure'):
                # 获取元素的文本内容
                failure_text = failure.text
                failure_info = re.search('@allure\.title\("(.*?)"\)', failure_text, re.S)
                failed_tests_info.append(failure_info.group(1))
    return {
        'total_tests': total_tests,
        'passed_tests': passed_tests,
        'failed_tests': failed_tests,
        'skipped_tests': skipped_tests,
        'failed_tests_info': [str(i+1) + '、' + v + ';\n' for i, v in enumerate(failed_tests_info)]
    }

def main():
    generate_case(project_path)
    # 注册自定义的 hook
    result_path = os.path.join(project_path, 'run_result', f'{datetime.now().date()}test_output.txt')
    with open(result_path, 'w') as f:
        # 重定向标准输出和标准错误
        sys.stdout = f
        sys.stderr = f
        # 运行测试
        pytest.main(['-s', '-v', 'testCases/', '--tb=long', '--junit-xml=test_results.xml'])
        # pytest.main(['-s', '-v', '--reruns', '3', 'testCases/'])
    results = parse_test_results('test_results.xml')
    result_message = "自动化测试结果:\n" \
                     f"总测试数: {results['total_tests']}\n" \
                     f"通过: {results['passed_tests']}\n" \
                     f"失败: {results['failed_tests']}\n" \
                     f"跳过: {results['skipped_tests']}\n" \
                     f"\n失败用例详情：\n{''.join(results['failed_tests_info'])}" if results['failed_tests_info'] else "自动化测试结果:\n" \
                                                                                                                      f"总测试数: {results['total_tests']}\n" \
                                                                                                                      f"通过: {results['passed_tests']}\n" \
                                                                                                                      f"失败: {results['failed_tests']}\n" \
                                                                                                                      f"跳过: {results['skipped_tests']}"
    send_message_to_feishu(feishu_hook_url, result_message)
    # 恢复标准输出和标准错误
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__


if __name__ == '__main__':
    main()