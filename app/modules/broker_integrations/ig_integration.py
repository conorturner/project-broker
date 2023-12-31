"""This module contains components of the IG Rest API integration."""

import json
import logging
from datetime import datetime

import aiohttp
from cachetools import TTLCache
import pandas as pd

from app.modules.broker_integrations.base_integration import BaseIntegration, NewPositionDetails
from app.modules.broker_integrations.lightstreamer import async_adapter, LSClient, Subscription

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


class IGAPIException(Exception):
    """Custom exception class for capital.com REST API errors."""

    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

    def __str__(self):
        return f"APIError(status code={self.status_code}) || Error: {self.text}"


class IGIntegration(BaseIntegration):
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

    async def create_session(self):
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
                return await resp.json()

    async def get_session_tokens(self):
        _, headers = await self.__make_request(1, 'GET', '/session?fetchSessionTokens=true', return_headers=True)
        return headers['X-SECURITY-TOKEN'], headers['CST']

    async def __token(self):
        """Getter for access token."""
        if 'access_token' in cache:
            return cache['access_token']
        if 'refresh_token' in store:
            token_response = await refresh_token(store['refresh_token'], self.api_key)
            store['refresh_token'] = token_response['refresh_token']
            cache['access_token'] = token_response['access_token']
            return token_response['access_token']

        resp = await self.create_session()

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

    async def __make_request(self, version, method, path, return_headers=False, **kwargs):
        """Wrapper method for making authenticated API requests."""
        headers = await self.__headers(version)
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.url + path, headers=headers, **kwargs) as resp:
                if not 200 <= resp.status < 300:
                    raise IGAPIException(resp.status, await resp.text())
                try:
                    if return_headers:
                        return (await resp.json()), resp.headers
                    else:
                        return await resp.json()
                except:
                    self.log.error(await resp.text())
                    raise

    async def get_positions(self):
        """Get list of open positions."""
        return await self.__make_request(2, "GET", '/positions')

    async def get_deal_details(self, deal_reference):
        """Get details of a deal."""
        return await self.__make_request(1, "GET", f'/confirms/{deal_reference}')

    async def open_position(self, epic: str, details: NewPositionDetails):
        """Open a new position"""
        payload = {
            "direction": details.direction,
            "size": details.size,
            "orderType": "MARKET",
            "epic": epic,
            "currencyCode": details.currency,
            "expiry": details.expiry,
            "forceOpen": True,
            "guaranteedStop": False,
            "limitDistance": details.limit,
            "stopDistance": details.stop,
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
        while details['status'] != 'CLOSED':  # TODO: a timeout may be needed here to wait for close.
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

    async def get_position(self, deal_id: str):
        raise NotImplementedError()

    async def search_instruments(self, search_term):
        """Search market by keyword."""
        return await self.__make_request(1, "GET", '/markets', params={'searchTerm': search_term})

    async def stream(self, epics):
        stream_get, stream_put = async_adapter()

        ig_session = await self.create_session()
        token, cst = await self.get_session_tokens()
        ls_password = "CST-%s|XST-%s" % (cst, token)
        endpoint = ig_session['lightstreamerEndpoint']
        ls_client = LSClient(endpoint, adapter_set="", password=ls_password)
        ls_client.connect()

        # Making a new Subscription in MERGE mode
        subscription_prices = Subscription(
            mode="MERGE",
            items=[f"MARKET:{epic}" for epic in epics],  # sample CFD epics
            fields=["BID", "OFFER", "UPDATE_TIME"],
        )

        # Adding the "on_price_update" function to Subscription
        subscription_prices.addlistener(stream_put)
        sub_key_prices = ls_client.subscribe(subscription_prices)

        async for item in stream_get:
            try:
                hour, minutes, seconds = tuple(map(int, item['values']['UPDATE_TIME'].split(':')))
                now = datetime.now().replace(hour=hour, minute=minutes, second=seconds, microsecond=0)
                yield {
                    'epic': item['name'].split(':')[1],
                    'ask': float(item['values']['OFFER']),
                    'bid': float(item['values']['BID']),
                    't': now
                }
            except ValueError as e:
                print('Error reading stream', e)
