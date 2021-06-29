import time
import codecs
import json
import re
import pymongo
import html
from datetime import datetime
from w3lib.html import remove_tags
from . import utils
from time import sleep
color = utils.colors_mark()
mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")


def sample_data():
    data = {
        'id': '',  # id
        'title': '',  # postTranslate/title
        'subtitle': '',  # leadText
        'link_img': '',  # postTranslate/avatar
        'views': '',  # views
        'id_post_translate': '',  # postTranslate/id
        'description': '',  # postTranslate/leadText
        'slug_content': '',  # slug
        'link_content': '',  # https://cointelegraph.com/news/ + slug
        'raw_content': '',
        'keyword_ranking': {},
        'author': '',  # author/authorTranslates/name
        'id_author': '',  # author/authorTranslates/id
        'link_author': '',  # https://cointelegraph.com/authors/ + slug_author
        'slug_author': '',  # author/slug
        'tag': '',
        'link_tag': '',
        'published': '',  # postTranslate/published
        'date': '',
        'timestamp': '',
        'latest': 0,
        'approve': 1,
    }
    return data


class CardanoscraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient["cardanoNews"]
        self.postContents = self.myDatabase['allNews']
        # self.postContents = self.myDatabase['allNews1']
        self.testCarda = self.myDatabase['testAllNews2']
        self.new_posts = []

    # ================================================
    # handle put data to GraphQl
    # ================================================
    def close_spider(self, spider):
        for index, value in enumerate(self.new_posts):
            utils.show_message(message='Latest Post for today', colour='okblue', data={index: value})
        print(f"{color['warning']}Cardano Crawl Completed!{color['endc']}")

    # call every item pipeline component
    def process_item(self, item, spider):
        print(f"\n{color['okblue']}Cardano Pipeline handling...{color['endc']}")
        # ================================================
        # we have two flows of data
        # 1st for posts, 2nd for contents
        # if run crawlAllCardanoNews, insert data into allNews table
        # ================================================
        if item['source'] == 'cardano':
            if 'title' in item:
                item['avatars'] = self.handle_link_avatars(item['avatars'])
                if self.postContents.find_one({'link_post': item['link_post']}):
                    self.update_table(self.postContents, item)
                else:
                    utils.insert_into_table(self.postContents, item)
                    self.new_posts.append(item['link_post'])
            elif 'raw_content' in item:
                utils.handle_datetime(item, item['post_time'])
                utils.text_ranking(item, item['raw_content'])
                self.update_raw_content(self.postContents, item)
                print(f"{color['warning']}Imported raw_content to {utils.get_table(self.postContents)} {color['endc']}\n")
        # print(f"{color['warning']}This is{color['endc']}Item...{color['okgreen']}{item}{color['endc']}")
        return item

    def update_table(self, table, data):
        query = {
            "link_post": data['link_post'].strip(),
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating Latest Cardano page into {get_table(table)}{color['endc']} ")
            utils.update_success_notify(table)
        time.sleep(1)

    def update_raw_content(self, table, data):
        query = {
            "link_post": data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating Raw Content into {get_table(table)}{color['endc']} for post: {data['link_content']}")
            utils.update_rawcontent_notify(table, data)
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


class IohkScraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient["cardanoNews"]
        self.iohk_sample1 = self.myDatabase['iohkSample']
        # self.iohk_sample1 = self.myDatabase['iohkSample2']
        self.new_posts = []

    def close_spider(self, spider):
        for index, value in enumerate(self.new_posts):
            utils.show_message(message='Latest Post for today', colour='okblue', data={index: value})
        print(f"{color['warning']}IOHK Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        print(f"\n{color['okblue']}IOHK Pipeline handling...{color['endc']}\n")
        if item['source'] == 'iohk':
            self.iohk_get_posts(item)
        # elif item['source'] == 'coindesk':
        #     return item
        return item

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
            iohk_all_posts = utils.initialize_sample_data()
            author_info = post['author']
            iohk_all_posts['publish_date'] = post['publish_date']
            iohk_all_posts['timestamp'] = utils.handle_datetime(iohk_all_posts, post['publish_date']),
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

            keyword_ranking = utils.text_ranking(iohk_all_posts, iohk_all_posts['raw_content'])

            print(f"Current page: {iohk_all_posts['current_url_page']}")
            print(f"Current post: {iohk_all_posts['title']}")
            iohk_all_posts['raw_data'] = post
            iohk_all_posts['keyword_ranking'] = keyword_ranking
            if self.iohk_sample1.find_one({'link_content': iohk_all_posts['link_content']}):
                self.update_iohk(self.iohk_sample1, iohk_all_posts)
                sleep(.05)
            else:
                utils.insert_into_table(self.iohk_sample1, iohk_all_posts)
                self.new_posts.append(iohk_all_posts['link_content'])
                sleep(.05)

    def update_iohk(self, table, data):
        query = {
            'link_content': data['link_content'].strip()
        }
        if table.update_one(query, {'$set': data}):
            # print(f"{color['okcyan']}Updating {get_table(table)} table{color['endc']}\n")
            utils.update_success_notify(table)
        time.sleep(.05)


class CoindeskScraperPipeline(object):
    def __init__(self):
        self.myDatabase = mongoClient['cardanoNews']
        self.coindesk = self.myDatabase['coindeskSample']
        # self.coindesk = self.myDatabase['coindeskLatest1']
        self.url = 'https://www.coindesk.com{}'
        self.new_posts = []

    def close_spider(self, spider):
        utils.handle_empty_content(self.coindesk, self.new_posts)
        print(f"{color['warning']}Coindesk Crawl Completed!{color['endc']}")

    # ================================================
    # classify flow of data and push data to mongoDb
    # ================================================
    def process_item(self, item, spider):
        print(f"{color['okblue']}Coindesk Pipeline handling...{color['endc']}\n")
        if item['source'] == 'coindesk':
            if 'title' in item:
                self.handle_links(item)
                utils.handle_datetime(item, item['date'])
                if self.coindesk.find_one({'link_content': item['link_content']}):
                    self.update_table(self.coindesk, item)
                else:
                    utils.insert_into_table(self.coindesk, item)
                    utils.show_message('Post', 'okblue', item['link_content'])
                    self.new_posts.append(item['link_content'])
            elif 'raw_data' in item:
                # utils.show_message('raw_data', 'fail', item['slug_content'])
                self.insert_raw_content(self.coindesk, item)
        elif item['source'] == 'coindeskLatestNews':
            if 'next' in item:
                self.coindesk_get_post(item)
            elif 'raw_content' in item:
                self.coindesk_get_raw_content(self.coindesk, data=item)
        return item

    def update_table(self, table, data):
        query = {
            'link_content': data['link_content']
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)
        time.sleep(1)

    def insert_raw_content(self, table, data):
        slug_content = data['slug_content']
        # many kinds of public post date
        self.handle_datetime(data)
        # some Video post had no content
        self.handle_content(data)
        data['raw_data'] = ''
        query = {
            "slug_content": slug_content,
        }
        if table.update_one(query, {'$set': data}):
            print(f"{color['okgreen']}Update raw_content success!{color['endc']} in {self.url.format('/' + str(slug_content)) }")
        time.sleep(1)

    def update_latest_news(self, table, data):
        query = {
            'slug_content': data['slug_content']
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)

    def coindesk_get_post(self, data):
        posts = data['posts']
        for post in posts:
            coindesk_sample_data = sample_data()
            img = post['images']['images']
            coindesk_sample_data['title'] = post['title']
            coindesk_sample_data['subtitle'] = post['text']
            if 'desktop' in img:
                coindesk_sample_data['link_img'] = img['desktop']['src']
            elif 'mobile' in img:
                coindesk_sample_data['link_img'] = img['mobile']['src']
            elif 'mobile@2x' in img:
                coindesk_sample_data['link_img'] = img['mobile@2x']['src']
            elif 'mobile@3x' in img:
                coindesk_sample_data['link_img'] = img['mobile@3x']['src']
            elif 'full' in img:
                coindesk_sample_data['link_img'] = img['full']['src']
            else:
                coindesk_sample_data['link_img'] = ''
            coindesk_sample_data['slug_content'] = post['slug']
            coindesk_sample_data['link_content'] = self.url.format('/' + str(post['slug']))
            coindesk_sample_data['author'] = post['authors'][0]['name']
            coindesk_sample_data['slug_author'] = post['authors'][0]['slug']
            coindesk_sample_data['link_author'] = self.url.format('/author/' + str(post['authors'][0]['slug']))
            coindesk_sample_data['tag'] = post['tag']['name']
            coindesk_sample_data['link_tag'] = self.url.format('/' + str(post['tag']['slug']))
            coindesk_sample_data['published'] = post['date']
            coindesk_sample_data['timestamp'] = datetime.strptime(post['date'], '%Y-%m-%dT%H:%M:%S').timestamp()
            if self.coindesk.find_one({'slug_content': coindesk_sample_data['slug_content']}):
                self.update_latest_news(self.coindesk, coindesk_sample_data)
                time.sleep(.05)
            else:
                utils.insert_into_table(self.coindesk, data=coindesk_sample_data)
                self.new_posts.append(coindesk_sample_data['link_content'])
                time.sleep(.05)

    def coindesk_get_raw_content(self, table, data):
        raw_content = data['raw_content']
        data['clean_content'] = utils.clean_html_tags(data['raw_content'])
        utils.show_message('raw_content', 'okgreen', raw_content)
        keyword_ranking = utils.text_ranking(data, raw_content)
        data['keyword_ranking'] = keyword_ranking
        data['raw_data'] = ''
        if table.find_one({'slug_content': data['slug_content']}):
            self.update_latest_news(self.coindesk, data=data)
        sleep(.05)

    def standard_date(self, date, data):
        standard_date = data[date].split(':')[:2]
        standard_date = ':'.join(standard_date)
        return standard_date

    def handle_content(self, data):
        data['raw_content'] = utils.decode_html_content(data['raw_content'])
        data['clean_content'] = utils.clean_html_tags(data['raw_content'])
        data['keyword_ranking'] = utils.text_ranking(data, data['raw_content'])
        utils.show_message('keywords', 'warning', data['keyword_ranking'])

    def handle_datetime(self, data):
        data['timestamp'] = datetime.strptime(str(data['date']), "%Y-%m-%dT%H:%M:%S").timestamp()

    def handle_links(self, data):
        data['link_content'] = self.url.format(str(data['link_content']))
        data['link_tag'] = self.url.format(str(data['link_tag']))
        data['link_author'] = self.url.format(str(data['link_author']))


class CoinTelegraphScraperPipeline(object):
    def __init__(self):
        self.url = 'https://cointelegraph.com/{}'
        self.myDatabase = mongoClient['cardanoNews']
        self.coinTele = self.myDatabase['coinTelegraphSample']
        # self.coinTele = self.myDatabase['coinTelegraphSampleTest']
        # self.coinTele = self.myDatabase['coinTelegraphBlockchain']
        # self.coinTele = self.myDatabase['coinTelegraphLitecoin2']
        # self.coinTele = self.myDatabase['coinTelegraphLatest']
        self.new_posts = []

    def close_spider(self, spider):
        utils.handle_empty_content(self.coinTele, self.new_posts)
        print(f"{color['warning']}CoinTelegraph Crawl Completed!{color['endc']}")

    def process_item(self, item, spider):
        if item['source'] == 'coinTelegraph':
            if 'title' in item:
                print(f"{color['okblue']}Cointelegraph Pipeline handling...{color['endc']}\n")
                self.cointele_get_post(item)
            elif 'raw_data' in item:
                self.get_content(item)
        # return item

    # ================================================
    # decode html tag and clean content
    # get keyword ranking
    # ================================================
    def get_content(self, data):
        data_ = data['raw_data']
        # decode_html_content = codecs.decode(data_, 'unicode-escape')
        decode_html_content = codecs.decode(data_, 'unicode-escape')
        # utils.show_message('decode_html_content', 'okcyan', decode_html_content)

        # get clean content for keywords ranking
        data_content = decode_html_content.split('fullText="')
        raw_content = data_content[1].split('audio="')[0]

        decode1 = utils.decode_html_content(raw_content)
        # utils.show_message('decode1', 'okgreen', decode1)
        # utils.show_message('decode_html_content', 'okcyan', raw_content)

        raw_content = raw_content.split('<template data-name="subscription_form"')[0]
        clean_content = remove_tags(raw_content)
        # set keywords
        data['keyword_ranking'] = utils.text_ranking(data, clean_content)
        if 'tag' in data:
            tag = data['tag']
            data['keyword_ranking'][tag] = '6.5'

        utils.show_message('keyword_ranking', 'warning', data['keyword_ranking'])

        data['raw_content'] = str(raw_content)
        data['clean_content'] = str(clean_content)
        data['raw_data'] = ''
        self.update_news(self.coinTele, data)

    def cointele_get_post(self, data):
        for post in data['data']:
            cointele_sample_data = sample_data()
            post_badge_title = post['postBadge']['postBadgeTranslates'][0]['title'].lower().strip()
            cointele_sample_data['id'] = post['id']
            cointele_sample_data['title'] = post['postTranslate']['title'].strip()
            cointele_sample_data['subtitle'] = str(post['postTranslate']['leadText']).strip()
            cointele_sample_data['link_img'] = post['postTranslate']['avatar'].strip()
            cointele_sample_data['views'] = post['views']
            cointele_sample_data['id_post_translate'] = post['postTranslate']['id']  # postTranslate/id
            cointele_sample_data['description'] = str(post['postTranslate']['leadText']).strip()  # postTranslate/leadText
            if post_badge_title == 'experts answer' or post_badge_title == 'explained':
                cointele_sample_data['link_content'] = self.url.format('explained/' + str(post['slug']))
            else:
                cointele_sample_data['link_content'] = self.url.format('news/' + str(post['slug']))  # https://cointelegraph.com/news/ + slug
            cointele_sample_data['slug_content'] = post['slug'].strip()  # slug
            # 'raw_content': '',
            # 'keyword_ranking': '',
            cointele_sample_data['author'] = post['author']['authorTranslates'][0]['name'].strip()  # author/authorTranslates/name
            cointele_sample_data['id_author'] = post['author']['authorTranslates'][0]['id'].strip()  # author/authorTranslates/id
            cointele_sample_data['link_author'] = self.url.format('authors/' + str(post['author']['slug'])).strip()  # https://cointelegraph.com/authors/ + slug_author
            cointele_sample_data['slug_author'] = post['author']['slug'].strip()  # author/slug
            if 'tag' in data:
                tag = data['tag']
                tag_ = self.handle_tag(tag)
                cointele_sample_data['tag'] = tag_
                if tag_ != '':
                    cointele_sample_data['link_tag'] = 'https://cointelegraph.com/tags/' + str(tag_)
                    # cointele_sample_data['keyword_ranking'][tag_] = '5'
                else:
                    cointele_sample_data['link_tag'] = ''
            cointele_sample_data['source'] = 'coinTelegraph'
            utils.handle_utc_datetime(post['postTranslate']['published'], cointele_sample_data)
            if self.coinTele.find_one({'link_content': cointele_sample_data['link_content']}):
                self.update_news(self.coinTele, cointele_sample_data)
                time.sleep(1)
            else:
                utils.insert_into_table(self.coinTele, cointele_sample_data)
                utils.show_message('Post', 'okblue', cointele_sample_data['link_content'])
                self.new_posts.append(cointele_sample_data['link_content'])
                time.sleep(1)

    def update_news(self, table, data):
        query = {
            'link_content': data['link_content'],
        }
        if table.update_one(query, {'$set': data}):
            utils.update_success_notify(table)

    def handle_tag(self, tag):
        if tag == '4':
            tag_ = 'bitcoin'
            return tag_
        elif tag == '26':
            tag_ = 'litecoin'
            return tag_
        elif tag == '581':
            tag_ = 'ripple'
            return tag_
        elif tag == '553':
            tag_ = 'ethereum'
            return tag_
        elif tag == '11':
            tag_ = 'blockchain'
            return tag_
        elif tag == '414':
            tag_ = 'business'
            return tag_
        else:
            utils.show_message('other tag', 'fail', 1)
