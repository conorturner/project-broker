"""
Contains the integration classes and functions for the Capital.com API
"""

import json
from types import MappingProxyType
from base64 import b64encode, b64decode
import requests
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5


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

    def __str__(self):  # pragma: no cover
        return f"APIError(status code={self.status_code}) || Capital.com Error: {self.code}"


def encrypt_password(password, key):
    """Encrypt API Key Password using RSA."""
    key = b64decode(key)
    key = RSA.importKey(key)
    cipher = PKCS1_v1_5.new(key)
    ciphertext = b64encode(cipher.encrypt(bytes(password, "utf-8")))
    return ciphertext


class Client:
    """Capital.com REST API client class."""
    x_token: str
    cst: str
    enc_key: list

    def __init__(self, username, api_key, password, demo=False):
        """Initialise client object with credentials and live/dev endpoint."""
        self.username = username
        self.api_key = api_key
        self.password = password
        self.headers = {
            "X-CAP-API-KEY": self.api_key,
            "content-type": "application/json",
        }
        if demo is False:
            self.server = "https://api-capital.backend-capital.com"
        else:
            self.server = "https://demo-api-capital.backend-capital.com"

    def __get_encryption_key__(self):
        """Request encryption key from API and store it with the current timestamp in a class variable."""
        url = f"{self.server}/api/v1/session/encryptionKey"
        data = self._make_request("get", url, "")[0]
        self.enc_key = [data["encryptionKey"], data["timeStamp"]]

    def _make_request(self, method: str, url: str, payload: str):
        """Wrapper function for making requests to the REST API."""
        if method == "post":
            response = requests.post(url, headers=self.headers, data=payload, timeout=30)
        elif method == "get":
            response = requests.get(url, headers=self.headers, data=payload, timeout=30)
        elif method == "delete":
            response = requests.delete(url, headers=self.headers, data=payload, timeout=30)
        elif method == "put":
            response = requests.put(url, headers=self.headers, data=payload, timeout=30)
        else:
            raise ValueError(f'Unsupported method: {method}')

        if 200 <= response.status_code or response.status_code > 300:
            raise CapitalAPIException(response, response.status_code, response.text)

        return json.loads(response.text), response.headers

    def _create_session(self):
        """Create a session using the stored credentials."""
        self.__get_encryption_key__()
        url = f"{self.server}/api/v1/session"
        string_encrypt = f"{self.password}|{self.enc_key[1]}"
        encrypted_password = str(
            encrypt_password(string_encrypt, self.enc_key[0]), "utf-8"
        )
        payload = json.dumps(
            {
                "identifier": self.username,
                "password": encrypted_password,
                "encryptedPassword": True,
            }
        )
        data = self._make_request("post", url, payload)[1]
        self.cst = data["CST"]
        self.x_token = data["X-SECURITY-TOKEN"]
        self.headers = {
            "X-SECURITY-TOKEN": self.x_token,
            "CST": self.cst,
            "content-type": "application/json",
        }

    def _confirmation(self, deal_reference):
        """Get deal confirmation object from API."""
        url = f"{self.server}/api/v1/confirms/{deal_reference}"
        return self._make_request("get", url, payload="")[0]

    def all_accounts(self):
        """List accounts under this API key."""
        self._create_session()
        url = f"{self.server}/api/v1/accounts"
        data = self._make_request("get", url, payload="")[0]
        self.__log_out__()
        return data

    def account_pref(self):
        """Returns account preferences, i.e. leverage settings and trading mode."""
        self._create_session()
        url = f"{self.server}/api/v1/accounts/preferences"
        data = self._make_request("get", url, payload="")[0]
        self.__log_out__()
        return data

    def update_account_pref(
            self,
            leverages=MappingProxyType({
                "SHARES": 5,
                "INDICES": 20,
                "CRYPTOCURRENCIES": 2,
            }),
            hedging_mode=False,
    ):
        """Update the account preferences for this API key."""
        self._create_session()
        data = {
            "leverages": leverages,
            "hedgingMode": hedging_mode,
        }
        payload = json.dumps(data)
        url = f"{self.server}/api/v1/accounts/preferences"
        data = self._make_request("put", url, payload=payload)[0]
        self.__log_out__()
        return data

    def change_active_account(self, account_id):
        """Change the active account to the supplier account_id."""
        self._create_session()
        url = f"{self.server}/api/v1/session"
        payload = json.dumps({"accountId": account_id})
        data = self._make_request("put", url, payload=payload)[0]
        self.__log_out__()
        return data

    def all_positions(self):
        """Request a list of all open positions from the API."""
        self._create_session()
        url = f"{self.server}/api/v1/positions"
        data = self._make_request("get", url, payload="")[0]
        self.__log_out__()
        return data

    def open_position(
            self,
            epic,
            direction,
            size,
            guaranteed_stop=False,
            trailing_stop=False,
            stop_level=None,
            stop_distance=None,
            stop_amount=None,
            profit_level=None,
            profit_distance=None,
            profit_amount=None,
    ):
        """Open a new position."""
        self._create_session()
        url = f"{self.server}/api/v1/positions"
        data = {
            "epic": epic,
            "direction": direction.upper(),
            "size": str(size),
            "guaranteedStop": guaranteed_stop,
            "trailingStop": trailing_stop,
        }
        if stop_level is not None:
            data.update({"stopLevel": stop_level})
        if stop_distance is not None:
            data.update({"stopDistance": stop_distance})
        if stop_amount is not None:
            data.update({"stopAmount": stop_amount})
        if profit_level is not None:
            data.update({"profitLevel": profit_level})
        if profit_distance is not None:
            data.update({"profitDistance": profit_distance})
        if profit_amount is not None:
            data.update({"profitAmount": profit_amount})
        payload = json.dumps(data)
        data = self._make_request("post", url, payload=payload)[0]
        final_data = self._confirmation(data["dealReference"])
        self.__log_out__()
        return final_data

    def close_position(self, deal_id):
        """Close a position using the deal_id."""

        self._create_session()
        url = f"{self.server}/api/v1/positions/{deal_id}"
        data = self._make_request("delete", url, payload="")[0]
        final_data = self._confirmation(data["dealReference"])
        self.__log_out__()
        return final_data

    def update_position(
            self,
            deal_id,
            guaranteed_stop=False,
            trailing_stop=False,
            stop_level=None,
            stop_distance=None,
            stop_amount=None,
            profit_level=None,
            profit_distance=None,
            profit_amount=None,
    ):
        """Update a position using the deal_id."""
        data = {"guaranteedStop": guaranteed_stop, "trailingStop": trailing_stop}
        if stop_level is not None:
            data.update({"stopLevel": stop_level})
        if stop_distance is not None:
            data.update({"stopDistance": stop_distance})
        if stop_amount is not None:
            data.update({"stopAmount": stop_amount})
        if profit_level is not None:
            data.update({"profitLevel": profit_level})
        if profit_distance is not None:
            data.update({"profitDistance": profit_distance})
        if profit_amount is not None:
            data.update({"profitAmount": profit_amount})
        payload = json.dumps(data)
        self._create_session()
        url = f"{self.server}/api/v1/positions/{deal_id}"
        data = self._make_request("put", url, payload=payload)[0]
        final_data = self._confirmation(data["dealReference"])
        self.__log_out__()
        return final_data

    def all_working_orders(self):
        """List all working orders."""
        self._create_session()
        url = f"{self.server}/api/v1/workingorders"
        data = self._make_request("get", url, payload="")[0]
        self.__log_out__()
        return data

    def create_working_order(
            self,
            epic,
            direction,
            size,
            level,
            order_type,
            guaranteed_stop=False,
            trailing_stop=False,
            stop_level=None,
            stop_distance=None,
            stop_amount=None,
            profit_level=None,
            profit_distance=None,
            profit_amount=None,
    ):
        """Create a working order."""
        self._create_session()
        url = f"{self.server}/api/v1/workingorders"
        data = {
            "epic": epic,
            "direction": direction.upper(),
            "size": str(size),
            "level": level,
            "type": order_type,
            "guaranteedStop": guaranteed_stop,
            "trailingStop": trailing_stop,
        }
        if stop_level is not None:
            data.update({"stopLevel": stop_level})
        if stop_distance is not None:
            data.update({"stopDistance": stop_distance})
        if stop_amount is not None:
            data.update({"stopAmount": stop_amount})
        if profit_level is not None:
            data.update({"profitLevel": profit_level})
        if profit_distance is not None:
            data.update({"profitDistance": profit_distance})
        if profit_amount is not None:
            data.update({"profitAmount": profit_amount})
        payload = json.dumps(data)
        data = self._make_request("post", url, payload=payload)[0]
        final_data = self._confirmation(data["dealReference"])
        self.__log_out__()
        return final_data

    def update_working_order(
            self,
            deal_id,
            level,
            guaranteed_stop=False,
            trailing_stop=False,
            stop_level=None,
            stop_distance=None,
            stop_amount=None,
            profit_level=None,
            profit_distance=None,
            profit_amount=None,
    ):
        """Update a working order by deal_id."""
        data = {
            "guaranteedStop": guaranteed_stop,
            "trailingStop": trailing_stop,
            "level": level,
        }
        if stop_level is not None:
            data.update({"stopLevel": stop_level})
        if stop_distance is not None:
            data.update({"stopDistance": stop_distance})
        if stop_amount is not None:
            data.update({"stopAmount": stop_amount})
        if profit_level is not None:
            data.update({"profitLevel": profit_level})
        if profit_distance is not None:
            data.update({"profitDistance": profit_distance})
        if profit_amount is not None:
            data.update({"profitAmount": profit_amount})
        payload = json.dumps(data)
        self._create_session()
        url = f"{self.server}/api/v1/workingorders/{deal_id}"
        data = self._make_request("put", url, payload=payload)[0]
        final_data = self._confirmation(data["dealReference"])
        self.__log_out__()
        return final_data

    def delete_working_order(self, deal_id):
        """Delete a working order by deal_id."""
        self._create_session()
        url = f"{self.server}/api/v1/workingorders/{deal_id}"
        data = self._make_request("delete", url, payload="")[0]
        final_data = self._confirmation(data["dealReference"])
        self.__log_out__()
        return final_data

    def all_top(self):
        """Returns all top-level nodes (market categories) in the market navigation hierarchy."""
        self._create_session()
        url = f"{self.server}/api/v1/marketnavigation"
        data = self._make_request("get", url, payload="")
        self.__log_out__()
        return data

    def all_top_sub(self, node_id):
        """Returns all sub-nodes (markets) of the given node (market category) in the market navigation hierarchy."""
        self._create_session()
        url = f"{self.server}/api/v1/marketnavigation/{node_id}?limit=500"
        data = self._make_request("get", url, payload="")
        self.__log_out__()
        return data

    def market_details(self, market):
        """Returns the details of the given markets."""
        self._create_session()
        url = f"{self.server}/api/v1/markets?searchTerm={market}"
        data = self._make_request("get", url, payload="")
        self.__log_out__()
        return data

    def single_market_details(self, epic):
        """Returns the details of the given market."""
        self._create_session()
        url = f"{self.server}/api/v1/markets/{epic}"
        data = self._make_request("get", url, payload="")
        self.__log_out__()
        return data

    def prices(self, epic, resolution="MINUTE", limit=10):
        """Returns historical prices for a particular instrument"""
        self._create_session()
        url = f"{self.server}/api/v1/prices/{epic}?resolution={resolution}&max={limit}"
        data = self._make_request("get", url, payload="")
        self.__log_out__()
        return data

    def client_sentiment(self, market_id):
        """Client sentiment for market"""
        self._create_session()
        url = f"{self.server}/api/v1/clientsentiment/{market_id}"
        data = self._make_request("get", url, payload="")
        self.__log_out__()
        return data

    def __log_out__(self):
        """Delete the active session."""
        requests.delete(f"{self.server}/api/v1/session", headers=self.headers, timeout=5)
        self.headers = {
            "X-CAP-API-KEY": self.api_key,
            "content-type": "application/json",
        }
