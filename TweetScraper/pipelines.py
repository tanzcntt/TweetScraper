import json
import logging
import os

import pymongo
from scrapy.utils.project import get_project_settings

from TweetScraper.items import Tweet, User
from TweetScraper.utils import mkdirs

logger = logging.getLogger(__name__)
SETTINGS = get_project_settings()


class SaveToFilePipeline(object):
    ''' pipeline that save data to disk '''

    def __init__(self):
        self.saveTweetPath = SETTINGS['SAVE_TWEET_PATH']
        self.saveUserPath = SETTINGS['SAVE_USER_PATH']
        mkdirs(self.saveTweetPath)  # ensure the path exists
        mkdirs(self.saveUserPath)
        self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        self.myDatabase = self.mongoClient["twitterdata"]
        self.uesr_collection = self.myDatabase["user"]
        self.tw_collection = self.myDatabase["tw"]
        self.tw_collection = self.myDatabase["tw"]
    def process_item(self, item, spider):
        if isinstance(item, Tweet):
            savePath = os.path.join(self.saveTweetPath, item['id_'] + ".json")

            if os.path.isfile(savePath):
                # logger.debug("skip tweet:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                logger.debug("Update tweet:%s" % item['id_'])
                self.update_to_item_mongo(item)
            else:
                self.save_to_file(item, savePath)
                self.save_to_item_mongo(item)
                logger.debug("Add tweet:%s" % item['id_'])

        elif isinstance(item, User):
            savePath = os.path.join(self.saveUserPath, item['id_'])
            if os.path.isfile(savePath):
                pass  # simply skip existing items
                # logger.debug("skip user:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update user:%s"%item['id_'])
                self.update_to_user_mongo(item)
            else:
                self.save_to_file(item, savePath)
                self.save_to_user_mongo(item)
                logger.debug("Add user:%s" % item['id_'])

        else:
            logger.info("Item type is not recognized! type = %s" % type(item))

    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(dict(item), f, ensure_ascii=False)

    def save_to_item_mongo(self, item):
        ''' input:
                item - a dict like object
                fname - where to save
        '''
        item_collection = self.myDatabase['tw']
        x = item_collection.insert_one(item["raw_data"])
        return x

    def update_to_item_mongo(self, item):
        print("Update item to mongo", item["raw_data"]["id_str"])
        ''' input:
                item - a dict like object
                fname - where to save
        '''
        item_collection = self.myDatabase['tw']
        query = {"id_str": item["raw_data"]["id_str"]}
        x = item_collection.update_one(query, {"$set": item["raw_data"]})
        return x

    def save_to_user_mongo(self, item):
        user_collection = self.myDatabase['user']
        x = user_collection.insert_one(item["raw_data"])
        return x

    def update_to_user_mongo(self, item):
        user_collection = self.myDatabase['user']
        query = {"id_str": item["raw_data"]["id_str"]}
        x = user_collection.update_one(query, {"$set": item["raw_data"]})
        return x
