import os
import unittest
from unittest import mock

from app.modules.broker_integrations.ig_api import IgClient

IG_API_KEY = os.environ.get('IG_API_KEY')
IG_ACCOUNT = os.environ.get('IG_ACCOUNT')
IG_USER = os.environ.get('IG_USER')
IG_PASS = os.environ.get('IG_PASS')


class MockResponse:
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
        api = IgClient(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)
        mock_response = {'correct': 'response'}
        with mock.patch('aiohttp.ClientSession.request',
                        return_value=MockResponse(mock_response, 200)) as mock_request:
            with mock.patch('app.modules.broker_integrations.ig_api.IgAPI._IgAPI__headers',
                            return_value={'example': 'header', 'dict': 1}) as mock_headers:
                result = await api._IgAPI__make_request(1, "GET", '/markets', params={'searchTerm': 'oil'})

                mock_request.assert_called_with('GET', 'https://demo-api.ig.com/gateway/deal/markets',
                                                headers={'example': 'header', 'dict': 1}, params={'searchTerm': 'oil'})
                mock_headers.assert_called_with(1)
                self.assertEqual(result, mock_response)

    async def test_market_search(self):
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

        with mock.patch('app.modules.broker_integrations.ig_api.IgAPI._IgAPI__make_request',
                        return_value=mock_response) as mock_make_request:
            api = IgClient(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)
            result = await api.search_market('wall street cash')
            self.assertIn('markets', mock_response)
            self.assertIsInstance(result['markets'], list)
            mock_make_request.assert_called_with(1, 'GET', '/markets', params={'searchTerm': 'wall street cash'})

    async def test_open_close_position(self):
        self.skipTest('No trades at the weekend')
        api = IgClient(IG_API_KEY, IG_ACCOUNT, IG_USER, IG_PASS)

        epic = 'IX.D.DOW.IFD.IP'

        position = await api.open_position('BUY', 1, epic, currency='USD')
        print(position)
        position = await api.close_position(position['dealId'], 1, 'SELL')
        print(position)


if __name__ == '__main__':
    unittest.main()
