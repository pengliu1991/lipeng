#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coding:utf-8
# 用ThreadPoolExecutor来实现线程池，此方法创建线程简单
import cookielib
import sys
import urllib2
import MySQLdb
import ssl
import hashlib
from bs4 import BeautifulSoup
import requests
import time
import warnings
import simplejson as json
import confing
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import concurrent.futures

reload(sys)
sys.setdefaultencoding('utf8')
warnings.filterwarnings("ignore", category=MySQLdb.Warning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class nytimes(object):
    def dbInit(self):
        self.con = MySQLdb.connect(host="192.168.20.40",user="root",passwd="root",port=3306,db="fits",charset ="utf8")
        self.cursor = self.con.cursor()
        self.cursor.execute("set names utf8")
        print "Enter dbInit"

    def dbClose(self):
        self.con.commit()
        self.con.close()
        print "Enter dbClose"

    def get_html(self, url):
        try:
            html = requests.get(url, verify=False).content
            return html
        except Exception as e:
            return None
            print e
            pass

    def obtainContent(self, html, id):
        contentSoup = BeautifulSoup(html, "lxml")
        byline = contentSoup.find('p', class_='byline-dateline')
        author_url = ""
        if byline == None:
            vedio = contentSoup.find('p', class_='byline')
            if vedio == None:
                pass
            else:
                author_url = vedio.a['href']
        else:
            author_url = byline.a['href']
        log = contentSoup.find('h3', class_='kicker')
        if log == None:
            article_type = 0
            log = contentSoup.find('h6', class_='kicker')
            if log == None:
                catalog = "SHOWS"
            else:
                catalog = log.find('a').get_text(strip=True)
        else:
            catalog = log.get_text(strip=True)
        contenthtml = contentSoup.find('div', class_='story-body story-body-1')
        if contenthtml == None:
            content_html = ""
            content = ""
        else:
            content_html = contenthtml
            content_all = content_html.find_all('p', class_='story-body-text story-content')
            content = ""
            for item in content_all:
                item = item.get_text(strip=True)
                item = str(item)
                content += item

    def getContent(self):
        sql = "select url from source_en_nytimes where craw_flag = 0"
        query = self.cursor.execute(sql)
        print query
        if query:
            rows = self.cursor.fetchall()
            urls= []
            htmls = []
            i = 0
            for row in rows:
                urls.append(row[0])
                i += 1
            with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
                future_to_url = {executor.submit(self.get_html, url): url for url in urls}
                for future in concurrent.futures.as_completed(future_to_url):
                    prime = future_to_url[future]
                    url_md5 = hashlib.md5(prime).hexdigest()
                    html = future.result()

                    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:


                    """sql = "update source_en_nytimes set html=%s, craw_flag=%s where url_md5=%s"
                    if html == None:
                        print "None"
                        value = (html, 3, url_md5)
                    else:
                        print "html"
                        value = (html, 2, url_md5)
                    try:
                        self.cursor.execute(sql, value)
                        self.con.commit()
                    except Exception as e:
                        print e
                        pass"""
                    print "------------------------------------------------"

if __name__ == "__main__":
    nytimes = nytimes()
    nytimes.dbInit()
    #nytimes.get_list()
    nytimes.getContent()

