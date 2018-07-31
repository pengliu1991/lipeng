#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coding:utf-8
import time
import sys
import MySQLdb
import hashlib
from bs4 import BeautifulSoup
import requests
import warnings
import simplejson as json
import random
import re
import confing
import chardet
from requests.packages.urllib3.exceptions import InsecureRequestWarning

reload(sys)
sys.setdefaultencoding('utf8')
warnings.filterwarnings("ignore", category = MySQLdb.Warning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class forbes(object):
    headers = {
        'Host': 'www.forbes.com',
        #'Proxy-Connection': 'keep-alive',
        'Connection': 'keep-alive',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate, sdch',
        'Accept-Language': 'zh-CN,zh;q=0.8'}

    @classmethod
    def get_html(cls, url):
        try:
            html = requests.get(url=url, headers=cls.headers, verify=False)
            response = html.content
            data_html = json.loads(response)
            return data_html
        except:
            return None
            pass

    @classmethod
    def get_contenthtml(cls, url):
        try:
            html = requests.get(url=url, verify=False, timeout=30)
            response = html.content
            return response
        except:
            return None
            pass

    @classmethod
    def dbInit(cls):
        cls.con = MySQLdb.connect(host=confing.HOST, user="root", passwd="root", port=3306, db="fits", \
                                   charset='utf8')
        cls.cursor = cls.con.cursor()
        cls.cursor.execute("set names utf8")
        print "enter dbInit"

    @classmethod
    def update(cls):
        num = 0
        cls.dbInit()
        sql = "select url_md5 from source_forbes order by time_pub desc limit 20"
        cls.cursor.execute(sql)
        buffer = [x[0] for x in cls.cursor.fetchall()]
        nowTime = int(time.time())
        i = 0
        lasttime = nowTime
        ids_last = ""
        while (i < 10):
            if num>4:
                break
            if i == 0:
                listurl = 'http://www.forbes.com/forbesapi/source/more.json?date=' + str(lasttime) \
                          + '&limit=10&source=stream&sourceType=channelsection&sourceValue=channel_1&start=1'
            else:
                listurl = 'http://www.forbes.com/forbesapi/source/more.json?date=' + str(lasttime) + '&ids=' \
                          + str(ids_last) + '&limit=10&source=stream&sourceType=channelsection&sourceValue=channel_1&start=' \
                          + str(i*10 + 1)
            print listurl
            i += 1
            html = cls.get_html(url=listurl)
            html_num = 0
            while(html==None):
                html = cls.get_html(url=listurl)
                html_num += 1
                if html_num > 5:
                    break
            data = html
            if data == None or data['promotedContent'] == None:
                pass
            else:
                items = data['promotedContent']['contentPositions']
                j = 0
                ids_tag = {}
                for item in items:
                    if num > 4:
                        break
                    title = item['title']
                    url = item['uri']
                    m2 = hashlib.md5()
                    m2.update(url)
                    url_md5 = m2.hexdigest()
                    if item.has_key("authors"):
                        author_tag = item['authors']
                        author = author_tag[0]['name']
                        author_url = author_tag[0]['url']
                    date = item['date']
                    time_pub = str(date)[:-3]
                    lasttime = time_pub
                    time_pub = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(int(time_pub)))
                    sql = "insert ignore into source_forbes (url, url_md5, title, author, author_url, time_pub) values(%s, %s, %s, %s, %s, %s)"
                    value = (url, url_md5, title, author, author_url, time_pub)
                    id = item['id']
                    ids_tag[j] = id
                    j += 1
                    if url_md5 in buffer:
                        num += 1
                        continue
                    else:
                        try:
                            cls.cursor.execute(sql, value)
                            cls.con.commit()
                            #print "insert sucess"
                        except Exception as e:
                            pass
                            print e
                k = len(ids_tag)
                ids_new = ""
                while (k > 0):
                    k = k - 1
                    if k == 9:
                        ids_new = ids_new + ids_tag[k]
                    else:
                        ids_new = ids_new + ',' + ids_tag[k]
                if ids_last == "":
                    ids_last = ids_new + ids_last
                else:
                    ids_last = ids_new + ',' + ids_last
    @classmethod
    def dbClose(cls):
        print "enter dbclose"
        cls.cursor.close()
        cls.con.commit()
        cls.con.close()

    @classmethod
    def get_content(cls):
        sql = "select id, url from source_forbes where craw_flag = 0"
        query = cls.cursor.execute(sql)
        if query:
            rows = cls.cursor.fetchall()
            for row in rows:
                id = row[0]
                url = row[1]
                print url
                siteOrPicture = url.find("pictures")
                if siteOrPicture < 0:
                    if url.find("video")<0:
                        html = cls.get_contenthtml(url=url)
                        html_num = 0
                        while (html == None):
                            html = cls.get_contenthtml(url=url)
                            html_num += 1
                            if html_num > 3:
                                break
                        if html == None:
                            pass
                        else:
                            contentSoup = BeautifulSoup(html, "lxml")
                            content_html = contentSoup.find(class_="article-text clearfix")
                            try:
                                article_text = content_html.find_all(name="p")
                                content = ""
                                for text in article_text:
                                    getText = text.get_text(strip=True).replace(r'\\', '').replace(r'\r', '')
                                    content = content + " " + getText
                                content = content.lstrip()
                                catalog = u'Business'
                                codelast = chardet.detect(html)['encoding']
                                html = html.decode(codelast)
                                html = MySQLdb.escape_string(html)
                                content = MySQLdb.escape_string(content)
                                #print content
                                sql = 'update source_forbes set content=%s, content_html=%s, html=%s, catalog=%s, craw_flag=%s where id=%s'
                                contentSql = (content, content_html, html, catalog, 1, id)
                                cls.cursor.execute(sql, contentSql)
                                cls.con.commit()
                            except:
                                pass
                    else:
                        contentSql = "update source_forbes set craw_flag=%s, article_type=%s where id=%s"
                        value = (2, 2, id)
                        cls.cursor.execute(contentSql, value)
                        cls.con.commit()
                else:
                    contentSql = "update source_forbes set craw_flag=%s, article_type=%s where id=%s"
                    value = (2, 2, id)
                    cls.cursor.execute(contentSql, value)
                    cls.con.commit()

def main():
    forbes.update()
    #forbes.dbInit()
    forbes.get_content()
    forbes.dbClose()

if __name__ == '__main__':
    main()
