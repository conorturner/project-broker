import os
import unittest
from unittest import mock

from app.modules.broker_integrations.base_integration import NewPositionDetails
from app.modules.broker_integrations.ig_integration import IGIntegration

IG_API_KEY = os.environ.get('IG_API_KEY')
IG_ACCOUNT = os.environ.get('IG_ACCOUNT')
IG_USER = os.environ.get('IG_USER')
IG_PASS = os.environ.get('IG_PASS')


class MockAsyncResponse:
    def __init__(self, text, status):
        self._text = text
        self.status = status

    async def text(self):
        return self._text

    async def json(self):
        return self._text

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self


class IGIntegrationTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_make_request(self):
        """Tests the generic __make_request function using dummy values."""

        api = IGIntegration(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)
        mock_response = {'correct': 'response'}
        with mock.patch('aiohttp.ClientSession.request',
                        return_value=MockAsyncResponse(mock_response, 200)) as mock_request:
            with mock.patch('app.modules.broker_integrations.ig_integration.IGIntegration._IGIntegration__headers',
                            return_value={'example': 'header', 'dict': 1}) as mock_headers:
                result = await api._IGIntegration__make_request(1, "GET", '/markets', params={'searchTerm': 'oil'})

                mock_request.assert_called_with('GET', 'https://demo-api.ig.com/gateway/deal/markets',
                                                headers={'example': 'header', 'dict': 1}, params={'searchTerm': 'oil'})
                mock_headers.assert_called_with(1)
                self.assertEqual(result, mock_response)  # This assertion doesn't add much

    async def test_market_search(self):
        """Tests the search_instruments function in the IG integration."""

        # This response was logged from the real API and represents a real response.
        mock_response = {'markets': [
            {'epic': 'IX.D.DOW.IFD.IP', 'instrumentName': 'Wall Street Cash ($10)', 'instrumentType': 'INDICES',
             'expiry': '-', 'high': 33550.2, 'low': 33478.4, 'percentageChange': 0.08, 'netChange': 25.3,
             'updateTime': '22:00:05', 'updateTimeUTC': '21:00:05', 'bid': 33527.2, 'offer': 33537.0, 'delayTime': 0,
             'streamingPricesAvailable': True, 'marketStatus': 'EDITS_ONLY', 'scalingFactor': 1},
            {'epic': 'IX.D.DOW.IFM.IP', 'instrumentName': 'Wall Street Cash ($2)', 'instrumentType': 'INDICES',
             'expiry': '-', 'high': 33550.2, 'low': 33478.4, 'percentageChange': 0.08, 'netChange': 25.3,
             'updateTime': '22:00:05', 'updateTimeUTC': '21:00:05', 'bid': 33527.2, 'offer': 33537.0, 'delayTime': 0,
             'streamingPricesAvailable': True, 'marketStatus': 'EDITS_ONLY', 'scalingFactor': 1}, ]}

        with mock.patch('app.modules.broker_integrations.ig_integration.IGIntegration._IGIntegration__make_request',
                        return_value=mock_response) as mock_make_request:
            api = IGIntegration(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)
            result = await api.search_instruments('wall street cash')
            self.assertIn('markets', mock_response)
            self.assertIsInstance(result['markets'], list)
            mock_make_request.assert_called_with(1, 'GET', '/markets', params={'searchTerm': 'wall street cash'})

    async def test_open_close_position(self):
        mock_open_response = {'dealReference': '6TJ656UG426TYQR'}

        mock_details_response = {'date': '2023-10-01T17:56:24.114', 'status': 'OPEN', 'reason': 'SUCCESS',
                                 'dealStatus': 'ACCEPTED', 'epic': 'IX.D.SUNNAS.IFS.IP', 'expiry': '-',
                                 'dealReference': 'S2PLQUNQ79STYQR', 'dealId': 'DIAAAAND4HSCUAX',
                                 'affectedDeals': [{'dealId': 'DIAAAAND4HSCUAX', 'status': 'OPENED'}], 'level': 14831.9,
                                 'size': 1.0, 'direction': 'BUY', 'stopLevel': None, 'limitLevel': None,
                                 'stopDistance': None, 'limitDistance': None, 'guaranteedStop': False,
                                 'trailingStop': False, 'profit': None, 'profitCurrency': None}

        mock_close_details_response = {'date': '2023-10-01T17:56:24.421', 'status': 'CLOSED', 'reason': 'SUCCESS',
                                       'dealStatus': 'ACCEPTED', 'epic': 'IX.D.SUNNAS.IFS.IP', 'expiry': '-',
                                       'dealReference': 'S2PLQUNQ79STYQR', 'dealId': 'DIAAAAND4HSCUAX',
                                       'affectedDeals': [{'dealId': 'DIAAAAND4HSCUAX', 'status': 'FULLY_CLOSED'}],
                                       'level': 14817.9, 'size': 1.0, 'direction': 'SELL', 'stopLevel': None,
                                       'limitLevel': None, 'stopDistance': None, 'limitDistance': None,
                                       'guaranteedStop': False,
                                       'trailingStop': False, 'profit': -14.0, 'profitCurrency': 'GBP'}

        api = IGIntegration(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)

        epic = 'IX.D.SUNNAS.IFS.IP'  # Weekend US Tech 100 (GBP1)

        with mock.patch('app.modules.broker_integrations.ig_integration.IGIntegration._IGIntegration__make_request',
                        return_value=mock_open_response) as mock_open_make_request:
            with mock.patch('app.modules.broker_integrations.ig_integration.IGIntegration.get_deal_details',
                            return_value=mock_details_response) as mock_get_deal_details:
                open_position = await api.open_position(epic, NewPositionDetails('BUY', 1))

        with mock.patch('app.modules.broker_integrations.ig_integration.IGIntegration._IGIntegration__make_request',
                        return_value=mock_open_response) as mock_close_make_request:
            with mock.patch('app.modules.broker_integrations.ig_integration.IGIntegration.get_deal_details',
                            return_value=mock_close_details_response) as mock_get_close_deal_details:
                closed_position = await api.close_position(open_position['dealId'], 1, 'SELL')

        # TODO: maybe some assertions on the return values
        # print(open_position)
        # print(closed_position)
        mock_open_make_request.assert_called_with(2, 'POST', '/positions/otc',
                                                  json={'direction': 'BUY', 'size': 1, 'orderType': 'MARKET',
                                                        'epic': 'IX.D.SUNNAS.IFS.IP', 'currencyCode': 'GBP',
                                                        'expiry': '-', 'forceOpen': True, 'guaranteedStop': False,
                                                        'limitDistance': None, 'stopDistance': None})
        mock_get_deal_details.assert_called_with(mock_open_response['dealReference'])
        mock_close_make_request.assert_called_with(1, 'POST', '/positions/otc', headers={'_method': 'DELETE'},
                                                   json={'dealId': 'DIAAAAND4HSCUAX', 'epic': None,
                                                         'expiry': None, 'direction': 'SELL', 'size': 1,
                                                         'level': None, 'orderType': 'MARKET',
                                                         'timeInForce': None, 'quoteId': None})
        mock_get_close_deal_details.assert_called_with(mock_open_response['dealReference'])


if __name__ == '__main__':
    unittest.main()
