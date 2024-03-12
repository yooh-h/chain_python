import os
import json
from datetime import time
from langchain_community.chat_models import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from openai import APIConnectionError

from partofproduct import split_news

os.environ["OPENAI_API_BASE"] = 'https://oneapi.xty.app/v1'
#3.5
#os.environ["OPENAI_API_KEY"] = 'sk-VEDbE0OfLniuK7eJEb7067B883944d57B1Dc2a638f8f7bBb'
#4
os.environ["OPENAI_API_KEY"] ='sk-SS3E9A82RI9P3rUg51E24031001949D59dBa51E0CeB6D3Fb'





def process(product,news_list):
    chat = ChatOpenAI(temperature=0.0)
    for n in news_list:
        result = ""
        news = split_news(n["content"], 400)
        for new in news:
            template_string = f"""
                            请你对文章进行预处理，保留和{product}相关的原文,去除不相关信息。
                            文章：{new}
                        """
            prompt_template = ChatPromptTemplate.from_template(template_string)
            prompts = prompt_template.format_messages(
                product=product,
                new=new
            )
            print(prompts)
            for i in range(1, 3):
                try:
                    response = chat(prompts)
                    print(response)
                except APIConnectionError as e:
                    time.sleep(10)
                    continue
                else:
                    break
            response = str(response)
            response = response.replace("content=\'", "")
            result = result + response
            result = result.replace("content=\'", "")
        n["content"]=result
    # 处理后的新闻
    print("处理后的新闻")
    print(news_list)
    # 定义一个Python字典
    return news_list