#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coding:utf-8
import sys
import MySQLdb
import hashlib
from bs4 import BeautifulSoup
import requests
import time
import warnings
import simplejson as json
import confing
from requests.packages.urllib3.exceptions import InsecureRequestWarning

reload(sys)
sys.setdefaultencoding('utf8')
warnings.filterwarnings("ignore", category=MySQLdb.Warning)
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


class nytimes(object):

    def dbInit(self):
        self.con = MySQLdb.connect(host=confing.HOST,user="root",passwd="root",port=3306,db="fits",charset ="utf8")
        self.cursor = self.con.cursor()
        self.cursor.execute("set names utf8")
        print "Enter dbInit"

    def dbClose(self):
        self.con.commit()
        self.con.close()
        print "Enter dbClose"

    def get_html(self, url):
        session = requests.Session()
        try:
            html = session.get(url=url, verify=False)
            return html
        except Exception as e:
            return None
            print e
            pass
    def get_contenthtml(self, url):
        try:
            html = requests.get(url, verify=False).content
            return html
        except:
            return None
            pass

    def get_list(self):
        sql = "select url_md5 from source_en_nytimes order by time_pub desc limit 20"
        self.cursor.execute(sql)
        buffer = [x[0] for x in self.cursor.fetchall()]
        num = 0
        i = 1
        while i:
            if num > 4:
                break
            listurl = "https://www.nytimes.com/svc/collections/v1/publish/www.nytimes.com/section/us?q=&sort=newest&page=" \
                      + str(i) + "&dom=www.nytimes.com&dedupe_hl=y"
            i += 1
            html = self.get_html(listurl)
            updateNum = 0
            if html == None:
                pass
            else:
                data = html.json()
                items = data['members']['items']
                for item in data['members']['items']:
                    if num > 4:
                        break
                    author = item['byline']
                    title = item['headline']
                    timestamp = item['publication_date']
                    url = item['url']
                    time_pub = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(int(timestamp)))
                    url_md5 = hashlib.md5(url).hexdigest()
                    if url_md5 in buffer:
                        num += 1
                        continue
                    url = MySQLdb.escape_string(url)
                    print author,timestamp, url_md5,time_pub
                    sql = 'insert ignore into source_en_nytimes (url, url_md5, title, author, time_pub) values(%s, %s, %s, %s, %s)'
                    value = (url, url_md5, title, author, time_pub)
                    try:
                        self.cursor.execute(sql, value)
                        self.con.commit()
                    except (AttributeError, MySQLdb.OperationalError):
                        self.dbInit()
                        self.cursor.execute(sql, value)
                        self.con.commit()

    def get_content(self):
        sql = "select id, url from source_en_nytimes where craw_flag=0"
        query = self.cursor.execute(sql)
        print query
        if query:
            rows = self.cursor.fetchall()
            for row in rows:
                id = row[0]
                url = row[1]
                html = self.get_contenthtml(url)
                num = 0
                while(html == None):
                    if num > 3:
                        break
                    html = self.get_contenthtml(url)
                    num += 1
                if html == None:
                    sql = "update source_en_nytimes set craw_flag=%s where id=%s"
                    contentSql = (3, id)
                else:
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
                except (AttributeError, MySQLdb.OperationalError):
                    self.dbInit()
                    try:
                        self.cursor.execute(sql, contentSql)
                        self.con.commit()
                    except:
                        pass
    def main(self):
        self.dbInit()
        self.get_list()
        self.get_content()
        self.dbClose()

if __name__ == "__main__":
    nytimes = nytimes()
    nytimes.main()
