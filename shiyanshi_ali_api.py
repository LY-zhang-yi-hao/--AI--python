import requests
import re
import time
import urllib3
from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import random
from http import HTTPStatus
import dashscope
from dashscope import Generation

# 输入账号信息
url = 'http://59.68.176.173/index.php'
#url = 'https://labexam.hunnu.edu.cn/labexam/index.php'
xuehao = input("学号：")
password = input("密码：")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
response = requests.get(url, verify=False)
html_data = response.text

# 设置Edge驱动路径
edge_driver_path = 'D:/Anacnonda/msedgedriver.exe'

# 创建Service对象，传递驱动路径
service = Service(executable_path=edge_driver_path)

# 初始化Edge浏览器
driver = webdriver.Edge(service=service)


# 访问网址
driver.get(url)

# 等待加载页面中的学号输入框，增加等待时间，确保页面完全加载
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.NAME, 'xuehao'))
)

# 定位学号输入框并输入学号
xuehao_input = driver.find_element(By.NAME, 'xuehao')
xuehao_input.send_keys(xuehao)

# 定位密码输入框并输入密码
password_input = driver.find_element(By.NAME, 'password')
password_input.send_keys(password)
#time.sleep(8)

# 定位确认登录按钮并点击
login_button = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"][value="确认登录"]')
login_button.click()
time.sleep(1)

# 点击“在线考试”
online_practice_button = driver.find_element(By.XPATH, "/html/body/div[2]/div[3]/div[2]/ul/a[1]/li")
online_practice_button.click()

# 等待页面加载
time.sleep(1)
# 点击“同意”
checkbox_element = driver.find_element(By.ID, 'kqcl')
checkbox_element.click()

# 点击“考试”
online_practice_button = driver.find_element(By.XPATH, '//*[@id="article"]/div[4]/div[2]/div/a[2]' )
#理学院//
#online_practice_button = driver.find_element(By.XPATH, '//*[@id="article"]/div[4]/div[2]/div/a' )
#online_practice_button = driver.find_element(By.XPATH, '//*[@id="article"]/div[4]/div[2]/div[1]/a' )
#online_practice_button = driver.find_element(By.XPATH, '//*[@id="article"]/div[4]/div[2]/div[2]/a' )

online_practice_button.click()


# 等待页面加载
time.sleep(1)
            
            

# 定义调用 DashScope API 的类
class DashScopeAPI:
    def __init__(self):
        # 配置API-KEY
        dashscope.api_key = ""
    
    # 单轮对话
    def call_with_messages(self, messages):
        response = Generation.call(
            model="qwen-turbo",
            messages=messages,
            seed=random.randint(1, 10000),  # 设置随机数种子
            result_format='message'
        )
        if response.status_code == HTTPStatus.OK:
            return response.output.choices[0]['message']['content']
        else:
            print('Request id: %s, Status code: %s, error code: %s, error message: %s' % (
                response.request_id, response.status_code,
                response.code, response.message
            ))
            return None

# 实例化API调用类
dsapi = DashScopeAPI()

# 记录无法回答的题目列表
unanswered_questions = []

# 遍历每个页面进行操作
for page_num in range(1, 11):
    # 每次翻页后都要重新获取当前页面的题目
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.shiti h3'))
        )
        questions = driver.find_elements(By.CSS_SELECTOR, 'div.shiti h3')
    except Exception as e:
        print(f"无法获取题目，跳过第 {page_num} 页: {e}")
        continue

    
    # 遍历每个题目，将题目传入 DashScope 模型进行判断，并点击正确选项
    for index, question in enumerate(questions):
        try:
            question_text = question.text
        except Exception as e:
            print(f"无法获取题目文本，跳过该题: {e}")
            continue
        
        # 获取选项文本
        try:
            Choose1_label = driver.find_element(By.XPATH, f"//label[@for='ti_{(page_num-1)*10+index+1}_0']").text
            Choose2_label = driver.find_element(By.XPATH, f"//label[@for='ti_{(page_num-1)*10+index+1}_1']").text
            
            # 尝试获取第三、第四个选项（用于选择题）
            try:
                Choose3_label = driver.find_element(By.XPATH, f"//label[@for='ti_{(page_num-1)*10+index+1}_2']").text
                Choose4_label = driver.find_element(By.XPATH, f"//label[@for='ti_{(page_num-1)*10+index+1}_3']").text
                options_text = f" {Choose1_label}, {Choose2_label}, {Choose3_label}, {Choose4_label}"
            except Exception:
                options_text = f" {Choose1_label}, {Choose2_label}"
        except Exception as e:
            print(f"无法获取选项文本，跳过该题: {e}")
            continue
        
        print(f"\n题目: {question_text}\n选项: {options_text}")
        
        # 调用 DashScope API
        messages = [
            {'role': 'system', 'content': '你是一个知识渊博的化学专业的实验室安全员.'},
            {'role': 'user', 'content': f'给你题目，请你回答，只需要给我答案即可。如果题目没有给你选项，就是判断题，如果给你了选项abcd，就给我答案选项,注意有些是多选题。请你认真作答\n题目: {question_text}\n选项: {options_text}'}
        ]
        
        result = dsapi.call_with_messages(messages)
        
        if result:
            print(f"模型回答: {result}")
        else:
            print(f"模型未返回结果: {question_text}")
            unanswered_questions.append(question_text)
            continue

        # 根据API返回的结果点击正确选项
        try:
            # 提取选项字母部分，去掉描述内容
            result_match = re.match(r'[A-D]|[对错]', result.strip().upper())
            if result_match:
                result_option = result_match.group()
            else:
                raise ValueError("无法识别的选项")
            # 根据返回的选项找到对应的 input 元素并点击
            if result_option == '对':
                correct_option = driver.find_element(By.ID, f'ti_{(page_num-1)*10+index+1}_1')
            elif result_option == '错':
                correct_option = driver.find_element(By.ID, f'ti_{(page_num-1)*10+index+1}_0')
            elif result_option == 'A':
                correct_option = driver.find_element(By.ID, f'ti_{(page_num-1)*10+index+1}_0')
            elif result_option == 'B':
                correct_option = driver.find_element(By.ID, f'ti_{(page_num-1)*10+index+1}_1')
            elif result_option == 'C':
                correct_option = driver.find_element(By.ID, f'ti_{(page_num-1)*10+index+1}_2')
            elif result_option == 'D':
                correct_option = driver.find_element(By.ID, f'ti_{(page_num-1)*10+index+1}_3')
            else:
                raise ValueError("无法识别的选项")
            correct_option.click()
            print(f"点击了'{result_option}'选项")
        except Exception as e:
            print(f"在点击选项时遇到错误: {e}")
            unanswered_questions.append(question_text)
            continue
        

    if page_num < 11:
        # 点击“下一页”按钮
        if page_num == 1:
            next_page_button = driver.find_element(By.XPATH, "//input[@type='button' and @value='下一页']")
            next_page_button.click()
            # next_page_button = driver.find_element(By.XPATH, '//*[@id="dati"]/div[26]/input[1]')
            # next_page_button.click()
        else:
            next_page_button = driver.find_element(By.XPATH, '//*[@id="dati"]/div[11]/input[2]')
            next_page_button.click()    
        print(f"已点击第 {page_num} 页的'下一页'按钮")  

# 输出无法回答的题目
if unanswered_questions:
    print("以下题目未能回答:")
    for unanswered in unanswered_questions:
        print(unanswered)
else:
    print("所有题目都已回答")

# 保持浏览器打开，等待用户按下回车键后关闭
input("Press Enter to close the browser...")
driver.quit()