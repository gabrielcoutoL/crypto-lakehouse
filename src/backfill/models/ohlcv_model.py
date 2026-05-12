from datetime import datetime
from typing import List

from pydantic import BaseModel, field_validator


class CryptoCandle(BaseModel):
    open_time: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    quote_asset_volume: float
    number_of_trades: int
    taker_buy_base_asset_volume: float

    @field_validator("open_time", mode="before")
    @classmethod
    def convert_timestamp(cls, value):

        if isinstance(value, int):
            return datetime.fromtimestamp(value / 1000.0)
        return value


class CryptoAPIResponse(BaseModel):
    data: List[CryptoCandle]
