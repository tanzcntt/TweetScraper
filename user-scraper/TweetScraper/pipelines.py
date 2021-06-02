import os, logging, json
from scrapy.utils.project import get_project_settings
import pymongo
from TweetScraper.items import Tweet, User
from TweetScraper.utils import mkdirs


logger = logging.getLogger(__name__)
SETTINGS = get_project_settings()

class SaveToFilePipeline(object):
    ''' pipeline that save data to disk '''

    def __init__(self):
        self.saveTweetPath = SETTINGS['SAVE_TWEET_PATH']
        self.saveUserPath = SETTINGS['SAVE_USER_PATH']
        mkdirs(self.saveTweetPath) # ensure the path exists
        mkdirs(self.saveUserPath)
        # connect to mongodb
        # self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        # self.myDatabase = self.mongoClient["twitterdata"]
        # self.trackUser = self.myDatabase['trackUser']
        print("In processing................__________________")
        # try:
        #     info = self.mongoClient.server_info()  # Forces a call.
        #     # print("info: ", info)
        # except ServerSelectionTimeoutError:
        #     print("server is down.")

    def process_item(self, item, spider):
        print("item______________________________________________________", item)
        if isinstance(item, Tweet):
            savePath = os.path.join(self.saveTweetPath, item['id_'])
            if os.path.isfile(savePath):
                pass  # simply skip existing items
                # logger.debug("skip tweet:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update tweet:%s"%item['id_'])
            else:
                self.save_to_file(item,savePath)
                logger.debug("Add tweet:%s" %item['id_'])

        elif isinstance(item, User):
            savePath = os.path.join(self.saveUserPath, item['id_'])
            if os.path.isfile(savePath):
                pass  # simply skip existing items
                # logger.debug("skip user:%s"%item['id_'])
                ### or you can rewrite the file, if you don't want to skip:
                # self.save_to_file(item,savePath)
                # logger.debug("Update user:%s"%item['id_'])
            else:
                self.save_to_file(item, savePath)
                logger.debug("Add user:%s" %item['id_'])

        else:
            logger.info("Item type is not recognized! type = %s" %type(item))


    def save_to_file(self, item, fname):
        ''' input: 
                item - a dict like object
                fname - where to save
        '''
        self.save_to_track_user(item)
        with open(fname, 'w', encoding='utf-8') as f:
            json.dump(dict(item), f, ensure_ascii=False)
        print('\033[93m' + 'savetofile' + '\033[0m')

    def hello(self):
        print('\033[93m' + 'Hello world' + '\033[0m')

    # def save_to_track_user(self, item):
    #     x = self.trackUser.insert_one(item)
    #     return x
