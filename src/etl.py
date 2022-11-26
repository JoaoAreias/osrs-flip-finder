import config
import api_requests
import pandas as pd

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
    data["margin"] = data["high"] * (1 - config.tax_rate) - data["low"]
    return data[data["margin"] > 0]


def add_item_names(data: pd.DataFrame) -> pd.DataFrame:
    return data.merge(
        config.ITEM_MAPPING[["id", "name"]],
        left_index=True,
        right_on="id",
    ).drop(columns="id")

def add_item_volume(data: pd.DataFrame) -> pd.DataFrame:
    return data.merge(
        config.VOLUME,
        left_index=True,
        right_on="id",
    ).drop(columns="id")

def filter_by_price(data: pd.DataFrame) -> pd.DataFrame:
    return data[
        (data["low"] > config.min_price) &
        (data["high"] < config.max_price)
    ]


def add_margin_pct(data: pd.DataFrame) -> pd.DataFrame:
    data["margin_pct"] = data["margin"] / data["low"]
    return data


def sort_by_margin(data: pd.DataFrame) -> pd.DataFrame:
    return data.sort_values("margin_pct", ascending=False)




pipeline = make_pipeline(
    api_requests.get_data,
    filter_inactive,
    filter_unprofitable,
    filter_by_price,
    add_item_names,
    add_item_volume,
    add_margin_pct,
    sort_by_margin
)