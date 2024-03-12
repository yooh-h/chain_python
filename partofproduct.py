from datetime import time
import re

import os
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openai import APIConnectionError, APIStatusError

os.environ["OPENAI_API_BASE"] = 'https://oneapi.xty.app/v1'
#3.5
#os.environ["OPENAI_API_KEY"] = 'sk-VEDbE0OfLniuK7eJEb7067B883944d57B1Dc2a638f8f7bBb'
#4
os.environ["OPENAI_API_KEY"] ='sk-SS3E9A82RI9P3rUg51E24031001949D59dBa51E0CeB6D3Fb'

def split_news(news, max_chars_per_sentence=300):
    sentences = news.split('。')
    resultlist = []
    current_sentence = sentences[0]
    for sentence in sentences[1:]:
        if len(current_sentence) + len(sentence) + 1 <= max_chars_per_sentence:
            current_sentence += sentence + '。'
        else:
            resultlist.append(current_sentence)
            current_sentence = sentence
        # 处理最后一个句子
    if current_sentence:
        resultlist.append(current_sentence)
    return resultlist


def product_by_model(product, productClass):

    chat = ChatOpenAI(temperature=0.0)
    template_string = """
        已知{product}是一种{product_class}，请尽可能输出{product}最重要的产品构成部件。
        输出格式：产品构成：构成部件1、构成部件2、构成部件3。
        例如：产品构成：屏幕、处理器、芯片。
        """
    prompt_template = ChatPromptTemplate.from_template(template_string)
    prompts = prompt_template.format_messages(
        product=product,
        product_class=productClass
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
    if response == None:
        return "调用模型出错，重试"
    response = str(response).replace('content=', '')
    print("大模型根据自身知识产生的产品构成有:")
    print(response)
    # 处理返回结果
    response = response.replace("'产品构成：", "")
    response = response.replace("。'", "")
    response = response.replace("等'", "")
    mid_result = [comp.strip() for comp in response.split("、")]
    mid_result = list(set(mid_result))
    result=[]
    for m in mid_result:
        part = {"name": m, "source": "", "link": "","class":"LLM内在知识"}
        result.append(part)
    print(result)
    result = {
        "result": result
    }
    return result


def product_by_news(product, after_news):
    results = []
    i=1
    for new in after_news:
        print("第" + str(i) + "次抽取新闻：")
        result = one_item_product_by_news(product, new)
        i = i + 1
        for r in result:
            results.append(r)
    results = {
        "result": results
    }
    return results


def one_item_product_by_news(product, new):
    new_list = split_news(new["content"], 500)
    results=[]
    for n in new_list:
        chat = ChatOpenAI(temperature=0.0)
        template_string = f"""
            根据下列新闻中的内容，尽可能详细的抽取新闻中提到的 {product}的重要的产品构成部件, 包括软件、硬件等，并按照下列格式输出结果。
            格式：产品构成：构成部件1、构成部件2、构成部件3。
            示例：输入：小米SU7搭载了1颗激光雷达、11颗高清摄像头、3颗毫米波雷达和12颗超声波雷达，搭载了2颗英伟达DRIVE Orin芯片。输出：产品构成：激光雷达、高清摄像头、毫米波雷达、超声波雷达、英伟达DRIVE Orin芯片。
            新闻: {n}
            """
        # 三元组格式为：（产品部件，“构成”，{product}），
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
        # 处理返回结果
        response = response.replace("'产品构成：", "")
        response = response.replace("。'", "")
        mid_result = [comp.strip() for comp in response.split("、")]
        mid_result = list(set(mid_result))
        print(mid_result)
        result=[]
        for r in mid_result:
            if len(r) > 20:
                continue
            result.append(r)
        for m in result:
            part = {"name": m, "source": n, "link": new["link"],"class":new["class"]}
            results.append(part)
    return results
