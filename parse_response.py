#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@create Time:2018-05-23

@author:Brook
"""
import re
import json
import time

from parsel import Selector
from urllib import parse
from mitmproxy import http

from utils import MongoPipeline
import settings


class Pipeline(MongoPipeline):
    query_fields = ['key']


mongo_url = settings.MONGO_URL
db_name = settings.WECHAT_DB
coll_name = settings.WECHAT_COLL


pipe = Pipeline(mongo_url, db_name, coll_name)


def response(flow: http.HTTPFlow) -> None:
    url = flow.request.url
    resp_text = flow.response.text
    try:
        parse_result = parse.urlparse(url)
        key = ''.join(parse.parse_qs(parse_result.query)['key'])
    except:
        pass
    else:
        # 文章
        if re.search("qq\.com/s\?__", url):
            item = parse_article(url, key, resp_text)
            pipe.update(item)
        # 点赞
        elif re.search("/mp/getappmsgext", url):
            item = parse_num(key, resp_text)
            pipe.update(item)
        # 评论    
        elif re.search("/mp/appmsg_comment\?action=getcomment", url):
            item = parse_comment(key, resp_text)
            pipe.update(item)
        else:
            pass

def parse_article(req_url, key, resp):
    sel = Selector(text=resp)
    item = {}
    item['key'] = key
    item['url'] = req_url
    item['title'] = sel.xpath("//script/text()").re_first('var msg_title = "(.*)"')
    item['author'] = sel.xpath("//script/text()").re_first('var nickname = "(.*)"')
    item['date'] = sel.xpath("//script/text()").re_first('var publish_time = "(.*?)"', "")
    item['article'] = "".join([s.strip() for s in sel.xpath("//div[@id='js_content']//text()").extract()])
    return item


def parse_num(key, resp):
    content = json.loads(resp)
    info = content.get('appmsgstat', {})
    item = {}
    item['key'] = key
    item['阅读数'] = info.get('read_num')
    item['点赞数'] = info.get('like_num')
    return item


def parse_comment(key, resp):
    content = json.loads(resp)
    comments_info = {}
    comments_info['key'] = key 
    comments_info['comments'] = []
    comments = content['elected_comment']
    for comment in comments:
        comment_info = {}
        comment_pub_time = time.strftime('%Y-%m-%d', time.localtime(comment['create_time']))
        comment_info['评论者'] = comment['nick_name']
        comment_info['评论内容'] = comment['content']
        comment_info['评论点赞数'] = comment['like_num']
        comment_info['评论日期'] = comment_pub_time
        comments_info['comments'].append(comment_info)
    return comments_info

