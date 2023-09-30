"""This module contains components of the IG Rest API integration."""

import json
import logging
from datetime import datetime

import aiohttp
import requests
from cachetools import TTLCache
import pandas as pd

cache = TTLCache(maxsize=10, ttl=60)  # Time limited cache for access token
store = {}  # Share token store across all instances of IgAPI


async def refresh_token(r_token, api_key):
    """Update access token using current refresh token"""
    url = "https://demo-api.ig.com/gateway/deal/session/refresh-token"

    payload = json.dumps({
        "refresh_token": r_token
    })
    headers = {
        'X-IG-API-KEY': api_key,
        'Version': '1',
        'Content-Type': 'application/json'
    }

    async with aiohttp.ClientSession() as session:
        async with session.request("POST", url, headers=headers, data=payload) as resp:
            return await resp.json()


def parse_ig_point(point):
    """Flatten historical data response."""
    if 'ask' not in point['openPrice'] or 'bid' not in point['openPrice']:
        return None

    return {
        'time_stamp': datetime.fromisoformat(point['snapshotTimeUTC']),
        'open_ask': point['openPrice']['ask'],
        'open_bid': point['openPrice']['bid'],
        'close_ask': point['closePrice']['ask'],
        'close_bid': point['closePrice']['bid'],
        'high_ask': point['highPrice']['ask'],
        'high_bid': point['highPrice']['bid'],
        'low_ask': point['lowPrice']['ask'],
        'low_bid': point['lowPrice']['bid'],
        'volume': point['lastTradedVolume']
    }


class IgAPI:
    """Class containing methods for interacting with the IG REST API."""

    def __init__(self, api_key, account_id, username, password, demo=True):
        self.api_key = api_key
        self.username = username
        self.password = password
        self.account_id = account_id
        if demo:
            self.url = "https://demo-api.ig.com/gateway/deal"
        else:
            self.url = "https://api.ig.com/gateway/deal"

        self.log = logging.getLogger('IgAPI')

    async def __token(self):
        """Getter for access token."""
        if 'access_token' in cache:
            return cache['access_token']
        if 'refresh_token' in store:
            token_response = await refresh_token(store['refresh_token'], self.api_key)
            store['refresh_token'] = token_response['refresh_token']
            cache['access_token'] = token_response['access_token']
            return token_response['access_token']

        url = "https://demo-api.ig.com/gateway/deal/session"

        payload = json.dumps({
            "identifier": self.username,
            "password": self.password
        })
        headers = {
            'X-IG-API-KEY': self.api_key,
            'Version': '3',
            'Content-Type': 'application/json'
        }

        async with aiohttp.ClientSession() as session:
            async with session.request("POST", url, headers=headers, data=payload) as resp:
                resp = await resp.json()

        store['refresh_token'] = resp['oauthToken']['refresh_token']
        cache['access_token'] = resp['oauthToken']['access_token']

        return cache['access_token']

    async def __headers(self, version=2):
        """Getter for shared headers."""
        return {
            'X-IG-API-KEY': self.api_key,
            'Version': str(version),
            'IG-ACCOUNT-ID': self.account_id,
            'Authorization': f'Bearer {await self.__token()}'
        }

    async def __make_request(self, version, method, path, **kwargs):
        """Wrapper method for making authenticated API requests."""
        headers = await self.__headers(version)
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.url + path, headers=headers, **kwargs) as resp:
                if not 200 <= resp.status < 300:
                    raise Exception(f'Status Code: {resp.status} \n {await resp.text()}')
                try:
                    return await resp.json()
                except:
                    self.log.error(await resp.text())
                    raise

    async def get_positions(self):
        """Get list of open positions."""
        return await self.__make_request(2, "GET", '/positions')

    async def search_market(self, term):
        """Search market by keyword."""
        return await self.__make_request(1, "GET", '/markets', params={'searchTerm': term})

    async def get_deal_details(self, deal_reference):
        """Get details of a deal."""
        return await self.__make_request(1, "GET", f'/confirms/{deal_reference}')

    async def open_position(self, direction: str, size: int, epic: str, expiry='-', limit=None, stop=None,
                            currency='GBP'):
        """Open a new position"""
        payload = {
            "direction": direction,
            "size": size,
            "orderType": "MARKET",
            "epic": epic,
            "currencyCode": currency,
            "expiry": expiry,
            "forceOpen": True,
            "guaranteedStop": False,
            "limitDistance": limit,
            "stopDistance": stop,
        }
        resp = await self.__make_request(2, "POST", '/positions/otc', json=payload)
        return await self.get_deal_details(resp['dealReference'])

    async def close_position(self, deal_id, size, direction):
        """Close a position by deal_id."""
        payload = {
            "dealId": deal_id,
            "epic": None,
            "expiry": None,
            "direction": direction,
            "size": size,
            "level": None,
            "orderType": "MARKET",
            "timeInForce": None,
            "quoteId": None
        }

        resp = await self.__make_request(1, "POST", '/positions/otc',
                                         headers={'_method': 'DELETE', }, json=payload)
        details = await self.get_deal_details(resp['dealReference'])
        while details['status'] != 'CLOSED':
            await self.get_deal_details(resp['dealReference'])

        return details

    async def get_historical_data(self, epic, resolution='DAY', max_values=100, start='2022-02-01', end='2022-02-02'):
        """Get historical data for an instrument."""
        resp = await self.__make_request(3, "GET", f'/prices/{epic}',
                                         params={'resolution': resolution,
                                                 'from': start + "T00:00:00",
                                                 'to': end + "T00:00:00",
                                                 'max': max_values,
                                                 'pageSize': 0})

        if 'prices' not in resp or len(resp['prices']) == 0:
            return

        points = [parse_ig_point(point) for point in resp['prices']]
        return pd.DataFrame(list(filter(None, points)))
