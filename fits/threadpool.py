#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coding:utf-8
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

    def getContent(self):
        sql = "select id, html from source_en_nytimes where craw_flag = 2"
        query = self.cursor.execute(sql)
        print query
        if query:
            rows = self.cursor.fetchall()
            for row in rows:
                id = row[0]
                html = row[1]
                contentSoup = BeautifulSoup(html, "lxml")
                byline = contentSoup.find('p', class_='byline-dateline')
                author_url = ""
                if byline == None:
                    vedio = contentSoup.find('p', class_='byline')
                    if vedio == None:
                        pass
                    else:
                        if vedio.find('a'):
                            author_url = vedio.a['href']
                else:
                    if byline.find('a'):
                        author_url = byline.a['href']
                log = contentSoup.find('h3', class_='kicker')
                catalog = ""
                if log == None:
                    article_type = 0
                    log = contentSoup.find('h6', class_='kicker')
                    if log == None:
                        catalog = "SHOWS"
                    else:
                        if log.find('a'):
                            catalog = log.find('a').get_text(strip=True)
                else:
                    if log.find('a'):
                        catalog = log.get_text(strip=True)
                contenthtml = contentSoup.find('div', class_='story-body story-body-1')
                html = MySQLdb.escape_string(html)
                if contenthtml == None:
                    content_html = ""
                    content = ""
                    sql = 'update source_en_nytimes set catalog=%s, content=%s, content_html=%s, html=%s, author_url=%s, article_type=%s, craw_flag=%s where id=%s'
                    contentSql = (catalog, content, content_html, html, author_url, article_type, 4, id)
                else:
                    content_html = contenthtml
                    content_all = content_html.find_all('p', class_='story-body-text story-content')
                    content = ""
                    for item in content_all:
                        item = item.get_text(strip=True)
                        item = str(item)
                        content += item
                    sql = 'update source_en_nytimes set catalog=%s, content=%s, content_html=%s, html=%s, author_url=%s, craw_flag=%s where id=%s'
                    contentSql = (catalog, content, content_html, html, author_url, 1, id)
                try:
                    print id
                    self.cursor.execute(sql, contentSql)
                    self.con.commit()
                    print "scuess"
                except (AttributeError, MySQLdb.OperationalError):
                    self.dbInit()
                    self.cursor.execute(sql, contentSql)
                    self.con.commit()

if __name__ == "__main__":
    nytimes = nytimes()
    nytimes.dbInit()
    #nytimes.get_list()
    nytimes.getContent()

"""URLS = ['http://www.foxnews.com/',
        'http://www.cnn.com/',
        'http://europe.wsj.com/',
        'http://www.bbc.co.uk/',
        'http://some-made-up-domain.com/']
def load_url(url, timeout):
    with requests.get(url, timeout=timeout) as conn:
        return conn.read()
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
    # Start the load operations and mark each future with its URL
    future_to_url = {executor.submit(load_url, url, 60): url for url in URLS}
    for future in concurrent.futures.as_completed(future_to_url):
        url = future_to_url[future]
        try:
            data = future.result()
        except Exception as exc:
            print('%r generated an exception: %s' % (url, exc))
        else:
            print('%r page is %d bytes' % (url, len(data)))"""