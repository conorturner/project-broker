"""
Contains classes and methods for storing position data.
"""


class PositionStore:
    """Class object for position storage."""

    # TODO: store position and keep live returns updated via websocket
    def __init__(self):
        """TBC"""
        raise NotImplementedError()

    def get_positions(self):
        """Return a list of positions for the current account."""
        raise NotImplementedError()

    def update_current_price(self, epic: str, current_price: float):
        """Update the current value of a position based on new price data."""
        raise NotImplementedError()
