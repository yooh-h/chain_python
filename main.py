import json

from flask import Flask, request
from flask_cors import CORS
from F10SqlQuery import product_by_sql
from cooperativecompany import company_by_news
from download_news import  download_product_news
from partofproduct import  product_by_model, product_by_news
from processnews import process

app=Flask(__name__)



CORS(app,resource=r'/*')

@app.route('/downloadnews',methods=['POST'])
def download_news():
    register_dict = request.json
    product = register_dict['product']
    queryList=register_dict['queryList']
    linknums = register_dict['linknums']
    news=download_product_news(product,queryList,linknums)
    return news

@app.route('/processnews',methods=['POST'])
def process_news():
    register_dict = request.json
    product = register_dict['product']
    news_list = register_dict['newsList']
    after_news=process(product, news_list)
    return  after_news


@app.route('/partofbymodel',methods=['POST'])
def part_of_product_model():
    register_dict = request.json
    product = register_dict['product']
    product_class = register_dict['productClass']
    partofproduct_by_model=product_by_model(product,product_class)
    return partofproduct_by_model


@app.route('/partofbynews',methods=['POST'])
def part_of_product_news():
    register_dict = request.json
    product = register_dict['product']
    after_news = register_dict['afterNews']
    partofproduct_by_news=product_by_news(product,after_news)
    return partofproduct_by_news



@app.route('/partofbyF10',methods=['POST'])
def summary():
    register_dict = request.json
    product_class = register_dict['productClass']
    partofproduct_by_sql=product_by_sql(product_class)
    return partofproduct_by_sql


@app.route('/summary',methods=['POST'])
def part_of_product_summary():
    register_dict = request.json
    partofproduct_by_model = register_dict['partbymodel']
    partofproduct_by_news = register_dict['partbynews']
    partofproduct_by_sql = register_dict['partbysql']
    result=[]
    for m in partofproduct_by_model:
        result.append(m)
    for n in partofproduct_by_news:
        result.append(n)
    for s in partofproduct_by_sql:
        result.append(s)
    unique_data = []
    seen_names = set()
    #使用集合去重
    for item in result:
        name = item['name']
        if name not in seen_names:
            unique_data.append(item)
            seen_names.add(name)
    results = {
        "result": unique_data
    }
    return results

@app.route('/cooperativecompany',methods=['POST'])
def cooperative_company():
    register_dict = request.json
    part = register_dict['partofproduct']
    product = register_dict['product']
    after_news = register_dict['afternews']
    part_of_product= [item["name"] for item in part]
    comperative_company_list = company_by_news(product,part_of_product, after_news)
    return comperative_company_list

if __name__=="__main__":
    # app.run(port=2000, host="127.0.0.1", debug=True)
    app.run(port=9999,host="0.0.0.0",debug=True)
