#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@create Time:2018-05-24

@author:Brook
"""
# 爬搜狗时用到chromedriver(通过selenium)
driver_path = "/home/brook/tools/chromedriver"

# mongodb保存数据
MONGO_URL = 'mongodb://user:password@ip'

# 第一步通过sogou获得的url存储数据库
URL_DB = 'test'
URL_COLL = 'url'

# 微信数据保存位置
WECHAT_DB = "test"
WECHAT_COLL = "wechat"
