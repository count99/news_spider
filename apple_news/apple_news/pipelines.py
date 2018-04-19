# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3

class AppleNewsPipeline(object):
    def open_spider(self, spider):
        self.conn = sqlite3.connect('news.db')
        self.cur = self.conn.cursor()
        self.cur.execute('create table if not exists apple_news("title" text, "content" text, "time" text, "view" integer, "url" text NOT NULL, PRIMARY KEY ("url"));')
    def close_spider(self, spider):
        self.conn.commit()
        self.conn.close()
    def process_item(self, item, spider):
        sql = "REPLACE INTO apple_news (title, content, time, view, url) VALUES (:title, :content, :time, :view, :url);"
        self.cur.execute(sql, item._values)
        return item
