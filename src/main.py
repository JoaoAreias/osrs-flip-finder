import config
import etl
import api_requests
import streamlit as st
import pandas as pd

from typing import Dict
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


def apply_ui_filters(df: pd.DataFrame, filters: Dict[str, st.slider]) -> pd.DataFrame:
    for column, filter in filters.items():
        df = df[
            (df[column] >= filter[0]) & 
            (df[column] <= filter[1])
        ]
    return df


def format_data(data: pd.DataFrame) -> pd.DataFrame:
    data =  data[["name", "high", "low", "margin_pct", "volume"]]

    grid_options = GridOptionsBuilder.from_dataframe(data)
    grid_options.configure_columns(
        ["high", "low", "volume"], 
        editable=False,
        type=["numericColumn", "numericColumn", "numericColumn"],
        valueFormatter="x.toLocaleString('en-US')",
    )
    grid_options.configure_column("margin_pct", editable=False, type="numericColumn", valueFormatter="x.toLocaleString('en-US', {style: 'percent'})")
    
    data = AgGrid(data, gridOptions=grid_options.build())
    return data

content = load_content()
data = load_data()

st.markdown(content['intro'])

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

filters = {
    'volume': volume,
    'low': price,
    'high': price,
}


data = load_data()
filtered_data = apply_ui_filters(data, filters)
ag_grid = format_data(filtered_data)
