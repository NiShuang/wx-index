# -*- coding: UTF-8 -*-

import sys
import json

import datetime
import MySQLdb
import config
reload(sys)
sys.setdefaultencoding('utf-8')

import requests


query_str = ''
for item in config.query_list:
    query_str += item + ';'
if len(query_str) > 0:
    query_str = query_str[:-1]

headers = {
    'charset': 'utf-8',
    'accept-Encoding': 'gzip',
    'referer': 'https://servicewechat.com/wxc026e7662ec26a3a/4/page-frame.html',
    'content-type': 'application/json',
    'user-agent': 'Mozilla/5.0 (Linux; Android 8.1.0; MI 8 Build/OPM1.171019.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/62.0.3202.84 Mobile Safari/537.36 MicroMessenger/6.7.2.1340(0x26070237) NetType/4G Language/zh_CN',
    'host': 'search.weixin.qq.com',
    'connection': 'Keep-Alive'
}
data = {
    'group_query_list': query_str,
    'wxindex_query_list': query_str,
    'gid': '',
    'openid': config.openid,
    'search_key': config.search_key
}

url = 'https://search.weixin.qq.com/cgi-bin/searchweb/wxindex/querywxindexgroup'
resp = requests.get(url, params=data, headers=headers)

wx_index_group = json.loads(resp)['data']['group_wxindex']
result = []
today = datetime.datetime.today()
for item in wx_index_group:
    key = item['query']
    wx_index_str = item['wxindex_str']
    index_group = str(wx_index_str).split(',')
    range = len(index_group)
    for index, value in enumerate(index_group):
        date = (today - datetime.timedelta(days=(range - index))).strftime('%Y-%m-%d')
        temp = {
            'platform': '微信指数',
            'key': key,
            'date': date,
            'value': int(value)
        }
        result.append(temp)
print json.dumps(result)

database_config = config.database
db = MySQLdb.connect(
    host=database_config['host'],
    port=database_config['port'],
    user=database_config['user'],
    passwd=database_config['passwd'],
    db=database_config['db'],
    charset=database_config['charset']
)

# 使用cursor()方法获取操作游标
cursor = db.cursor()

for record in result:
    sql1 = "DELETE FROM web_index_record WHERE platform = '%s' AND `key` = '%s' AND `date` = '%s'" % \
          (record['platform'], record['key'], record['date'])
    sql2 = "INSERT INTO web_index_record(platform,`key`, `date`, `value`) VALUES ('%s', '%s', '%s', %d)" % \
           (record['platform'], record['key'], record['date'], record['value'])
    try:
        # 执行SQL语句
        cursor.execute(sql1)
        cursor.execute(sql2)
        # 提交修改
        db.commit()
    except:
        # 发生错误时回滚
        db.rollback()

cursor.close()
# 关闭数据库连接
db.close()


