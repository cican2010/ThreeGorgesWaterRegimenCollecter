import requests
import os
import time,datetime

url = "http://www.ctg.com.cn/eportal/ui"

querystring = {"moduleId":"50c13b5c83554779aad47d71c1d1d8d8","":"","struts.portlet.mode":"view","struts.portlet.action":"/portlet/waterFront!getDatas.action"}

def get_data_by_date(dt):
    payload=dt.strftime("%Y-%m-%d")
    headers = {
        'cookie': "JSESSIONID=694985A069B377839B1249B0D8A9348D",
        'origin': "http://www.ctg.com.cn",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.9,en-US;q=0.8,en;q=0.7,zh-TW;q=0.6",
        'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36",
        'content-type': "application/x-www-form-urlencoded; charset=UTF-8",
        'accept': "application/json, text/javascript, */*; q=0.01",
        'referer': "http://www.ctg.com.cn/sxjt/sqqk/index.html",
        'x-requested-with': "XMLHttpRequest",
        'proxy-connection': "keep-alive",
        'dnt': "1",
        'cache-control': "no-cache",
        'postman-token': "02aa6e6b-0f3d-3759-2500-05dd67899581"
        }
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring)
    return response.json()

if __name__=='__main__':
    # 设置初始时间
    sDate=datetime.date(2003,1,1)
    # 获取当前日期
    eDate=datetime.date.today()
    print("开始时间:"+sDate.strftime("%Y-%m-%d"))
    print("结束时间:"+eDate.strftime("%Y-%m-%d"))
    # 循环获取每天的数据
    while(sDate<=eDate):
        # 抓取数据
        data=get_data_by_date(sDate)
        # 查看数据
        print(data)
        # 存储数据
        sDate=sDate+datetime.timedelta(days = 1)
