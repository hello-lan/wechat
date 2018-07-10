#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
@create Time:2018-05-22

@author:Brook
"""
import os
import sqlite3
from pymongo import MongoClient


class Pipeline:
    def __init__(self, db, table):
        f =  os.path.expanduser(db)
        dirname = os.path.dirname(f)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        self.db = f 
        self.table = table

    def start(self):
        self.conn = sqlite3.connect(self.db)
        self.cur = self.conn.cursor()

    def close(self):
        self.conn.commit()
        self.conn.close()

    def __enter__(self):
        self.start()
        return self

    def __exit__(self, *args, **kwarfs):
        self.close()

    def process_item(self, item):
        keys, values = list(zip(*item.items()))
        fields = ", ".join(keys)
        values = repr(values)
        sql = """insert into {tb}({fields}) values {values}""".format(tb=self.table, fields=fields, values=values)
        try:
            self.cur.execute(sql)
        except sqlite3.OperationalError:
            # 如果不存在插入的表，则创建它
            #self.create_table(item.__class__)
            self.create_table(item)
            self.conn.commit()
            self.cur.execute(sql)
        self.conn.commit()
        
    def create_table(self, Item):
        #attrs = ItemClass.__dict__['fields'].keys()
        attrs = Item.keys()

        fields = ", ".join(["{field} Text".format(field=attr) for attr in attrs])
        sql = """
            CREATE TABLE {tb} ({fields});
        """.format(tb=self.table, fields=fields)
        self.cur.execute(sql)
        self.conn.commit() 




class MongoPipeline:
    query_fields = None  ## for update method
    def __init__(self, mongo_url, db_name, coll_name):
        self.client = MongoClient(mongo_url)
        db = self.client.get_database(db_name)
        self.coll = db.get_collection(coll_name)

    def close(self):
        self.client.close()

    def save(self, item):
        self.insert(item)
            
    def update(self, item):
        query = {k:v for k,v in item.items() if k in self.query_fields}
        try:
            self.coll.update_one(query, {"$set":item}, upsert=True)
        except:
            pass
            #self.close()
    
    def insert(self, item):
        try:
            self.coll.insert_one(item)
        except:
            self.close()   
            
    def find(self, *args, **kwargs):
        return self.coll.find(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, type, value, trace):
        self.close()

    def process_item(self, item):
        self.insert(item)


