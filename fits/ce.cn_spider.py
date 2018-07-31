#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coding:utf-8

import sys
import MySQLdb
import hashlib
from bs4 import BeautifulSoup
import requests
import confing
import warnings

reload(sys)
sys.setdefaultencoding('utf8')
warnings.filterwarnings("ignore", category = MySQLdb.Warning)

class ce(object):
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
    def getHtml(cls, url):
        try:
            contentHtml = requests.get(url=url).content
            return contentHtml
        except Exception as e:
            return None
            pass

    @classmethod
    def update(cls):
        pages = 9
        num = 0
        cls.dbInit()
        sql = "select url_md5 from source_ce order by time_pub desc limit 20"
        cls.cursor.execute(sql)
        buffer = [x[0] for x in cls.cursor.fetchall()]
        while (pages >= 0):
            if num > 4:
                break
            if pages > 0:
                pagesUrl = 'http://intl.ce.cn/sjjj/qy/index_' + str(pages) + '.shtml'
            else:
                pagesUrl = 'http://intl.ce.cn/sjjj/qy/index.shtml'
            pages -= 1
            print pagesUrl
            html = cls.getHtml(pagesUrl)
            html_num = 0
            while(html == None):
                if html_num > 3:
                    break
                html = cls.getHtml(pagesUrl)
                html_num += 1
            if html == None:
                pass
            else:
                listSoup = BeautifulSoup(html, "lxml")
                items = listSoup.find_all('div', class_="list_con left")
                for item in items:
                    if num > 4:
                        break
                    list_tag = item.find_all('li')
                    for li in list_tag:
                        if num > 4:
                            break
                        url_tag = li.a['href']
                        tag = url_tag.find('/specials/zxgjzh/')
                        if tag > 0:
                            url_tag = url_tag[5:]
                            url = 'http://intl.ce.cn/' + url_tag
                        else:
                            url_tag = url_tag[1:]
                            url = 'http://intl.ce.cn/sjjj/qy' + url_tag
                        m2 = hashlib.md5()
                        m2.update(url)
                        url_md5 = m2.hexdigest()
                        titles_tag = li.find_all('a')
                        for title_tag in titles_tag:
                            title = title_tag.get_text(strip=True)
                        if url_md5 in buffer:
                            num += 1
                            continue
                        else:
                            sql = "insert ignore into source_ce (url, url_md5, title) values(%s, %s, %s)"
                            value = (url, url_md5, title)
                            cls.cursor.execute(sql, value)
                            cls.con.commit()
    @classmethod
    def get_content(cls):
        sql = "select id, url from source_ce where craw_flag = 0"
        query = cls.cursor.execute(sql)
        print query
        if query:
            rows = cls.cursor.fetchall()
            for row in rows:
                id = row[0]
                url = row[1]
                html = cls.getHtml(url)
                num = 0
                while (html == None):
                    if num > 3:
                        break
                    html = cls.getHtml(url)
                    num += 1
                if html == None:
                    sql = "update source_ce set craw_flag=%s where id=%s"
                    contentsql = (2, id)
                    cls.cursor.execute(sql, contentsql)
                    cls.con.commit()
                    print "2", id
                else:
                    contentSoup = BeautifulSoup(html, "lxml")
                    items = contentSoup.find_all('div', class_="neirong")
                    for item in items:
                        time_pub = item.find('span', id='articleTime').get_text(strip=True)
                        time_pub = time_pub.replace('年', '-').replace('月', '-').replace('日', '')
                        time_pub = str(time_pub) + ':00'
                        source = item.find('span', id='articleSource').get_text(strip=True)
                        content_html = item.find('div', class_="content")
                        content = content_html.get_text(strip=True)
                        author = item.find('span', id="articleAuthor").get_text(strip=True)
                        catalog = u'国际经济'
                        html = html.decode('GBK')
                        html = MySQLdb.escape_string(html)
                        print id
                        sql = 'update source_ce set time_pub=%s, catalog=%s, author=%s, content=%s, content_html=%s, html=%s, source=%s, craw_flag=%s' \
                              ' where id=%s'
                        contentSql = (time_pub, catalog, author, content, content_html, html, source, 1, id)
                        cls.cursor.execute(sql, contentSql)
                        cls.con.commit()

def main():
    ce.update()
    #ce.dbInit()
    ce.get_content()
    #ce.dbClose()

if __name__ == "__main__":
    main()
