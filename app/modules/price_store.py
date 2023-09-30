"""
Module contains functionality for storing and retrieving price data.
"""

import asyncio
from typing import Dict, List
from pathlib import Path


class PriceStore:
    """The PriceStore class contains a buffer to accumulate prices and a cron to write them to disk."""
    accumulators: Dict[str, List]
    cache_folder: str
    frequency: float
    running = True

    def __init__(self, cache_folder: str, frequency: int = 60):
        """Initialise PriceStore instance with empty accumulator dictionary."""
        self.frequency = frequency
        self.cache_folder = cache_folder
        self.accumulators = {}

    async def start(self):
        """Start the disk storage cron job."""
        while self.running:
            await asyncio.sleep(self.frequency)
            for epic, prices in self.accumulators.items():
                # TODO: write accumulators to disk as parquet.
                # TODO: add lock to prevent sending while writing.
                self.accumulators[epic] = []

    def stop(self):
        """Stop the cron job gracefully (useful in testing)."""
        self.running = False

    def store_price(self, epic, price):
        """Add a price to the accumulator."""
        if epic not in self.accumulators:
            self.accumulators[epic] = []

        self.accumulators[epic].append(price)

    def get_price_file(self, epic):
        """Get the path for the price file for a given epic."""
        # TODO: add lock to prevent sending the file while it is being written to.
        return str(Path(self.cache_folder) / f'{epic}.parquet')
