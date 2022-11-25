from pydantic import BaseModel
from typing import Dict


class APIConfigModel(BaseModel):
    url: str
    endpoints: Dict[str, str]

    def __getattr__(self, name: str):
        return self.url + self.endpoints[name]


class ConfigModel(BaseModel):
    api: APIConfigModel
    refresh_rate: int = 60      # Seconds
    inactive_threshold: int = 4 # Hours
    tax_rate: float = 0.01

    min_volume: int = 1000
    min_price: int = 0
    max_price: int = 20000000
