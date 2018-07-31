#!/usr/bin/env python
# coding:utf-8

import MySQLdb
import redis
import requests, json
from apscheduler.schedulers.blocking import BlockingScheduler

class in_redis(object):
    url = "http://www.xdaili.cn/ipagent//privateProxy/getDynamicIP/DD20175100029Lx94Th/36f4fe52f79211e6942200163e1a31c0?returnType=2"
    def dbInit(self):
        self.conn = MySQLdb.connect(host="192.168.20.40", user="root", passwd="root", port=3306, db="poi", charset='utf8')
        self.cursor = self.conn.cursor()
        self.cursor.execute("set names utf8")
        print "Init MYSQL"

    def dbClose(self):
        print "Close MYSQL"
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def inRedis(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        self.dbInit()
        sql = "select URL from amap_POI where State=0 limit 10000"
        query = self.cursor.execute(sql)
        if query:
            rows = self.cursor.fetchall()
            for row in rows:
                url = row[0]
                _db.rpush("get_poi_position:start_urls", url)
        self.dbClose()

    def readRedis(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        #url = _db.rpop("get_poi_position:start_urls")
        i = 0
        while i<50:
            i+=1
            url = _db.rpop("redis:proxy_ip")
            print url
        print i

    def delectRedis(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        if 'in_redis:ip' in _db.keys():
            _db.delete('in_redis:ip')

    def ip_in_redis(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        r = requests.get(url = self.url)
        ip_json = json.loads(r.text)
        port = ip_json["RESULT"].get("proxyport")
        ip = ip_json["RESULT"].get("wanIp")
        proxy_ip = 'http://%s:%s' % (ip, port)
        _db.rpush("in_redis:ip", proxy_ip)
        #self.db.rpush("in_redis:ip", proxy_ip)  # 存入新的ip
        _db.ltrim("in_redis:ip", 1, 1)

    def get_ip(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        proxy_ip = _db.lindex("in_redis:ip", 0)
        print proxy_ip

    def update_ip(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        _db.lset("in_redis:ip", 0, "{afakgksHGK}")

    def ipportpool(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        ip_port = [["111.1.3.34", 8000, 10], ["121.8.98.201", 80, 9], ["60.211.209.79", 8080, 9], ["111.56.7.8", 80, 8], ["111.56.7.8", 8080, 8], ["111.56.7.9", 8080, 8], ["111.56.7.6", 80, 7], ["111.23.10.51", 80, 7], ["111.56.7.7", 80, 6], ["111.23.10.40", 80, 6], ["111.23.10.23", 80, 6], ["111.23.10.54", 80, 6], ["111.23.10.37", 80, 6], ["111.8.22.213", 80, 6], ["221.14.7.241", 8080, 6], ["121.8.98.201", 81, 6], ["115.231.128.81", 8080, 6], ["60.211.182.76", 8080, 6], ["202.97.207.147", 8080, 6], ["120.52.72.58", 80, 5], ["120.52.72.59", 80, 5], ["121.8.98.202", 9999, 5], ["111.23.10.44", 80, 5], ["120.52.72.54", 80, 5], ["111.23.10.28", 80, 5], ["60.21.206.165", 9999, 5], ["1.30.130.60", 8080, 5], ["111.56.7.9", 80, 4], ["60.169.19.66", 9000, 4], ["111.23.10.22", 80, 4], ["111.23.10.112", 8088, 4], ["125.88.74.122", 85, 4], ["183.131.215.107", 8080, 4], ["111.56.7.4", 80, 3], ["111.23.10.46", 80, 3], ["110.88.223.177", 8080, 3], ["125.88.74.122", 84, 3], ["114.55.156.225", 80, 3], ["58.242.248.5", 80, 2], ["111.8.22.207", 80, 2], ["110.84.228.244", 80, 2], ["125.67.239.82", 8080, 2], ["125.88.74.122", 81, 2], ["120.52.21.132", 8082, 2], ["111.13.7.123", 8080, 2], ["1.82.132.75", 8080, 2], ["125.88.74.122", 83, 1], ["111.13.7.121", 80, 1], ["111.56.7.4", 8080, 0], ["111.56.7.6", 8080, 0]]
        for ips in ip_port:
            ip = ips[0]
            port = ips[1]
            proxy_ip = 'http://%s:%s' % (ip, port)
            print proxy_ip
            _db.rpush("redis:proxy_ip", proxy_ip)
    def num_redis(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        num = _db.llen("get_poi_position:start_urls")
        print num

    def update_ipportpool(self):
        _db = redis.Redis(host="192.168.20.25", port=6379, db=0)
        r = requests.get('http://192.168.20.25:8000/??types=0&count=50&country=国内&protocol=0')
        ip_port = json.loads(r.text)
        num = _db.llen("redis:proxy_ip")#查看原有ip的数量
        num_update = 0
        for ips in ip_port:
            ip = ips[0]
            port = ips[1]
            proxy_ip = 'http://%s:%s' % (ip, port)
            print proxy_ip
            _db.rpush("redis:proxy_ip", proxy_ip)#更新ip到原有ip之后
            num_update += 1
        _db.ltrim("redis:proxy_ip", num, int(num_update) + int(num)-1)#删除原有ip
        print "gengxin"

    def get_state_num(self):
        self.dbInit()
        sql = "select ID from amap_POI where State=0"
        query = self.cursor.execute(sql)
        print query
        self.dbClose()


if __name__ == "__main__":
    in_redis = in_redis()
    name = 9
    if name == 0:
        in_redis.inRedis()
    elif name == 1:
        in_redis.readRedis()
    elif name == 2:
        in_redis.delectRedis()
    elif name == 3:
        in_redis.ip_in_redis()
    elif name==4:
        in_redis.get_ip()
    elif name==5:
        in_redis.update_ip()
    elif name == 6:
        in_redis.ipportpool()
    elif name== 7:
        in_redis.num_redis()
    elif name == 8:
        scheduler = BlockingScheduler()
        scheduler.add_job(in_redis.update_ipportpool, 'cron', minute='*/1', hour='*')
        try:
            scheduler.start()
        except (KeyboardInterrupt, SystemExit):
            scheduler.shutdown()
            pass
    elif name==9:
        in_redis.get_state_num()