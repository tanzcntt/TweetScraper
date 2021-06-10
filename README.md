# I. Twitter Scraper #
# Introduction #
`TweetScraper` can get tweets from [Twitter Search](https://twitter.com/explore). 
It is built on [Scrapy](http://scrapy.org/) without using [Twitter's APIs](https://dev.twitter.com/rest/public).
The crawled data is not as *clean* as the one obtained by the APIs, but the benefits are you can get rid of the API's rate limits and restrictions. Ideally, you can get all the data from Twitter Search.

**WARNING:** please be polite and follow the [crawler's politeness policy](https://en.wikipedia.org/wiki/Web_crawler#Politeness_policy).
 

# Installation #
1. Install `conda`, you can get it from [miniconda](https://docs.conda.io/en/latest/miniconda.html). The tested python version is `3.7`. 

2. Install selenium python bindings: https://selenium-python.readthedocs.io/installation.html. (Note: the `KeyError: 'driver'` is caused by wrong setup)

3. For ubuntu or debian user, run:
    
    ```
    $ bash install.sh
    $ conda activate tweetscraper
    $ scrapy list
    $ #If the output is 'TweetScraper', then you are ready to go.
    ```

    the `install.sh` will create a new environment `tweetscraper` and install all the dependencies (e.g., `firefox-geckodriver` and `firefox`),

# Usage #
1. Change the `USER_AGENT` in `TweetScraper/settings.py` to identify who you are
	
		USER_AGENT = 'your website/e-mail'

2. In the root folder of this project, run command like: 

		scrapy crawl TweetScraper -a query="foo,#bar"

	where `query` is a list of keywords seperated by comma and quoted by `"`. The query can be any thing (keyword, hashtag, etc.) you want to search in [Twitter Search](https://twitter.com/search-home). `TweetScraper` will crawl the search results of the query and save the tweet content and user information. 

3. The tweets will be saved to disk in `./Data/tweet/` in default settings and `./Data/user/` is for user data. The file format is JSON. Change the `SAVE_TWEET_PATH` and `SAVE_USER_PATH` in `TweetScraper/settings.py` if you want another location.


# Acknowledgement #
Keeping the crawler up to date requires continuous efforts, please support our work via [opencollective.com/tweetscraper](https://opencollective.com/tweetscraper).


# License #
TweetScraper is released under the [GNU GENERAL PUBLIC LICENSE, Version 2](https://github.com/jonbakerfish/TweetScraper/blob/master/LICENSE)


# start on local #
cd TweetScraper
conda activate tweetscraper
./start.sh >> logs/command.log 2>&1 &
./push.sh >> logs/pushdhunt.log 2>&1 &

//sudo docker-compose -d up

# II. user-scraper #
# Introduction #
`user-scraper` can get all user through specific [User Page](https://twitter.com/elonmusk). 

Main purposes: 
+ follow twitter users
+ statistic and visualize account growth,...

# Usage #
1. Open this project and run command like:

		python3 run_command.py -t 5 -u 100
   
		-t: is the number of thread
		-u: is the number of User we want to crawl data

This command will start with `5 threads` at the same time and crawl `100 users` taken from the [followUser](http://localhost:8081/db/twitterdata/followUser) in mongodb. Free to change `thread & user`

2. See the results in collection [trackUser](http://localhost:8081/db/twitterdata/trackUser) 

# III. CardanoScraper #
# Introduction #

`CardanoScraper` will crawl all data through category: [News and Announcements](https://forum.cardano.org/c/english/announcements/13) on forum.cardano.org

Main purposes:
+ Get *latest posts*, *all posts* and *Content* of this posts
+ Implement Natural Language Processing use `spacy` package to
  + Mark up the words in text format for a particular paragraph depended on its Context and Definition
  + Extract and rank keywords follow the specific paragraph
+ Handle many functions behind this phase. Developing...

# Installation #

1. Install `requirements` 
+ pip install -r requirements.txt
  
2. Install `NLP trained model` for English
+ [python -m spacy download en_core_web_sm](https://spacy.io/models/en)


# Usage #
1. Run demo ranking keyword in `text_rank_4_key.py`
	
		python3 text_rank_4_key.py
	
*window_size* is custom, better in range 5 - 10

*candidate_post* is custom follow the link to set [POS tag](https://spacy.io/usage/linguistic-features): PROPN, NOUN, VERB,...,

*get_keyword*(number=10) to get *top number* of these keywords

, ...

2. Open `CardanoScraper` and run commands:

Remember to activate the environment firstly,

Run these commands do not need to follow the sequence.

This command crawls and updates 1 Latest page on [Cardano Forum](https://forum.cardano.org/c/english/announcements/13):
		
		scrapy crawl crawlLatestCarda

This command crawls and updates all pages [Cardano Forum](https://forum.cardano.org/c/english/announcements/13):

		scrapy crawl crawlAllCarda
