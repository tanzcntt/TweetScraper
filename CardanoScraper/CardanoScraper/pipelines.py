from . import utils
import json
import re
import pymongo
from itemadapter import ItemAdapter
from . import text_rank_4_keyword
from datetime import datetime

color = utils.colors_mark()
textRank = text_rank_4_keyword.TextRank4Keyword()


class CardanoscraperPipeline(object):
    def __init__(self):
        self.mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
        self.myDatabase = self.mongoClient["cardanoNews"]
        self.latestNews = self.myDatabase['latestNews']
        self.postContents = self.myDatabase['allNews']

    # ================================================
    # handle put data to GraphQl
    # ================================================
    def close_spider(self, spider):
        print(f"{color['bold']}End spider {color['endc']}")

    # call every item pipeline component
    def process_item(self, item, spider):
        print(f"{color['okblue']}Pipeline handling...{color['endc']}")
        # we have two flows of data
        # 1st for posts, 2nd for contents
        # if run crawlLatestCardano, insert data into latestNews table
        if 'avatars' in item and item['latest'] == 1:
            item['avatars'] = self.handle_link_avatars(item['avatars'])
            if self.latestNews.find_one({'link_post': item['link_post']}):
                self.update_table(self.latestNews, item)
            else:
                self.insert_into_table(self.latestNews, item)
        elif 'raw_content' in item and item['latest'] == 1:
            self.handle_datetime(item)
            self.text_ranking(item)
            self.update_raw_content(self.latestNews, item)
            print(f"{color['warning']}latestNews table{color['endc']}")
        # if run crawlAllCardanoNews, insert data into postContents table
        elif 'avatars' in item and item['latest'] == 0:
            item['avatars'] = self.handle_link_avatars(item['avatars'])
            if self.postContents.find_one({'link_post': item['link_post']}):
                self.update_table(self.postContents, item)
            else:
                self.insert_into_table(self.postContents, item)
        elif 'raw_content' in item and item['latest'] == 0:
            self.handle_datetime(item)
            self.text_ranking(item)
            self.update_raw_content(self.postContents, item)
            print(f"{color['warning']}allNews table{color['endc']}")
        # print(f"{color['okgreen']}Item...{item}{color['endc']}")
        # return item

    def handle_link_avatars(self, links):
        new_links = []
        parent = 'https://sjc3.discourse-cdn.com/business4'
        for link in links:
            if "https:" not in link:
                new_links.append(parent + link)
            else:
                pass
        return new_links

    def insert_into_table(self, table, data):
        if table.insert_one(data):
            print(f"{color['okgreen']}Import Success!!!{color['endc']}")

    def update_table(self, table, data):
        query = {
            "link_post": data['link_post'],
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okblue']}Updating: title, tags, posts link,...{color['endc']}")

    def update_raw_content(self, table, data):
        query = {
            "link_post": data['link_content']
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okblue']}Updating Raw Content....{color['endc']}")

    def write_json_file(self, file, item):
        line = json.dumps(ItemAdapter(item['avatars']).asdict()) + '\n'
        file.write(line)

    def remove_html_tags(self, raw_content):
        clean = re.compile('<.*?>')
        return re.sub(clean, '', raw_content)

    def text_ranking(self, data):
        raw_content = self.remove_html_tags(data['raw_content'])
        textRank.analyze(raw_content.lower(), window_size=6, stopwords={'%'})
        data['keyword_ranking'] = textRank.get_keywords(10)
        return data['keyword_ranking']

    def handle_datetime(self, data):
        data['timestamp'] = datetime.strptime(data['post_time'], "%d %B %Y %H:%M").timestamp()
