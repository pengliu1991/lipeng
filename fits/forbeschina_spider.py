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
import confing

reload(sys)
sys.setdefaultencoding('utf8')
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

class forbeschina(object):
    headers = {
        'Host': 'www.forbeschina.com',
        'Connection': 'keep-alive',
        'Content-Length': '43',
        'Origin': 'http://www.forbeschina.com',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': '*/*',
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'Content-Type': 'application/x-www-form-urlencoded'}

    @classmethod
    def dbInit(cls):
        cls.con = MySQLdb.connect(host=confing.HOST, user="root", passwd="root", port=3306, db="fits", \
                                  charset='utf8')
        cls.cursor = cls.con.cursor()
        cls.cursor.execute("set names utf8")
        print "enter dbInit"

    @classmethod
    def dbClose(cls):
        print "enter dbclose"
        cls.con.commit()
        cls.con.close()
    @classmethod
    def getListHtml(cls, url, post):
        try:
            listHtml = requests.post(url=url, data=post, headers=cls.headers).content
            return listHtml
        except Exception as e:
            return None
            pass

    @classmethod
    def getContentHtml(cls, url):
        try:
            contentHtml = requests.get(url=url).content
            return contentHtml
        except Exception as e:
            return None
            pass

    @classmethod
    def update(cls):
        num = 0
        cls.dbInit()
        sql = "select url_md5 from source_forbeschina order by time_pub desc limit 20"
        cls.cursor.execute(sql)
        buffer = [x[0] for x in cls.cursor.fetchall()]
        nowTime = int(time.time())
        lasttime = str(nowTime)
        listUrl = "http://www.forbeschina.com/ajax/news_most.php"
        while(lasttime != ''):
            if num >4:
                break
            postdata = {
                'lasttime': lasttime,
                'cate': '%E5%85%A8%E9%83%A8'}
            listHtml = cls.getListHtml(listUrl, postdata)
            if listHtml == None:
                pass
            else:
                soup = BeautifulSoup(listHtml, "lxml")
                time_tag = soup.input.attrs
                if time_tag.has_key('value'):
                    lasttime = str(soup.input['value'])
                    listContent = soup.find_all('div', class_='news_list')
                    for content in listContent:
                        if num > 4:
                            break
                        title = content.a['title']
                        author = content.find(name='span', class_='author_name').get_text(strip=True)
                        url = content.a['href']
                        url = 'http://www.forbeschina.com' + str(url)
                        m2 = hashlib.md5()
                        m2.update(url)
                        url_md5 = m2.hexdigest()
                        sql = 'insert ignore into source_forbeschina (url, url_md5, title, author) values(%s, %s, %s, %s)'
                        value = (url, url_md5, title, author)
                        if url_md5 in buffer:
                            num += 1
                            continue
                        else:
                            cls.cursor.execute(sql, value)
                            cls.con.commit()
                else:
                    lasttime = ''
                print lasttime

    @classmethod
    def getcontent(cls):
        sql = "select id, url from source_forbeschina where craw_flag = 0"
        query = cls.cursor.execute(sql)
        print query
        if query:
            rows = cls.cursor.fetchall()
            for row in rows:
                id = row[0]
                url = row[1]
                html = cls.getContentHtml(url)
                num = 0
                while(html == None):
                    if num > 3:
                        break
                    html = cls.getContentHtml(url)
                    num += 1
                if html == None:
                    sql = "update source_forbeschina set craw_flag=%s where id=%s"
                    contentsql = (2, id)
                    cls.cursor.execute(sql, contentsql)
                    cls.con.commit()
                    print "2"
                else:
                    contentSoup = BeautifulSoup(html, "lxml")
                    channel = contentSoup.find('div', id='channel')
                    if channel == None:
                        sql = "update source_forbeschina set craw_flag=%s where id=%s"
                        contentsql = (2, id)
                        cls.cursor.execute(sql, contentsql)
                        cls.con.commit()
                        print "22"
                    else:
                        catalog_tag = channel.find('input')
                        if catalog_tag == None:
                            catalog = channel.find_all('a')
                            catalog = catalog[2].get_text(strip=True)
                        else:
                            catalog = channel.input['value']
                        #print catalog
                        # catalog = channel.input['value']
                        author_tag = contentSoup.find('div', class_='userinfo')
                        if author_tag == None:
                            author_urltag = contentSoup.find('div', class_='message')
                            author_url = author_urltag.a['href']
                            author_url = "http://www.forbeschina.com" + str(author_url)
                            time = author_urltag.find('h6')
                            if time == None:
                                time_pub = contentSoup.find('p', class_='p_message').get_text(strip=True)
                                print time_pub
                            else:
                                time_pub = time.get_text(strip=True)
                                # print time_pub
                        else:
                            author_urltag = author_tag.find('p', class_='p_userinfo_right1')
                            author_url = author_urltag.a['href']
                            time = contentSoup.find('h6')
                            if time == None:
                                time_pub = contentSoup.find('p', class_='p_message').get_text(strip=True)
                            else:
                                time_pub = time.get_text(strip=True)
                        time_pub = str(time_pub).replace('年', '-').replace('月', '-').replace('日', '')
                        print time_pub
                        content_html = contentSoup.find('div', class_='p_detail')
                        content = ""
                        content_all = content_html.find_all('p')
                        for item in content_all:
                            item = item.get_text(strip=True)
                            item = str(item)
                            content += item
                        print content
                        html = MySQLdb.escape_string(html)
                        content = MySQLdb.escape_string(content)
                        sql = 'update source_forbeschina set time_pub=%s, catalog=%s, content=%s, content_html=%s, html=%s, author_url=%s, craw_flag=%s where id=%s'
                        contentSql = (time_pub, catalog, content, content_html, html, author_url, 1, id)
                        try:
                            cls.cursor.execute(sql, contentSql)
                            cls.con.commit()
                        except (AttributeError, MySQLdb.OperationalError):
                            cls.dbInit()
                            cls.cursor.execute(sql, contentSql)
                            cls.con.commit()

def main():
    forbeschina.update()
    #forbeschina.dbInit()
    forbeschina.getcontent()
    forbeschina.dbClose()

if __name__ == '__main__':
    main()
