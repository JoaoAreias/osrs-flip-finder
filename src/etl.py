import config
import api_requests
import pandas as pd
import numpy as np

from functools import reduce

def make_pipeline(*funcs):
    """
    Compose multiple etl steps into a full pipeline
    """
    return reduce(lambda f, g: lambda x: g(f(x)), funcs, lambda x: x)


def filter_inactive(data: pd.DataFrame) -> pd.DataFrame:
    now = pd.Timestamp.now()
    threshold = now - pd.Timedelta(hours=config.inactive_threshold)
    return data[
        (data["highTime"] > threshold) & 
        (data["lowTime"] > threshold)
    ]


def filter_unprofitable(data: pd.DataFrame) -> pd.DataFrame:
    due_to_tax = np.clip(
        data["high"] * config.tax_rate * (data["high"] > 100),
        0,
        config.tax_threshold
    )
    
    data["margin"] = data["high"] - due_to_tax - data["low"]
    return data[data["margin"] > 0]


def add_item_names(data: pd.DataFrame) -> pd.DataFrame:
    return data.merge(
    config.ITEM_MAPPING[["id", "name", "members"]],
        left_index=True,
        right_on="id",
    )


def add_item_volume(data: pd.DataFrame) -> pd.DataFrame:
    return data.merge(
        config.VOLUME,
        on='id'
    )


def imput_ge_prices(data: pd.DataFrame) -> pd.DataFrame:
    ge_prices = api_requests.get_ge_price(data["name"].tolist(), config.ge_prices)
    return data.merge(ge_prices, on="name")


def add_margin_pct(data: pd.DataFrame) -> pd.DataFrame:
    data["margin_pct"] = data["margin"] / data["low"]
    return data


def sort_by_margin(data: pd.DataFrame) -> pd.DataFrame:
    return data.sort_values("margin_pct", ascending=False)


pipeline = make_pipeline(
    api_requests.get_data,
    filter_inactive,
    filter_unprofitable,
    add_item_names,
    imput_ge_prices,
    add_item_volume,
    add_margin_pct,
    sort_by_margin
)