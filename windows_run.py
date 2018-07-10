# -*- coding: utf-8 -*-
"""
Created on Tue May 22 17:09:33 2018

@author: shaohan
"""

import time
from pywinauto.application import Application
import pywinauto
from utils import MongoPipeline
import settings

mongo_url = settings.MONGO_URL
mongo_db = settings.URL_DB
mongo_coll = settings.URL_COLL

app = Application().Connect(title='微信')

wechat = app['微信']


with MongoPipeline(mongo_url, mongo_db, mongo_coll) as pipe:
    for item in pipe.find():
        url = item['url']
        pywinauto.mouse.click(button='left', coords=(1387, 544))
        wechat.TypeKeys(url)
        wechat.TypeKeys('{ENTER}')
        pywinauto.mouse.click(button='left', coords=(1570, 417))
        time.sleep(8)

