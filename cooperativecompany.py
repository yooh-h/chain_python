import re
import time

from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openai import APIConnectionError, APIStatusError

from partofproduct import split_news
# 匹配括号中，第一个逗号前的内容
def matchFirstTwoChars(text):
    pattern = re.compile(r'（([^，]+)，.*?）')
    match = pattern.search(text)
    if match:
        return match.group(1)
    else:
        return None

def company_by_news(product,part_of_product, after_news):
    results = []
    i = 1
    for new in after_news:
        print("第" + str(i) + "次抽取新闻：")
        result = one_item_company_by_news(product,part_of_product, new)
        i = i + 1
        for r in result:
            results.append(r)
    results = {
        "result": results
    }
    return results


def one_item_company_by_news(product,part_of_product, new):
    new_list = split_news(new["content"], 500)
    mid_result = []
    results = []
    for n in new_list:
        chat = ChatOpenAI(temperature=0.0)
        template_string = f"""
                根据下列新闻中的内容和构成部件列表，尽可能详细的总结{product}的构成部件的供应商公司名称。
                新闻: {n}
                构成部件列表：{part_of_product}
                以多个三元组的形式输出，三元组格式为：（{product}的构成部件，“相关公司”，供应商公司），例如：（无线充电接收端，“相关公司”，美芯晟）等。
                示例：输入：Mate 60 Pro采用国芯片，此外其中Wifi蓝牙模块、充电IC、显示IC、电源管理IC均为海思自研或国产供应商。输出：（Wifi蓝牙模块，”相关公司“，海思自研）\n（充电IC，”相关公司“，海思自研）\n（显示IC，”相关公司“，海思自研）\n（电源管理IC，”相关公司“，海思自研）。
                """
        prompt_template = ChatPromptTemplate.from_template(template_string)
        prompts = prompt_template.format_messages(
            product=product,
            news=n,
        )
        for i in range(1, 3):
            try:
                response = chat(prompts)
                # print(response)
            except APIConnectionError as e:
                time.sleep(5)
                print("APIConnectionError")
            except APIStatusError as e:
                time.sleep(5)
                print("APIStatusError")
            else:
                break
        if response is None:
            return "调用模型出错，重试"
        response = str(response).replace('content=', '')
        print("大模型根据新闻产生的产品构成有:")
        print(response)
        # 处理返回结果-匹配
        pattern = re.compile(r'（(.*?)）')
        matches = pattern.findall(response)
        for match in matches:
            m=re.search(r'^([^，]+)', match)
            if m:
                first_part = m.group(1)
                if first_part in part_of_product:
                    match = "（" + match + "）"
                    mid_result.append(match)
                else:
                    continue
            else:
                continue

        for item in mid_result:
            # 去除括号和引号，并按逗号分隔
            components = item.strip("（）“”").split("，")
            # 创建字典存储实体信息
            entity = {"name": components[0],
                "cooperativecompany": components[2],
                "source":n,
                "link":new["link"],
                "class":new["class"]}
            results.append(entity)
    return results
