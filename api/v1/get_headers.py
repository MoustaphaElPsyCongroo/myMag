#!/usr/bin/python3
"""Get a collection of random headers using Scrapeops' Headers API"""
from decouple import config
import requests
import json

SCRAPEOPS_API_KEY = config('SCRAPEOPS_API_KEY')


# On sauvegardera ces headers dans un simple file
def get_headers_list():
    """Fetch Scrapeops' Headers API for random headers"""
    try:
        response = requests.get(
            url='http://headers.scrapeops.io/v1/browser-headers',
            params={
                'api_key': SCRAPEOPS_API_KEY,
                'num_results': '30'
            })
    except Exception as e:
        return []
    json_response = response.json()
    return json_response.get('result')


headers = get_headers_list()

with open('headers.json', 'w') as f:
    json.dump(headers, f)
