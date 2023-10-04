import asyncio
import os.path
import unittest

import pandas as pd
import numpy as np
from fastparquet import write

from app.modules.price_store import PriceStore


class PriceStoreTestCase(unittest.IsolatedAsyncioTestCase):
    async def test_store_price(self):
        self.skipTest('not implemented')
        ps = PriceStore('./data', frequency=1)

        async def test():
            ps.store_price('TSLA', {'open': 10})
            ps.store_price('TSLA', {'open': 12})
            print(ps.accumulators)
            self.assertEqual(len(ps.accumulators['TSLA']), 2)
            await asyncio.sleep(2)
            print(ps.accumulators)
            ps.stop()
            self.assertEqual(len(ps.accumulators['TSLA']), 0)
            self.assertEqual(os.path.exists('data/TSLA.parquet'), True)
            # TODO: assert that the required files exist on disk

        return await asyncio.gather(ps.start(), test())

    async def test_get_price_file(self):
        ps = PriceStore('./data', frequency=1)
        self.assertEqual(ps.get_price_file('TSLA'), 'data/TSLA.parquet')

    def test_parquet(self):
        self.skipTest('not needed yet')
        df = pd.DataFrame({'rand': np.random.random(100)})
        write('sample.parquet', df, append=True)
        print(pd.read_parquet('sample.parquet'))


if __name__ == '__main__':
    unittest.main()
