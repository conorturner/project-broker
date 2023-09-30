import asyncio
import time
from typing import Dict, List
from pathlib import Path


class PriceStore:
    accumulators: Dict[str, List]
    cache_folder: str
    frequency: float
    running = True

    def __init__(self, cache_folder, frequency=60):
        self.frequency = frequency
        self.cache_folder = cache_folder
        self.accumulators = {}

    async def start(self):
        while self.running:
            await asyncio.sleep(self.frequency)
            for k, v in self.accumulators.items():
                # TODO: write accumulators to disk as parquet.
                # TODO: add lock to prevent sending while writing.
                self.accumulators[k] = []

    def stop(self):
        self.running = False

    def store_price(self, epic, price):
        if epic not in self.accumulators:
            self.accumulators[epic] = []

        self.accumulators[epic].append(price)

    def get_price_file(self, epic):
        # TODO: add lock to prevent sending the file while it is being written to.
        return str(Path(self.cache_folder) / f'{epic}.parquet')
