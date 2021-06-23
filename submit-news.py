import datetime
import getopt
import re
import sys

import pymongo
from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import asyncio

mongoClient = pymongo.MongoClient("mongodb://root:password@localhost:27017/")
myDatabase = mongoClient["cardanoNews"]

news_collection = myDatabase["allNews"]
iohk_collection = myDatabase['iohkSample']
coindesk_collection = myDatabase['coindeskSample']
# Remove 1st argument from the
# list of command line arguments
argumentList = sys.argv[1:]

# Options
options = "d:u:t:s:"

long_options = ["day", "url", "token", "status"]
url = ''
token = ''
day = 0
status = 1
try:
    # Parsing argument
    arguments, values = getopt.getopt(argumentList, options, long_options)
    # checking each argument
    for currentArgument, currentValue in arguments:
        if currentArgument in ("-d", "--day"):
            day = int(currentValue)
        if currentArgument in ("-t", "--token"):
            token = currentValue
        if currentArgument in ("-u", "--url"):
            url = currentValue
        if currentArgument in ("-s", "--status"):
            status = currentValue
except getopt.error as err:
    # output error, and return with an error code
    print(str(err))


async def get_news_from(x, table):
    top_tws = table.find({"approve": 1, "timestamp": {"$gt": 1}, "$or": [{"submit": {"$exists": False}},
                                                                         {"submit": {"$exists": True,
                                                                                     "$ne": status}}]}) \
        .sort([("timestamp", -1)]) \
        .limit(100)
    await push_data_to_dhunt(top_tws, table)


async def push_data_to_dhunt(top_tws, table):
    i = 0
    for tw in top_tws:
        transport = AIOHTTPTransport(url=url, headers={'Authorization': 'Bearer ' + token})

        # Create a GraphQL client using the defined transport
        # client = Client(transport=transport, fetch_schema_from_transport=True)
        # Provide a GraphQL query
        # Execute the query on the transport
        _id = tw['_id']
        tw.pop("_id", None)
        params = {"newsData": tw}
        async with Client(
                transport=transport, fetch_schema_from_transport=True,
        ) as session:
            # Execute single query
            query = gql(
                """
                mutation submitNews($newsData : JSONObject!){
                  submitNews(newsData : $newsData) {
                    id
                    title
                  }
                }
                """
            )

            result = await session.execute(query, variable_values=params)
            print(i, ':', result)
            table.update_one(filter={"_id": _id}, update={"$set": {"submit": status}})
            i += 1


async def main(day_in):
    today = datetime.date.today()
    yesterday = today
    task1 = asyncio.create_task(get_news_from(yesterday, news_collection))
    task2 = asyncio.create_task(get_news_from(yesterday, iohk_collection))
    task3 = asyncio.create_task(get_news_from(yesterday, coindesk_collection))
    await task3
    await task2
    await task1


asyncio.run(main(day))
