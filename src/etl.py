import config
import logging
import api_requests
import pandas as pd
import numpy as np

from functools import reduce

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def try_or_log(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {e}")
            logger.error(f"Args: {args}")
            logger.error(f"Kwargs: {kwargs}")
            raise e
    return wrapper


def make_pipeline(*funcs):
    """
    Compose multiple etl steps into a full pipeline
    """
    return reduce(lambda f, g: lambda x: g(f(x)), funcs, lambda x: x)

@try_or_log
def filter_inactive(data: pd.DataFrame) -> pd.DataFrame:
    now = pd.Timestamp.now()
    threshold = now - pd.Timedelta(hours=config.inactive_threshold)
    return data[
        (data["highTime"] > threshold) & 
        (data["lowTime"] > threshold)
    ]

@try_or_log
def filter_unprofitable(data: pd.DataFrame) -> pd.DataFrame:
    due_to_tax = np.clip(
        data["high"] * config.tax_rate * (data["high"] > 100),
        0,
        config.tax_threshold
    )
    
    data["margin"] = data["high"] - due_to_tax - data["low"]
    return data[data["margin"] > 0]

@try_or_log
def add_item_names(data: pd.DataFrame) -> pd.DataFrame:
    return data.merge(
    config.ITEM_MAPPING[["id", "name", "members", "highalch"]],
        left_index=True,
        right_on="id",
    )

@try_or_log
def add_item_volume(data: pd.DataFrame) -> pd.DataFrame:
    if config.VOLUME["id"].dtypes == "object":
        config.VOLUME["id"] = pd.to_numeric(config.VOLUME["id"])

    return data.merge(
        config.VOLUME,
        on='id'
    )

@try_or_log
def imput_ge_prices(data: pd.DataFrame) -> pd.DataFrame:
    ge_prices = api_requests.get_ge_price(data["name"].tolist(), config.ge_prices)
    return data.merge(ge_prices, on="name")

@try_or_log
def add_margin_pct(data: pd.DataFrame) -> pd.DataFrame:
    data["margin_pct"] = data["margin"] / data["low"]
    return data

@try_or_log
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