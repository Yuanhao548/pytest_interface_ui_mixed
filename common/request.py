import json
import platform
import time

import requests
import json as complexjson

from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

# 配置Chrome无头模式
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")  # 禁用GPU加速（可选）
chrome_options.add_argument("--no-sandbox")  # 在Docker容器中运行时需要此选项
chrome_options.add_argument("--disable-dev-shm-usage")  # 在Linux系统上使用此选项以防止内存不足
chrome_options.add_argument("--disk-cache-size=300000000")  # 设置缓存大小
chrome_options.add_argument("--aggressive-cache-discard=false")  # 禁用激进的缓存清理
chrome_options.add_argument("--disable-extensions")  # 禁用扩展
chrome_options.add_experimental_option("prefs", {
    "profile.managed_default_content_settings.images": 2,  # 禁用图片
    "profile.managed_default_content_settings.media_stream": 2  # 禁用多媒体
})


class RestClient:
    session = requests.session()

    def __init__(self, api_root_url):
        self.api_root_url = api_root_url

    def set_cookie(self, selenium_cookies):
        # 将 Selenium 获取的 cookies 添加到 session
        for cookie in selenium_cookies:
            self.session.cookies.set(cookie['name'], cookie['value'])
        print('转换后的接口cookies：', self.session.cookies)

    def request(self, url, method, headers, json=None, **kwargs):
        url = self.api_root_url + url
        # headers['cookie'] = self.cookie
        # self.session.headers.update(headers)
        content_type = headers['content_type']
        print('self.session.cookies', self.session.cookies)
        if method == "GET":
            return self.session.get(url, verify=False, **kwargs)
        if method == "POST":
            if content_type.__contains__('application/json'):
                return self.session.post(url, json=kwargs['data'], verify=False)
            return self.session.post(url, verify=False, **kwargs)
        if method == "PUT":
            if json:
                # PUT 和 PATCH 中没有提供直接使用json参数的方法，因此需要用data来传入
                data = complexjson.dumps(json)
            return self.session.put(url, verify=False, **kwargs)
        if method == "DELETE":
            return self.session.delete(url, verify=False, **kwargs)
        if method == "PATCH":
            if json:
                data = complexjson.dumps(json)
            return self.session.patch(url, verify=False, **kwargs)


class WebDriver:
    # 配置Selenium WebDriver
    if platform.system() == 'Linux':
        # 指定 chromedriver 的路径
        print("当前环境是linux")
        service = ChromeService(executable_path='/usr/local/bin/chromedriver')
        driver = webdriver.Chrome(service=service, options=chrome_options)  # 请确保已安装ChromeDriver,隐式启动浏览器
    else:
        print("当前环境是mac")
        driver = webdriver.Chrome(options=chrome_options)  # 请确保已安装ChromeDriver,隐式启动浏览器
        # driver = webdriver.Chrome()  # 请确保已安装ChromeDriver,显式启动浏览器

    def __init__(self, login_page, user_name, pass_word):
        self.login_page = login_page
        self.user_name = user_name
        self.pass_word = pass_word

    def login(self):
        # 获取 ChromeDriver 的版本号
        version = self.driver.capabilities['chrome']['chromedriverVersion']
        print(f"ChromeDriver Version: {version}")

        selenium_cookies = None
        self.driver.implicitly_wait(100)
        try:
            # 访问登录页面
            self.driver.get(self.login_page)

            # 使用JavaScript检查页面加载状态
            def is_page_loaded(driver):
                return driver.execute_script("return document.readyState") == "complete"
            # 等待页面加载完成
            WebDriverWait(self.driver, 80).until(is_page_loaded)
            # 切换为普通账号模式
            iframe_element = self.driver.find_element(By.TAG_NAME, "iframe")
            # 通过 WebElement 切换到 iframe
            self.driver.switch_to.frame(iframe_element)
            different_type = self.driver.find_element(By.XPATH, "//*[text()='普通账号登录']")
            different_type.click()
            # 输入用户名和密码
            username_input = self.driver.find_element(By.ID, "namelogin")
            password_input = self.driver.find_element(By.ID, "passwordlogin")
            # 使用 JavaScript 移除事件监听器
            # self.driver.execute_script("""
            #     const input = arguments[0];
            #     input.removeEventListener('input', handleInput);
            # """, username_input)
            username_input.send_keys(self.user_name)
            password_input.send_keys(self.pass_word)
            login_button = self.driver.find_element(By.XPATH, "//div//button[contains(@class, 'submit-button')]")
            # 等待用户输入完成
            def input_is_complete(driver):
                # 假设输入完成的条件是输入框的内容长度大于0
                return len(password_input.get_attribute("value")) > 0
            WebDriverWait(self.driver, 30).until(input_is_complete)
            time.sleep(2)
            login_button.click()
            time.sleep(60)
            selenium_cookies = self.driver.get_cookies()
            print('selenium_cookies: ', selenium_cookies)
        except Exception as e:
                print('web登陆失败：', e)
        finally:
            # 关闭浏览器
            self.driver.quit()
        return selenium_cookies

def web_login(login_page, user_name, pass_word, REQ=None):
    d = WebDriver(login_page=login_page, user_name=user_name, pass_word=pass_word)
    selenium_cookies = d.login()
    REQ.set_cookie(selenium_cookies)

def send_message_to_feishu(webhook_url, message):
    """
    发送消息到飞书群

    :param webhook_url: 飞书机器人的 Webhook 地址
    :param message: 要发送的消息内容
    """
    headers = {
        'Content-Type': 'application/json'
    }

    # 构建消息体
    payload = {
        "msg_type": "text",  # 消息类型，可以是 "text", "post", "image" 等
        "content": {
            "text": message  # 文本消息内容
        }
    }

    # 发送 POST 请求
    response = requests.post(webhook_url, headers=headers, data=json.dumps(payload))

    # 检查响应状态
    if response.status_code == 200:
        print("消息发送成功")
    else:
        print(f"消息发送失败，状态码: {response.status_code}, 响应内容: {response.text}")

if __name__ == '__main__':
    web_login('https://gpark.g2link.cn', 'amssys', '399999')