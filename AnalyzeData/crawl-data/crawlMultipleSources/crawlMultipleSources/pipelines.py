# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo
from time import sleep
from datetime import datetime
from . import utils
from .text_rank_4_keyword import TextRank4Keyword
# useful for handling different item types with a single interface


colors = utils.colors_mark()
textRank = TextRank4Keyword()


# ================================================
# shared functions
# ================================================
def insert_into_table(table, data):
    if table.insert_one(data):
        print(f"{colors['okgreen']}Imported Posts {get_table(table)} success!!!{colors['endc']}")
    sleep(1)


def update_raw_content(table, data):
    pass


def handle_text_ranking(data, raw_content_):
    raw_content = utils.remove_html_tags(raw_content_)
    textRank.analyze(raw_content, window_size=6)
    data['keyword_ranking'] = textRank.get_keywords(10)
    return data['keyword_ranking']


def handle_datetime(data, date_time):
    if '-' in date_time:
        # handle datetime for IOHK
        date_time = date_time.split('T')[0]
        data['timestamp'] = datetime.strptime(date_time, "%y-%m-%d").timestamp()
        return data['timestamp']
    data['timestamp'] = datetime.strptime(date_time, "%d %B %Y %H:%M").timestamp()


def get_table(table):
    return str(table).split(', ')[-1].split("'")[1]


class CrawlmultiplesourcesPipeline(object):

    def __init__(self):
        self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        self.myDatabase = self.mongoClient["analytic"]
        self.influencers = self.myDatabase['influencers']

    def process_item(self, item, spider):
        if item['source'] == 'upfolio.com':
            self.handle_twitter_account(data=item)
            if self.influencers.find_one({'link_avatar': item['link_avatar']}):
                self.update_table(self.influencers, item)
            else:
                self.insert_into_table(self.influencers, item)
        else:
            print(f"{colors['okcyan']}\nMove to next Cardano Pipeline!{colors['endc']}")
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


# ================================================
# only directly import 10 latest page everyday,
# do not need to update
# ================================================
class CrawlCardanoPipeline(object):
    def __init__(self):
        self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        self.myDatabase = self.mongoClient["analytic"]
        self.allNewsAnalytic = self.myDatabase['allNewsAnalytic']
        self.allTradingAnalytic = self.myDatabase['allTradingAnalytic']

    def process_item(self, item, spider):
        print(f"{colors['warning']}Working on Cardano Pipeline {colors['endc']}")
        if item['source'] == 'news.cardano':
            # import posts firstly
            if 'title' in item:
                # test update firstly
                item['avatars'] = self.handle_link_avatars(item['avatars'])
                if self.allNewsAnalytic.find_one({'link_post': item['link_post']}):
                    self.update_table(self.allNewsAnalytic, item)
                else:
                    insert_into_table(self.allNewsAnalytic, item)
            # import raw content in detail page secondly
            elif 'raw_content' in item:
                handle_datetime(item, item['post_time'])
                handle_text_ranking(item, item['raw_content'])
                self.update_raw_content(self.allNewsAnalytic, item)
                print(f"{colors['warning']}Imported raw_content to {get_table(self.allNewsAnalytic)} {colors['endc']}\n")
        elif item['source'] == 'trading.cardano':
            if 'title' in item:
                # test update firstly
                item['avatars'] = self.handle_link_avatars(item['avatars'])
                if self.allTradingAnalytic.find_one({'link_post': item['link_post']}):
                    self.update_table(self.allTradingAnalytic, item)
                else:
                    insert_into_table(self.allTradingAnalytic, item)
            elif 'raw_content' in item:
                handle_datetime(item, item['post_time'])
                handle_text_ranking(item, item['raw_content'])
                self.update_raw_content(self.allTradingAnalytic, item)
                print(f"{colors['warning']}Imported raw_content to {get_table(self.allTradingAnalytic)} {colors['endc']}\n")
        return item

    def update_table(self, table, data):
        query = {
            'link_post': data['link_post'].strip()
        }
        if table.update_one(query, {'$set': data}):
            print(f"{colors['okcyan']}Updating Latest Cardano page into {get_table(table)}{colors['endc']} ")
        sleep(1)

    def update_raw_content(self, table, data):
        query = {
            'link_post': data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            print(f"{colors['okcyan']}Updating Raw Content into {get_table(table)}{colors['endc']} for post: {data['link_content']}")
        sleep(1)

    def handle_link_avatars(self, links):
        new_links = []
        parent = 'https://sjc3.discourse-cdn.com/business4'
        for link in links:
            if "https:" not in link:
                new_links.append(parent + link)
            else:
                pass
        return new_links
