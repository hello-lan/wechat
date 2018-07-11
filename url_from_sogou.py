# !/usr/bin/env python3
"""@author: loricheung <mr.lorizhang@gmail.com>"""
""" """
import sys
import time
import random
import logging

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from utils import MongoPipeline
import settings

driver_path = settings.driver_path
mongo_url = settings.MONGO_URL
db_name = settings.URL_DB
coll_name = settings.URL_COLL


class Search:
    """search wechat public account article on Sogou"""
    def __init__(self, driver_path):
        self.driver = webdriver.Chrome(executable_path=driver_path)
        self.driver.get('http://weixin.sogou.com')

    def login(self):
        login_btn = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, "loginBtn")))
        login_btn.click()
        WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.ID, "login_yes")))
        logging.info('login successful!')

    def search(self, keyword):
        self.input_btn = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "query")))
        self.input_btn.clear()
        self.input_btn.send_keys(keyword)
        self.form_btn = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CLASS_NAME, "swz")))
        self.form_btn.click()
        self.tool_btn = WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.LINK_TEXT, "搜索工具")))
        self.tool_btn.click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="time"]').click()
        time.sleep(1)
        self.driver.find_element_by_xpath('//*[@id="tool"]/span[1]/div/a[5]').click()
        info_list = []
        while True:
            print(self.driver.current_url)
            article_list = self.driver.find_elements_by_xpath("//li[starts-with(@id, 'sogou_vr_11002601_box_')]")
            for article in article_list:
                info = {}
                title = article.find_element_by_xpath('*//h3/a')
                url = title.get_attribute('href')
                info['title'] = title.text
                info['url'] = url
                info['author'] = article.find_element_by_xpath(".//div/a[@class='account']").text
                yield info
                #info_list.append(info)
            time.sleep(random.randint(5, 10))
            try:
                next_btn = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.ID, "sogou_next")))
                time.sleep(5)
                next_btn.click()
                continue
            except Exception as e:
                logging.info('no more pages, now quit...')
                break
                print(e)


   
if __name__ == "__main__":
    #coll = sys.argv[1]
    #keywords = sys.argv[2:]

    coll = coll_name
    keywords = sys.argv[1:]
    
    search = Search(driver_path)
    search.login()

    with MongoPipeline(mongo_url, db_name, coll) as pipe:
        for kw in keywords:
            for item in search.search(kw):
                item['keword'] = kw
                pipe.insert(item)




