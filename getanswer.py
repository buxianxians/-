from selenium import webdriver
import time
import re
import jsonpath
import json
from pprint import pprint
from math import *
user  = input("输入账号:")
pwd =  input("输入密码:")
object_name = input("输入课程（完整名字）：")
had_work_y_n = input("是否已经提交过:(y-是)")
work_num = int(input("倒数第几次作业:"))
op = webdriver.ChromeOptions()
# op.add_argument("--headless")
# op.add_argument("--disable-gpu")
op.add_experimental_option("excludeSwitches", ["enable-automation"])
op.add_argument("--user-agent=Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)")
drive = webdriver.Chrome(options=op)
drive.get("https://www.ulearning.cn/portal/index.html#/index/portal")
# 设置等待时间
drive.implicitly_wait(10)
# 登录
login = drive.find_element_by_xpath("/html/body/div[1]/div/div/div[3]/div[1]/div[2]/div[2]/div/div[1]")
login.click()
username = drive.find_element_by_xpath("/html/body/div[3]/div/div/div/div[1]/div[2]/form/div[1]/div[1]/input")
username.send_keys(user)
password = drive.find_element_by_xpath("/html/body/div[3]/div/div/div/div[1]/div[2]/form/div[1]/div[3]/input")
password.send_keys(pwd)
loginbutton = drive.find_element_by_xpath("/html/body/div[3]/div/div/div/div[1]/div[2]/form/button")
loginbutton.click()


# 选择课程
time.sleep(4)
course = drive.find_element_by_xpath(f"//*[text()='{object_name}']") #这里填你的课程
course.click()
time.sleep(2)
work = drive.find_element_by_xpath('/html/body/div[1]/div/div/div[3]/div[1]/div/a[4]')
work.click()


# 进入作业页面
drive.execute_script("window.scrollTo(0,100)")
if had_work_y_n == "y":
    jinrulist = drive.find_elements_by_xpath("/html/body/div[1]/div/div/div[3]/div[2]/div/div/div/div[2]/div[1]/ul//button[text()='查看']")[work_num-1]
else:
    jinrulist = drive.find_elements_by_xpath("/html/body/div[1]/div/div/div[3]/div[2]/div/div/div/div[2]/div[1]/ul//button[text()='写作业']")[work_num-1]

jinrulist.click()
time.sleep(5)
drive.switch_to.window(drive.window_handles[-1])
pagestr = drive.page_source


#正则获取公式
funres = 'correctAnswerAndCorrectReplay = (.*?);'
valres = 'var questionJson = (.*);'
funlist  = re.findall(funres,pagestr)[0]
vallist  = re.findall(valres,pagestr)[0]
vallist = json.loads(vallist)
funlist = json.loads(funlist)
# pprint(vallist)
# print("-------------------")


#数据清理(重新锁定题目)
questionid = jsonpath.jsonpath(vallist,"$..questionid")
fun_dict = {}
val_dict = {}
i = 0
#数据字典化{"id":[formula]}
for id in questionid:
    fun_dict[str(id)] = funlist[str(id)]['correctAnswer']
    val_dict[str(id)] = vallist[i]['formulaVar']
    i+=1

# pprint(fun_dict)
# print("------------------------------")
# pprint(val_dict)


# 公式代换与计算

all_result_list = []
all_formula_list = []
for id in questionid:
    var_list = val_dict[str(id)]
    formula_list = fun_dict[str(id)]
    result_list = []
    formula_one_list = []
    for formula_ in formula_list:
        pre = formula_["precision"]
        pre = int(log(pre, 0.1))
        formula = formula_['formula']
        formula_one_list.append(formula)
        for sub_ in var_list:
            formula = re.sub('\\b' + sub_["name"] + '\\b', str(sub_["value"]), formula)
        formula = re.sub("\^", "**", formula)
        result = round(eval(formula), pre + 1)
        result_list.append(str(result))
    all_formula_list.append(formula_one_list)
    all_result_list.append(result_list)

print(f"公式:{all_formula_list}")
print("===============================================================")
print(f"答案:{all_result_list}")

#自动填入（可选择性开启）
# def put(drive, all_result_list):
#     inputel = drive.find_elements_by_xpath("/html/body/div[4]/div[3]//input[@type='text']")
#     print(len(inputel))
#     input_list = []
#     for i in all_result_list:
#         input_list.extend(i)
#     num = 0
#     for i in inputel:
#         i.send_keys(str(input_list[num]))
#         num+=1
# put(drive, all_result_list)





