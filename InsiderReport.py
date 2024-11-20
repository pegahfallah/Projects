import http.client
import json
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Set up connection
conn = http.client.HTTPSConnection("analytics.api.useinsider.com")
payload = ''
key = os.getenv('AUTH_KEY')

if not key:
    raise ValueError("AUTH_KEY not found in environment variables.")

headers = {
    'X-INS-AUTH-KEY': key
}

# First API request to get the list of campaigns
conn.request("GET", "/email/v1/campaign/list?page=2&perPage=5", payload, headers)
res = conn.getresponse()
result = res.read()

decoded_result = result.decode("utf-8")
data = json.loads(decoded_result)

date_format = "%d-%m-%Y %H:%M:%S"

campaigns = data.get('data', [])
campaign_analytics = {}

for campaign in campaigns:
    campaign_id = campaign['id']
    campaign_name = campaign['campaignName']
    campaign_start = campaign['startTime']
    dt_object = datetime.strptime(campaign_start, date_format)
    epoch_time = int(dt_object.timestamp())
    print(epoch_time, campaign_id, campaign_name, campaign_start)
    
    # get metrics for each campaign
    stats_url = f"/email/v1/campaign/statistics?campaignId={campaign_id}&startTime={epoch_time}"
    conn.request("GET", stats_url, payload, headers)
    res = conn.getresponse()
    stats_data = res.read()

    print(campaign_id, campaign_name, campaign_start, stats_data.decode("utf-8"), '\n')

# Targeted	Delivered	Delivery (In %)	Opened	Open Rate 	Revenue (Click to order)	Revenue (View to order)

