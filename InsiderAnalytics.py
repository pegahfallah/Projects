import http.client
import json
import os
from dotenv import load_dotenv


class CampaignAnalytics:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('AUTH_KEY')
        if not self.api_key:
            raise ValueError("AUTH_KEY is not set in the .env file.")
        self.base_url = "analytics.api.useinsider.com"
        self.headers = {
            'X-INS-AUTH-KEY': self.api_key
        }
        self.conn = http.client.HTTPSConnection(self.base_url)

    def fetch_campaigns(self, page=1, per_page=5):
        """Fetch the list of campaigns."""
        endpoint = f"/email/v1/campaign/list?page={page}&perPage={per_page}"
        self.conn.request("GET", endpoint, '', self.headers)
        response = self.conn.getresponse()
        if response.status != 200:
            raise Exception(f"Failed to fetch campaigns: {response.status} {response.reason}")
        result = response.read().decode("utf-8")
        data = json.loads(result)
        return data.get('data', [])

    def fetch_campaign_statistics(self, campaign_id, start_time):
        """Fetch statistics for a specific campaign."""
        endpoint = f"/email/v1/campaign/statistics?campaignId={campaign_id}&startTime={start_time}"
        self.conn.request("GET", endpoint, '', self.headers)
        response = self.conn.getresponse()
        if response.status != 200:
            raise Exception(f"Failed to fetch campaign statistics: {response.status} {response.reason}")
        result = response.read().decode("utf-8")
        data = json.loads(result)
        return data

    def get_all_campaigns_with_analytics(self, start_time):
        """Get all campaigns with their analytics."""
        campaigns = self.fetch_campaigns()
        campaign_analytics = {}
        for campaign in campaigns:
            campaign_id = campaign['id']
            campaign_name = campaign['campaignName']
            print(f"Fetching analytics for Campaign ID: {campaign_id}, Name: {campaign_name}")
            analytics = self.fetch_campaign_statistics(campaign_id, start_time)
            campaign_analytics[campaign_id] = {
                "campaign_name": campaign_name,
                "analytics": analytics
            }
        return campaign_analytics


if __name__ == "__main__":
    analytics = CampaignAnalytics()
    
    try:
        start_time = 1683726709
        all_campaign_analytics = analytics.get_all_campaigns_with_analytics(start_time)
        print(json.dumps(all_campaign_analytics, indent=4))
    except Exception as e:
        print(f"An error occurred: {e}")
