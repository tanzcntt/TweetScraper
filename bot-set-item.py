import datetime
import getopt
import re
import sys

from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport

argumentList = sys.argv[1:]

# Options
options = "u:t:"

long_options = ["url", "token"]
url = ''
token = ''
category_dist = {
    "F5: Developer ecosystem": "ecosystem",
    "F4: Fund6 Challenge Setting": "marketing",
    "F4: Local Community Centers": "marketing",
    "F4: Catalyst Value Onboarding": "marketing",
    "F4: Proposer Outreach": "marketing",
    "F4: Distributed Decision Making": "dao",
    "F4: Dapps & Integrations": "dapp",
    "F4: Developer ecosystem": "ecosystem",
    "F5: Scale-UP Cardano's DeFi Ecosystem": "defi",
    "F5: Grow Africa, Grow Cardano": "africa",
    "F5: Fund7 challenge setting": "marketing",
    "F5: Metadata challenge": "metadata",
    "F5: Catalyst value onboarding": "marketing",
    "F5: Distributed decision making": "dao",
    "F5: DApps & Integrations": "dapp",
    "Project Catalyst Problem Sensing": "problem",
    "F5: Proposer outreach": "marketing",
    "https://cardano.ideascale.com/a/ideas/random/campaign-filter/byids/campaigns/25942/stage/unspecified": "dao",
}
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
except getopt.error as err:
    # output error, and return with an error code
    print(str(err))

transport = AIOHTTPTransport(url=url, headers={'Authorization': 'Bearer ' + token})

# Create a GraphQL client using the defined transport
client = Client(transport=transport, fetch_schema_from_transport=True)


def process_content_to_item_type(item):
    if category_dist[item["category"]["title"]]:
        item_type = category_dist[item["category"]["title"]]
        query = gql(
            """
            mutation updateItem($id: String!,$itemType : String!) {
                updateItem(id : $id,itemType : $itemType){
                    id
                    itemType
                }
            }
            """
        )
        result = client.execute(query, {"id": item["id"], "itemType": item_type})
        print(result)


def item_without_type():
    print("Item without type")
    while True:
        query = gql(
            """
            query{
              itemFeed(itemType : "none",take :20){
                id
                title
                description
                imageUri
                itemType
                category{
                  id
                  title,
                  slug
                }
                ideaUser{
                  name,
                  description
                  avatarUri
                  url
                }
                websiteUri
                metadata{
                  value
                  valueNumber
                  name
                }
              }
            }
            """
        )
        result = client.execute(query)
        if result["itemFeed"]:
            for item in result["itemFeed"]:
                process_content_to_item_type(item)
        else:
            break


item_without_type()
