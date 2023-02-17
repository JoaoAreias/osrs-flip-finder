import config
import etl
import api_requests
import streamlit as st
import pandas as pd
import warnings

import streamlit.components.v1 as components

from typing import Callable, Dict
from st_aggrid import AgGrid, GridOptionsBuilder
from streamlit_autorefresh import st_autorefresh


st.set_page_config(page_title="OSRS flip finder")
st_autorefresh(config.refresh_rate * 1000)


@st.cache(ttl=config.refresh_rate, allow_output_mutation=True)
def load_data():
    data = etl.pipeline(config.api.latest)
    return data

@st.cache(ttl=24 * 60 * 60)
def refresh_volume():
    api_requests.refresh_volume()


def load_content():
    content = {}
    for path in config.CONTENT_PATH.glob('*.md'):
        content[path.stem] = path.read_text()
    return content


def apply_filters(data: pd.DataFrame, filters: Dict[str, Callable]) -> pd.DataFrame:
    for filter in filters.values():
        data = filter(data)
    return data


def format_data(data: pd.DataFrame) -> pd.DataFrame:
    data =  data[["name", "high", "low", "price", "margin_pct", "volume"]]

    grid_options = GridOptionsBuilder.from_dataframe(data)
    grid_options.configure_columns(
        ["high", "low", "volume", "price"], 
        editable=False,
        type=["numericColumn", "numericColumn", "numericColumn"],
        valueFormatter="x.toLocaleString('en-US')",
    )
    grid_options.configure_column("margin_pct", editable=False, type="numericColumn", valueFormatter="x.toLocaleString('en-US', {style: 'percent'})")
    
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        data = AgGrid(data, gridOptions=grid_options.build())
    
    return data

content = load_content()

st.markdown(content['intro'])
components.html("""
<div style="text-align: center; margin: 0px">
    <a href="https://www.buymeacoffee.com/joaoareias7" target="_blank">
        <img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" >
    </a>
</div>""", height=60)

with st.sidebar:
    st.markdown('## Volume')
    volume = (
        st.number_input('Minimum daily volume', 0, None, 1000),
        st.number_input('Maximum daily volume', 0, None, 1000000000),
    )

    st.markdown('## Price')
    price = (
        st.number_input('Minimum price', 0, None, 1000),
        st.number_input('Maximum price', 0, None, 100000)
    )

    st.markdown('----')
    free_to_play = st.checkbox('Free to play only', False)
    bellow_ge_price = st.checkbox('Bellow GE price', False)



filters = {
    'volume': lambda df: df[(df['volume'] >= volume[0]) & (df['volume'] <= volume[1])],
    'price': lambda df: df[(df['low'] >= price[0]) & (df['low'] <= price[1]) & (df['high'] >= price[0]) & (df['high'] <= price[1])],
    'free_to_play': lambda df: df[df['free_to_play'] == True] if free_to_play else df,
    'bellow_ge_price': lambda df: df[df['high'] < df['price']] if bellow_ge_price else df,
}

data = load_data()
filtered_data = apply_filters(data, filters)
ag_grid = format_data(filtered_data)
