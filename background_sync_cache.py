import os
import json
import requests
from apscheduler.schedulers.background import BackgroundScheduler
from cachetools import cached, TTLCache
import time

cache = TTLCache(maxsize=100, ttl=600)
API_URL = "https://your-api-url.com/athlete/metrics"
API_KEY = "YOUR_API_KEY"

def fetch_cloud_data():
    try:
        response = requests.get(API_URL, headers={"Authorization": f"Bearer {API_KEY}"})
        if response.status_code == 200:
            cloud_data = response.json()
            with open("athlete_data.json", 'w') as f:
                json.dump(cloud_data, f, indent=2)
            print("✅ Synced from cloud.")
        else:
            print(f"⚠️ Sync failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

@cached(cache)
def get_cached_api_data():
    try:
        response = requests.get(API_URL, headers={"Authorization": f"Bearer {API_KEY}"})
        return response.json() if response.status_code == 200 else None
    except Exception as e:
        print(f"❌ API Error: {str(e)}")
        return None

scheduler = BackgroundScheduler()
scheduler.add_job(fetch_cloud_data, 'interval', hours=1)
scheduler.start()

while True:
    time.sleep(1)
