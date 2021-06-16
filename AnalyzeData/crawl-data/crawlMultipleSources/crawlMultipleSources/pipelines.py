# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from time import sleep
from scrapy import Item
from . import utils
# useful for handling different item types with a single interface

colors = utils.colors_mark()

class CrawlmultiplesourcesPipeline(object):

    def __init__(self):
        self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        self.myDatabase = self.mongoClient["analytic"]
        self.influencers = self.myDatabase['influencers']

    def process_item(self, item, spider):
        self.handle_twitter_account(data=item)
        if self.influencers.find_one({'link_avatar': item['link_avatar']}):
            self.update_table(self.influencers, item)
        else:
            self.insert_into_table(self.influencers, item)
        return item

    def insert_into_table(self, table, data):
        if table.insert_one(data):
            print(f"{colors['okblue']} Imported success! {colors['endc']}")
            sleep(.5)

    def update_table(self, table, data):
        query = {
            'link_avatar': data['link_avatar'],
        }
        if table.update_one(query, {'$set': data}):
            print(f"{colors['okcyan']}Updating {colors['endc']}")
        sleep(.5)

    def handle_twitter_account(self, data):
        if 'twitter' in data['link_profile']:
            data['twitter_account'] = data['link_profile'].split('m/')[1]
        else:
            data['twitter_account'] = ""
