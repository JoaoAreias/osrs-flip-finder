"""
Handles all requests to the API
"""
import requests
import config
import pandas as pd


def make_request(url: str, json: bool = True) -> dict:
    response = requests.get(
        url,
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "Flip finder",
        }
    )
    return response.json() if json else response.text


def refresh_mapping():
    data = make_request(config.api.mapping)
    mapping = pd.DataFrame(data)
    mapping.to_csv(config.MAPPING_PATH, index=False)
    config.ITEM_MAPPING = mapping


def refresh_volume():
    data = make_request(config.api.volumes)
    volume = pd.DataFrame(data['data'].items(), columns=['id', 'volume'])
    volume.to_csv(config.VOLUME_PATH, index=False)
    config.VOLUME = volume


def get_data(url: str) -> pd.DataFrame:
    data = make_request(url)
    data = pd.DataFrame(data["data"]).transpose()

    data["highTime"] = pd.to_datetime(data["highTime"], unit="s")
    data["lowTime"] = pd.to_datetime(data["lowTime"], unit="s")
    data.index = pd.to_numeric(data.index)

    
    return data