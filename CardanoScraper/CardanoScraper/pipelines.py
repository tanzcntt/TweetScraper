import time

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
        self.testCarda = self.myDatabase['testAllNews2']
        self.iohk_sample1 = self.myDatabase['iohkSample']

    # ================================================
    # handle put data to GraphQl
    # ================================================
    def close_spider(self, spider):
        print(f"{color['warning']}Crawl Completed!{color['endc']}")

    # call every item pipeline component
    def process_item(self, item, spider):
        print(f"\n{color['okblue']}Pipeline handling...{color['endc']}")
        # we have two flows of data
        # 1st for posts, 2nd for contents
        # ================================================
        # if run crawlAllCardanoNews, insert data into allNews table
        # for Update to analyze
        # ================================================
        if item['source'] == 'cardano':
            if 'title' in item:
                item['avatars'] = self.handle_link_avatars(item['avatars'])
                if self.postContents.find_one({'link_post': item['link_post']}):
                    self.update_table(self.postContents, item)
                else:
                    self.insert_into_table(self.postContents, item)
            elif 'raw_content' in item:
                self.handle_datetime(item, item['post_time'])
                self.text_ranking(item, item['raw_content'])
                self.update_raw_content(self.postContents, item)
                print(f"{color['warning']}Imported raw_content to {self.get_table(self.postContents)} {color['endc']}\n")
        # ================================================
        # for test every day
        # ================================================
        # if item['source'] == 'cardano':
        #     if 'title' in item:
        #         item['avatars'] = self.handle_link_avatars(item['avatars'])
        #         if self.testCarda.find_one({'link_post': item['link_post']}):
        #             self.update_table(self.testCarda, item)
        #         else:
        #             self.insert_into_table(self.testCarda, item)
        #     elif 'raw_content' in item:
        #         self.handle_datetime(item, item['post_time'])
        #         self.text_ranking(item, item['raw_content'])
        #         self.update_raw_content(self.testCarda, item)
        #         print(f"{color['warning']}Imported raw_content to {self.get_table(self.testCarda)} {color['endc']}\n")
        # ================================================
        #
        # ================================================
        # print(f"{color['warning']}This is{color['endc']}Item...{color['okgreen']}{item}{color['endc']}")
        elif item['source'] == 'iohk':
            self.iohk_get_posts(item)
        elif item['source'] == 'coindesk':
            return item
        # return item

    def initialize_iohk_sample_data(self):
        iohk_all_posts = {
            'publish_date': '',
            'timestamp': '',
            'approve': 1,
            'author_title': '',
            'author_display_name': '',
            'author_thumbnail': '',
            'author_job_titles': '',
            'author_profile_links': '',
            'post_main_img': '',
            'lang': '',
            'title': '',
            'slug': '',
            'subtitle': '',
            'audio': '',
            'soundcloud': [],
            'raw_content': '',
            'keyword_ranking': '',
            'total_pages': '',
            'filters': '',
            'recent_posts': '',
            'current_page': '',
            'current_url_page': '',
            'link_content': '',
            'author_profile_url': '',
            'source': 'iohk',
            'raw_data': '',
        }
        return iohk_all_posts

    def iohk_get_posts(self, data):
        content = data['result']['pageContext']
        profile_url = "https://iohk.io/en{}page-1/"
        iohk_url = "https://iohk.io/en/blog/posts/page-{}/"
        content_url = "https://iohk.io/en{}"
        posts = content['posts']
        recent_posts = content['recentPosts']
        total_pages = content['total_pages']
        current_page = content['current_page']
        sidebar_post_filter = content['filters']
        # current_url_page = iohk_url.format(content['crumbs'][0]['path'])
        # get all posts through all pages: 44 current pages
        for post in posts:
            iohk_all_posts = self.initialize_iohk_sample_data()
            author_info = post['author']
            iohk_all_posts['publish_date'] = post['publish_date']
            iohk_all_posts['timestamp'] = self.handle_datetime(iohk_all_posts, post['publish_date']),
            iohk_all_posts['author_title'] = author_info['title']
            iohk_all_posts['author_display_name'] = author_info['display_name']
            iohk_all_posts['author_thumbnail'] = author_info['thumbnail']
            iohk_all_posts['author_job_titles'] = author_info['job_titles']
            iohk_all_posts['author_profile_links'] = author_info['profile_links']  # all social links of the author
            iohk_all_posts['post_main_img'] = post['main_image']
            iohk_all_posts['lang'] = post['lang']
            iohk_all_posts['title'] = post['title'].strip()
            iohk_all_posts['slug'] = post['slug']
            iohk_all_posts['subtitle'] = post['subtitle']
            iohk_all_posts['audio'] = post['audio']
            iohk_all_posts['soundcloud'] = post['soundcloud']
            iohk_all_posts['raw_content'] = post['body_content']
            # iohk_all_posts['recent_posts'] = recent_posts
            iohk_all_posts['total_pages'] = total_pages
            # iohk_all_posts['filters'] = sidebar_post_filter
            iohk_all_posts['current_page'] = current_page
            iohk_all_posts['current_url_page'] = iohk_url.format(current_page)
            iohk_all_posts['link_content'] = content_url.format(post['url'])
            iohk_all_posts['author_profile_url'] = profile_url.format(author_info['profile_url'])

            keyword_ranking = self.text_ranking(iohk_all_posts, iohk_all_posts['raw_content'])

            print(f"Current page: {iohk_all_posts['current_url_page']}")
            print(f"Current post: {iohk_all_posts['title']}")
            iohk_all_posts['raw_data'] = post
            iohk_all_posts['keyword_ranking'] = keyword_ranking
            if self.iohk_sample1.find_one({'link_content': iohk_all_posts['link_content']}):
                self.update_iohk(self.iohk_sample1, iohk_all_posts)
                time.sleep(2)
            else:
                self.insert_into_iohk(self.iohk_sample1, iohk_all_posts)
                time.sleep(2)

    def insert_into_iohk(self, table, data):
        print(f"\n{color['warning']}Importing: data{color['endc']}")
        if table.insert_one(data):
            print(f"{color['okblue']}Imported into {self.get_table(table)} success!{color['endc']}")
        time.sleep(1)

    def update_iohk(self, table, data):
        query = {
            'link_content': data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okcyan']}Updating {self.get_table(table)} table{color['endc']}\n")
        time.sleep(1)

    def insert_into_table(self, table, data):
        if table.insert_one(data):
            print(f"{color['okgreen']}Imported Posts {self.get_table(table)} success!!!{color['endc']}")
        time.sleep(1)

    def update_table(self, table, data):
        query = {
            "link_post": data['link_post'].strip(),
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okcyan']}Updating Latest Cardano page into {self.get_table(table)}{color['endc']} ")
        time.sleep(1)

    def update_raw_content(self, table, data):
        query = {
            "link_post": data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okcyan']}Updating Raw Content into {self.get_table(table)}{color['endc']} for post: {data['link_content']}")
        time.sleep(1)

    def handle_link_avatars(self, links):
        new_links = []
        parent = 'https://sjc3.discourse-cdn.com/business4'
        for link in links:
            if "https:" not in link:
                new_links.append(parent + link)
            else:
                pass
        return new_links

    def get_table(self, table):
        return str(table).split(', ')[-1].split("'")[1]

    def write_json_file(self, file, item):
        line = json.dumps(ItemAdapter(item['avatars']).asdict()) + '\n'
        file.write(line)

    def text_ranking(self, data, raw_content_):
        raw_content = utils.remove_html_tags(raw_content_)
        textRank.analyze(raw_content, window_size=6)
        data['keyword_ranking'] = textRank.get_keywords(10)
        return data['keyword_ranking']

    def handle_datetime(self, data, date_time):
        # cardar date type: 28 November 2017 19:22
        if '-' in date_time:
            date_time = date_time.split('T')[0]
            data['timestamp'] = datetime.strptime(date_time, "%Y-%m-%d").timestamp()
            return data['timestamp']
        data['timestamp'] = datetime.strptime(date_time, "%d %B %Y %H:%M").timestamp()
        return data['timestamp']
