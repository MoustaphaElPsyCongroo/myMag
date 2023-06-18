#!/usr/bin/python3
"""Cronjob function to get new random headers from ScrapeOPS API"""
from decouple import config
import requests
import json

SCRAPEOPS_API_KEY = config('SCRAPEOPS_API_KEY')


def get_random_header_list():
    """Get new random headers from API and save them in headers.json"""
    headers = fetch_random_headers_list()

    with open('headers.json', 'w') as f:
        json.dump(headers, f)


def fetch_random_headers_list():
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
