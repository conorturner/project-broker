"""
Contains the integration classes and functions for the Capital.com API
"""

import json
import logging
from base64 import b64encode, b64decode

import aiohttp
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from cachetools import TTLCache

from app.modules.broker_integrations.base_integration import BaseIntegration, NewPositionDetails

cache = TTLCache(maxsize=10, ttl=600)  # Time limited cache for access token
store = {}  # Share token store across all instances of CapitalClient


class CapitalAPIException(Exception):
    """Custom exception class for capital.com REST API errors."""

    def __init__(self, response, status_code, text):
        self.code = 0
        try:
            json_res = json.loads(text)
        except ValueError:
            self.message = f"Invalid JSON error message from Capital.com: {response.text}"
        else:
            self.code = json_res["errorCode"]
        self.status_code = status_code
        self.response = response
        self.request = getattr(response, "request", None)

    def __str__(self):
        return f"APIError(status code={self.status_code}) || Capital.com Error: {self.code}"


def encrypt_password(password, key):
    """Encrypt API Key Password using RSA."""
    key = b64decode(key)
    key = RSA.importKey(key)
    cipher = PKCS1_v1_5.new(key)
    ciphertext = b64encode(cipher.encrypt(bytes(password, "utf-8")))
    return ciphertext


class CapitalIntegration(BaseIntegration):
    """Class for the capital.com API integration."""
    def __init__(self, username, api_key, password, demo=False):
        """Initialise client object with credentials and live/dev endpoint."""
        self.username = username
        self.api_key = api_key
        self.password = password
        self.log = logging.getLogger('CapitalClient')

        if demo is False:
            self.server = "https://api-capital.backend-capital.com"
        else:
            self.server = "https://demo-api-capital.backend-capital.com"

    async def __auth_request(self, method, path, **kwargs):
        """Wrapper method for making authenticated API requests."""
        headers = await self.__headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
            del kwargs['headers']

        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.server + path, headers=headers, **kwargs) as resp:
                try:
                    return await resp.json()
                except:
                    self.log.error(await resp.text())
                    raise

    async def __make_request(self, method, path, **kwargs):
        """Wrapper method for making API requests, returns both response and response headers."""
        async with aiohttp.ClientSession() as session:
            async with session.request(method, self.server + path, **kwargs) as resp:
                try:
                    return resp.headers, await resp.json()
                except:
                    self.log.error(await resp.text())
                    raise

    async def __token(self):
        """Create a session using the stored credentials."""
        if 'access_token' in cache:
            return cache['access_token']

        encryption_key, timestamp = await self.__get_encryption_key()
        string_encrypt = f"{self.password}|{timestamp}"
        encrypted_password = str(encrypt_password(string_encrypt, encryption_key), "utf-8")
        body = {
            "identifier": self.username,
            "password": encrypted_password,
            "encryptedPassword": True,
        }
        headers, _ = await self.__make_request("POST", "/api/v1/session", json=body, headers={
            "X-CAP-API-KEY": self.api_key,
            "content-type": "application/json",
        })
        cache['access_token'] = (headers["X-SECURITY-TOKEN"], headers["CST"])

        return cache['access_token']

    async def __headers(self):
        """Returns headers with auth token."""
        token, cst = await self.__token()

        return {
            "X-SECURITY-TOKEN": token,
            "CST": cst,
            "content-type": "application/json",
        }

    async def __get_encryption_key(self):
        """Request encryption key from API."""
        _, data = await self.__make_request("GET", "/api/v1/session/encryptionKey", headers={
            "X-CAP-API-KEY": self.api_key,
            "content-type": "application/json",
        })

        return data["encryptionKey"], data["timeStamp"]

    async def __confirmation(self, deal_reference):
        """Get deal confirmation object from API."""
        url = f"/api/v1/confirms/{deal_reference}"
        return self.__auth_request("GET", url)

    async def all_accounts(self):
        """List accounts under this API key."""
        return (await self.__auth_request("GET", "/api/v1/accounts"))['accounts']

    async def open_position(self, epic: str, details: NewPositionDetails):
        """Open a new position."""
        data = {
            "epic": epic,
            "direction": details.direction.upper(),
            "size": str(details.size),
            "guaranteedStop": False,
            "trailingStop": False,
        }

        if details.stop is not None:
            data.update({"stopDistance": details.stop})
        if details.limit is not None:
            data.update({"profitDistance": details.limit})

        data = await self.__auth_request("post", "/api/v1/positions", json=data)
        final_data = await self.__confirmation(data["dealReference"])
        return final_data

    async def close_position(self, deal_id, size, direction):
        """Close a position using the deal_id."""
        url = f"{self.server}/api/v1/positions/{deal_id}"
        data = await self.__auth_request("DELETE", url)
        final_data = await self.__confirmation(data["dealReference"])
        return final_data

    async def prices(self, epic, resolution="MINUTE", limit=10):
        """Returns historical prices for a particular instrument"""
        url = f"/api/v1/prices/{epic}?resolution={resolution}&max={limit}"
        data = await self.__auth_request("GET", url)
        return data

    async def search_instruments(self, search_term):
        """Returns the details of the given markets."""
        data = await self.__auth_request("GET", f"/api/v1/markets?searchTerm={search_term}")
        return data

    async def get_position(self, deal_id):
        raise NotImplementedError()

    async def get_positions(self):
        raise NotImplementedError()
