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
        self.iohk = self.myDatabase['iohk']
        self.iohk_sample1 = self.myDatabase['iohkSample1']
        self.iohk_sample2 = self.myDatabase['iohkSample2']

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
        # ================================================
        # if run crawlAllCardanoNews, insert data into allNews table
        # ================================================
        if 'title' in item:
            item['avatars'] = self.handle_link_avatars(item['avatars'])
            if self.postContents.find_one({'link_post': item['link_post']}):
                self.update_table(self.postContents, item)
            else:
                self.insert_into_table(self.postContents, item)
        elif 'raw_content' in item:
            self.handle_datetime(item)
            self.text_ranking(item, item['raw_content'])
            self.update_raw_content(self.postContents, item)
            print(f"{color['warning']}allNews table{color['endc']}")
        # print(f"{color['warning']}This is{color['endc']}Item...{color['okgreen']}{item}{color['endc']}")
        # if self.iohk.insert_one(item):
        #     print(f"{color['okcyan']} Import Success! {color['endc']}")
        self.iohk_get_posts(item)
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
            print(f"{color['okgreen']}Import Posts success!!!{color['endc']}")

    def update_table(self, table, data):
        query = {
            "link_post": data['link_post'],
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okcyan']}Updating Latest page{color['endc']}")

    def update_raw_content(self, table, data):
        query = {
            "link_post": data['link_content']
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okcyan']}Updating Raw Content....{color['endc']}")

    def write_json_file(self, file, item):
        line = json.dumps(ItemAdapter(item['avatars']).asdict()) + '\n'
        file.write(line)

    def text_ranking(self, data, raw_content_):
        raw_content = utils.remove_html_tags(raw_content_)
        textRank.analyze(raw_content, window_size=6)
        data['keyword_ranking'] = textRank.get_keywords(10)
        return data['keyword_ranking']

    def handle_datetime(self, data):
        data['timestamp'] = datetime.strptime(data['post_time'], "%d %B %Y %H:%M").timestamp()

    def handle_iohk(self, data):
        content = data['result']['posts']
        author = content['author']['display_name']
        author_thumbnail = author['thumbnail']
        job_titles1 = author['localized']  # including job titles, email, youtube link, linkedin, twitter, github.
        profile_url = "https://iohk.io/en" + author['profile_url'] + "page-1/"
        first_post_img = content['main_image']

    def initialize_iohk_sample_data(self):
        iohk_all_posts = {
            'publish_date': '',
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
            'body_content': '',
            'keyword_ranking': '',
            'total_pages': '',
            'filters': '',
            'recent_posts': '',
            'current_page': '',
            'current_url_page': '',
            'url': '',
            'author_profile_url': '',
            'raw_data': '',
        }
        # get recent posts on sidebar
        iohk_recent_posts = {
            'recent_posts': '',
        }
        return iohk_all_posts

    def iohk_get_posts(self, data):
        content = data['result']['pageContext']
        profile_url = "https://iohk.io/en{}page-1/"
        iohk_url = "https://iohk.io/en{}"

        posts = content['posts']
        recent_posts = content['recentPosts']
        total_pages = content['total_pages']
        current_page = content['current_page']
        sidebar_post_filter = content['filters']
        current_url_page = iohk_url.format(content['crumbs'][0]['path'])
        # get all posts through all pages: 44 current pages
        for post in posts:
            sample2 = {
                'posts': '',
                'keyword_ranking': '',
                # 'recents_post': recent_posts,
                'total_pages': total_pages,
                'current_pages': current_page,
                'current_url_page': current_url_page,
                'filters': sidebar_post_filter,
            }
            iohk_all_posts = self.initialize_iohk_sample_data()
            author_info = post['author']
            iohk_all_posts['publish_date'] = post['publish_date']
            iohk_all_posts['author_title'] = author_info['title']
            iohk_all_posts['author_display_name'] = author_info['display_name']
            iohk_all_posts['author_thumbnail'] = author_info['thumbnail']
            iohk_all_posts['author_job_titles'] = author_info['job_titles']
            iohk_all_posts['author_profile_links'] = author_info['profile_links']  # all social links of the author
            iohk_all_posts['post_main_img'] = post['main_image']
            iohk_all_posts['lang'] = post['lang']
            iohk_all_posts['title'] = post['title']
            iohk_all_posts['slug'] = post['slug']
            iohk_all_posts['subtitle'] = post['subtitle']
            iohk_all_posts['audio'] = post['audio']
            iohk_all_posts['soundcloud'] = post['soundcloud']
            iohk_all_posts['body_content'] = post['body_content']

            # iohk_all_posts['recent_posts'] = recent_posts
            iohk_all_posts['total_pages'] = total_pages
            # iohk_all_posts['filters'] = sidebar_post_filter
            iohk_all_posts['current_page'] = current_page
            iohk_all_posts['current_url_page'] = current_url_page

            iohk_all_posts['url'] = iohk_url.format(post['url'])
            iohk_all_posts['author_profile_url'] = profile_url.format(author_info['profile_url'])
            iohk_all_posts['raw_data'] = post

            keyword_ranking = self.text_ranking(iohk_all_posts, iohk_all_posts['body_content'])
            iohk_all_posts['keyword_ranking'] = keyword_ranking
            self.insert_into_iohk(iohk_all_posts, 1)

            time.sleep(1)
            sample2['posts'] = iohk_all_posts
            sample2['keyword_ranking'] = keyword_ranking
            self.insert_into_iohk(sample2, 2)
            time.sleep(1)

    def insert_into_iohk(self, data, sample):
        print(f"\n{color['warning']}Importing: data{color['endc']}")
        if sample == 1:
            if self.iohk_sample1.insert_one(data):
                print(f"{color['okblue']}Import into IOHK sample1 success!{color['endc']}\n")
        else:
            if self.iohk_sample2.insert_one(data):
                print(f"{color['okcyan']}Import into IOHK sample2 success!{color['endc']}\n")
