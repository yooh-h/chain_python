import datetime

from serpapi import GoogleSearch
import requests
from langchain.document_loaders import UnstructuredHTMLLoader
import re

def remove_after_substring(input_string, substring):
    # 查找子串的位置
    index = input_string.find(substring)
    # 如果找到了子串
    if index != -1:
        # 截取子串之前的部分
        result = input_string[:index]
        return result
    else:
        # 如果子串不存在，则返回原始字符串
        return input_string


def extract_alphanumeric(input_str):
    # 使用正则表达式匹配中文、英文、数字等字符
    pattern = re.compile(r'[\u4e00-\u9fa5a-zA-Z0-9]+')
    result = pattern.findall(input_str)
    # 将匹配到的字符列表连接成一个字符串
    output_str = ''.join(result)
    return output_str


def download_product_news(product, queryList, linknums):

    # 替换为你的API密钥
    api_key = '746a288e9f392d1e883afd5527eddfb0407f62bf0766ee70c1dba0b3dde901c5'
    download_result = []

    # 谷歌API获取网页地址
    # 查询数组
    for query in queryList:
        # 设置搜索参数
        params = {
            'api_key': api_key,
            'q': product+"的"+query,
            # 下载数量
            'num': 15
        }
        print(params)
        # 执行搜索
        search = GoogleSearch(params)
        results = search.get_dict()

        # 处理搜索结果
        for result in results['organic_results']:
            download = {"link": "", "date": "", "title": "","content":"","class":""}
            print(result['title'])
            print(result['link'])
            if (result['link'].endswith('.html')):
                if len(download_result) >= linknums+2:
                    break
                download['link'] = result['link']
                try:
                    download['date'] = datetime.datetime.strptime(result['date'], "%b %d, %Y").strftime("%Y年%m月%d日")
                    # .strptime(result['date'], "%b %d, %Y")
                except KeyError:
                    download['date']=""

                download["title"] = result["title"]
                download["class"]="GoogleAPI新闻"
                download_result.append(download)

        if len(download_result) >= linknums+2:
            break
    print("谷歌搜索得到的网址：")
    print(download_result)

    # 解析网页内容并保存
    for i in range(0, len(download_result)):

        header = {
            "User-Agent": "Mozilla / 5.0(Windows NT 10.0; Win64; x64) AppleWebKit / 537.36(KHTML, like Gecko) Chrome / 120.0.0.0 Safari / 537.36"
        }
        for j in range(1, 3):
            try:
                response = requests.get(download_result[i]["link"], headers=header)
                response.encoding = "utf-8"
                if response.status_code == 200:
                    # 成功获取页面内容
                    html_content = response.text
                    if response.text=='':
                        break
                    htmlSavePath = "HTMLPage\\" + product + str(i)+".html"
                    # 将页面内容保存到本地文件
                    with open(htmlSavePath, "w", encoding="utf-8") as file:
                        file.write(html_content)
                    print("页面已成功下载到本地文件" + htmlSavePath)
                    loader = UnstructuredHTMLLoader(htmlSavePath)
                    docs = loader.load()

                    filecontent = str(docs[0])
                    downloadcontent = remove_after_substring(filecontent, "metadata={").replace("page_content=", "") \
                        .replace("\\n", "").replace("\\t", "").replace("\\r", "").replace("\\",'')
                    download_result[i]["content"] = downloadcontent.replace(' ','')


            except requests.exceptions.RequestException as e:
                # 捕获异常，并打印错误信息
                print("Error:", e)
                break
            else:
                break
    result=[]
    for i in download_result:
        if i['content']!='':
            result.append(i)
    print(result)
    return result


