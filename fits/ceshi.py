#!/usr/bin/env python
# -*- coding:utf-8 -*-
# coding:utf-8

import requests
import time
import simplejson as json
from pymongo import MongoClient

conn = MongoClient('192.168.20.42', 27017)
db = conn.tcasoft
class tcasoft(object):
    headers = {
        "Accept": "*/*",
        "Connection": "close",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "zh-CN,zh;q=0.8",
        "Content-Length": "application/x-www-form-urlencoded; charset=UTF-8",
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36",
        "Cookie": "JSESSIONID=2B03C03AE6534246DCFCFBDFB16BFFEC"
    }
    def get_reportId(self):
        pagenum = 1
        while(pagenum <=55):
            formdata = {
                "page": pagenum
            }
            url = "http://www.tcasoft.com/tcaCloudPlatform/sample/findSample.action"
            html = requests.post(url= url, headers=self.headers, data=formdata)
            html_json = json.loads(html.text)
            reportIds = html_json.get("reportIds")
            print reportIds
            samples = html_json.get("samples")
            i = 0
            for sample in samples:
                createTime = sample["createTime"]
                updateTime = sample["updateTime"]
                fileName = sample["fileName"]
                id = sample["id"]
                reportId = reportIds[i]
                i += 1
                reportId_inMongo = {
                    "_id": id,
                    "createTime": createTime,
                    "updateTime": updateTime,
                    "fileName": fileName,
                    "reportId": reportId,
                    "update_flag": 0
                }
                if db.sample.find_one({"_id": id}) == None:
                    db.sample.save(reportId_inMongo)
            time.sleep(5)
            pagenum += 1

    def get_sample(self):
        url = "http://www.tcasoft.com/tcaCloudPlatform/report/viewReport.action"
        demos = db.sample.find({"update_flag": 0})
        for demo in demos:
            parentReportId = demo["_id"]
            print parentReportId
            childReportId = str(parentReportId) + "-0"
            formdata= {
                "parentReportId": parentReportId,
                "childReportId": childReportId
            }
            html = requests.post(url=url, data=formdata, headers=self.headers)
            sample_json = html.text
            #从sample_json中提取数据
            requests.post.keep_alive = False
            db.sample.update({"_id": parentReportId},{"$set" : {"sample_json": sample_json, "update_flag": 1}})
            time.sleep(5)

if __name__ == "__main__":
    tcasoft = tcasoft()
    tcasoft.get_reportId()
    tcasoft.get_sample()