import pymysql

IP = "39.101.141.53"
MYSQLPWD = 'neumyb415sql'
DB = 'dps_target'


def product_by_sql(product_name):
    conn = pymysql.connect(host=IP, user='root', passwd=MYSQLPWD, db=DB)
    cursor = conn.cursor()
    sql = "SELECT related_product FROM `industry_chain_relation`where relationship=-1 and primary_name =%s"
    cursor.execute(sql, product_name)
    res = cursor.fetchall()
    sql_product = []
    for row in res:
        part = {"name": row[0], "source": "", "link": "", "class": "F10数据库"}
        sql_product.append(part)
    results = {
        "result": sql_product
    }
    print(res)
    conn.commit()
    cursor.close()
    conn.close()
    return results
