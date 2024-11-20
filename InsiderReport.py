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
conn.request("GET", "/email/v1/campaign/list?page=2&perPage=10", payload, headers)
res = conn.getresponse()
result = res.read()

decoded_result = result.decode("utf-8")
data = json.loads(decoded_result)

date_format = "%d-%m-%Y %H:%M:%S"

# Initialize lists to store data
details_data = []
isp_data = []
summary_data = []
link_activity_data = []

campaigns = data.get('data', [])

if not campaigns:
    print("No campaigns found in the response.")
    campaigns = []

for campaign in campaigns:
    campaign_id = campaign.get('id', 'Unknown')
    campaign_name = campaign.get('campaignName', 'Unknown')
    campaign_start = campaign.get('startTime', '01-01-1970 00:00:00')

    try:
        dt_object = datetime.strptime(campaign_start, date_format)
        epoch_time = int(dt_object.timestamp())
    except ValueError:
        print(f"Invalid date format for campaign {campaign_id}: {campaign_start}")
        epoch_time = 0

    # Get metrics for each campaign
    stats_url = f"/email/v1/campaign/statistics?campaignId={campaign_id}&startTime={epoch_time}"
    conn.request("GET", stats_url, payload, headers)
    res = conn.getresponse()
    stats_data = res.read()

    try:
        stats = json.loads(stats_data)
    except json.JSONDecodeError:
        print(f"Failed to decode JSON for campaign {campaign_id}")
        continue

    if "data" not in stats:
        print(f"'data' key missing for campaign {campaign_id}")
        continue

    # Extract details data
    details = stats["data"].get("details", {})
    for cid, metrics in details.items():
        details_data.append({
            "Campaign ID": cid,
            "Campaign Name": campaign_name,
            "Start Time": campaign_start,
            **metrics
        })

    # Extract ISP data
    isp = stats["data"].get("isp", [])
    for isp_entry in isp:
        isp_data.append({
            "Campaign ID": campaign_id,
            "Campaign Name": campaign_name,
            **isp_entry.get("metrics", {}),
            "ISP Name": isp_entry.get("name", "Unknown")
        })

    # Extract summary data
    summary = stats["data"].get("summary", {})
    summary_data.append({
        "Campaign ID": campaign_id,
        "Campaign Name": campaign_name,
        **summary
    })

    # Extract link activity data
    link_activity = summary.get("linkActivity", [])
    for link in link_activity:
        link_activity_data.append({
            "Campaign ID": campaign_id,
            "Campaign Name": campaign_name,
            **link
        })

# Convert lists to DataFrames
IN_details_df = pd.DataFrame(details_data)
IN_isp_df = pd.DataFrame(isp_data)
IN_summary_df = pd.DataFrame(summary_data)
IN_link_activity_df = pd.DataFrame(link_activity_data)
