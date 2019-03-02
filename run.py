import requests,json
import os
import time,datetime
import pymysql
import queue,threading
import xlwt,shutil
import configparser

url = "http://www.ctg.com.cn/eportal/ui"

modelIdList=[
        '50c13b5c83554779aad47d71c1d1d8d8', # 三峡
        '622108b56feb41b5a9d1aa358c52c236', # 葛洲坝
        '3245f9208c304cfb99feb5a66e8a3e45', # 向家坝
        '8a2bf7cbd37c4d4f961ed1a6fbdf1ea8'  # 溪洛渡
        ]
modelNameList=[
    '三峡',
    '葛洲坝',
    '向家坝',
    '溪洛渡'
]

col=['ckList','rkList','syList','xyList']
colAlias={
    'ckList':'outSpeed',
    'rkList':'inSpeed',
    'syList':'upLevel',
    'xyList':'downLevel'
}

cf=configparser.ConfigParser()
cf.read('config.ini',encoding='utf8')

# 用户配置项
excelFileName=cf.get('excel-file','name')
targetDir=cf.get('excel-file','path')
# 初始时间
startDate=cf.get('common','start_date')
startDate=datetime.datetime.strptime(startDate,"%Y-%m-%d").date()
# recent_sync_days
recent_sync_days=int(cf.get('common','recent_sync_days'))

# conn=pymysql.connect(cf.get('mysql-database','host'),cf.get('mysql-database','user'),cf.get('mysql-database','passwd'),cf.get('mysql-database','db'),cf.get('mysql-database','charset'))
conn=pymysql.connect(host=cf.get('mysql-database','host'),user=cf.get('mysql-database','user'),passwd=cf.get('mysql-database','password'),db=cf.get('mysql-database','db'),charset=cf.get('mysql-database','charset'))
cursor=conn.cursor()

thLock=threading.Lock()
dateQueue=queue.Queue()

def get_data_by_date(dt):
    data=[]
    for modelId in modelIdList:
        res=get_water_data_by_id_and_date(modelId,dt)
        if not res:
            return False
        else:
            data.append(res)
    return data

# 检查 json
def check_json(str):
    try:
        json.load(str)
        return True
    except:
        return False

# 根据 modelId 和 date 获取水情信息
def get_water_data_by_id_and_date(modelId,cDate):
    payload='time='+cDate.strftime("%Y-%m-%d")
    headers = {
        #'cookie': "JSESSIONID=694985A069B377839B1249B0D8A9348D",
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
        'cache-control': "no-cache"
        }
    querystring = {"moduleId":modelId,"struts.portlet.mode":"view","struts.portlet.action":"/portlet/waterFront!getDatas.action"}
    response = requests.request("POST", url, data=payload, headers=headers, params=querystring, timeout=2)
    try:
        if(response.status_code!=200 or check_json(response.text)):
            # 查询出错
            return False
        else:
            res=response.json()
            res['modelId']=modelId
            return res
    except Exception as e:
        return False

def update_database(date,data):
    try:
        for site in data:
            # 对于每个站
            for c in col:
                # 对于每个参数
                for t in site[c]:
                    # 对于每个时刻, 更新或插入
                    cursor.execute("SELECT id FROM water_regimen WHERE date='%s' and hour=%d and site='%s'"%(date,int(t['time']),site['senName']))
                    oldRowId=cursor.fetchone()
                    if not oldRowId:
                        # 空, 创建新的
                        cursor.execute("INSERT INTO water_regimen (`date`,`hour`,`site`,`%s`) VALUES ('%s',%d,'%s',%f)"%(colAlias[c],date,int(t['time']),site['senName'],float(t['avgv'])))
                    else:
                        # 已经存在, 更新
                        cursor.execute("UPDATE water_regimen SET %s=%f WHERE id=%d"%(colAlias[c],float(t['avgv']),oldRowId[0]))
        conn.commit()
    except Exception as e:
        return False
def get_all_water_data_by_date_section(startDate,endDate):
    currentDate=startDate
    while(currentDate<=endDate):
        # 获取该天数据
        currentDateData=get_data_by_date(currentDate)
        # 存储数据到 sql 数据库中
        update_database(currentDate.strftime("%Y-%m-%d"),currentDateData)
        # 日期+1
        print(currentDate," 已同步")
        currentDate=currentDate+datetime.timedelta(days=1)
    return True

def database_backup():
    cursor.execute("SHOW TABLES LIKE 'water_regimen'")
    if not cursor.fetchone():
        print("不存在该表")
        return False
    # 复制表
    cursor.execute("CREATE TABLE water_regimen_%s SELECT * FROM water_regimen" % datetime.datetime.today().strftime("%Y%m%d%H%M%S"))
    # 获取最大的日期
    cursor.execute("SELECT max(date) FROM water_regimen")
    row=cursor.fetchone()
    if not row or not row[0]:
        return False
    else:
        return row[0]

def update_excel_file():
    outputFile=xlwt.Workbook()
    # 分站点类型导出为表
    for site in modelNameList:
        # 对于每个站点
        cursor.execute("SELECT date,hour,site,upLevel,downLevel,inSpeed,outSpeed FROM water_regimen WHERE site='%s'"%site)
        fields=cursor.description
        cursor.scroll(0,mode='absolute')
        results=cursor.fetchall()
        # 记录为表
        sheet=outputFile.add_sheet(site)
        # 标题
        for field in range(0,len(fields)):
            sheet.write(0,field,fields[field][0])
        # 添加行
        row = 1
        col = 0
        for row in range(1,len(results)+1):
            for col in range(0,len(fields)):
                sheet.write(row,col,u'%s'%results[row-1][col])
    outputFile.save(excelFileName)
    # 将文件复制到下载目录
    outputFile.save(targetDir+excelFileName)
    # shutil.copy(excelFileName,targetDir)

def loop():
    while True:
        thLock.acquire()
        if dateQueue.empty():
            # 已经完成任务
            thLock.release()
            break
        # 从队列获取日期
        date=dateQueue.get()
        thLock.release()
        # 获取参数
        currentDateData=get_data_by_date(date)
        # 存储数据到 sql 数据库中
        update_database(date.strftime("%Y-%m-%d"),currentDateData)
        print(date," 已同步")

def collectTask():
    print("任务启动:",datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%I"))
    # 设置初始时间
    sDate=startDate
    # 获取当前日期
    eDate=datetime.date.today()
    # 备份数据库, 找到上次备份的日期
    dtLastDate=database_backup()
    if dtLastDate and dtLastDate>sDate:
        # 若数据库有数据
        currentDate=dtLastDate-datetime.timedelta(days=recent_sync_days)
    else:
        # 设置的初始时间
        currentDate=sDate
    print("初始日期:",currentDate)
    # # 创建 dateQueue
    # while currentDate<=eDate:
    #     thLock.acquire()
    #     dateQueue.put(currentDate)
    #     thLock.release()
    #     currentDate=currentDate+datetime.timedelta(days=1)
    # # 创建多线程
    # thList=[]
    # for i in range(1):
    #     t=threading.Thread(target=loop)
    #     t.start()
    #     thList.append(t)
    # for t in thList:
    #     t.join()
    get_all_water_data_by_date_section(sDate,eDate)
    print("任务结束:",datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%I"))
        

if __name__=='__main__':
    # 采集数据
    collectTask()
    # 转为 csv 提供下载
    update_excel_file()
