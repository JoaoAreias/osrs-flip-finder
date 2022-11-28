import config
import etl
import api_requests
import streamlit as st
import pandas as pd

import streamlit.components.v1 as components

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


def inject_ga():
    import pathlib
    import shutil

    from bs4 import BeautifulSoup
    GA_ID = "google_analytics"

    # Note: Please replace the id from G-XXXXXXXXXX to whatever your
    # web application's id is. You will find this in your Google Analytics account
    
    GA_JS = """
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-W6W4DL1THR"></script>
    <script>
    window.dataLayer = window.dataLayer || [];
    function gtag(){dataLayer.push(arguments);}
    gtag('js', new Date());

    gtag('config', 'G-W6W4DL1THR');
    </script>
    """

    # Insert the script in the head tag of the static template inside your virtual
    index_path = pathlib.Path(st.__file__).parent / "static" / "index.html"
    soup = BeautifulSoup(index_path.read_text(), features="html.parser")
    if not soup.find(id=GA_ID):  # if cannot find tag
        bck_index = index_path.with_suffix('.bck')
        if bck_index.exists():
            shutil.copy(bck_index, index_path)  # recover from backup
        else:
            shutil.copy(index_path, bck_index)  # keep a backup
        html = str(soup)
        new_html = html.replace('<head>', '<head>\n' + GA_JS)
        index_path.write_text(new_html)


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

st.markdown(content['intro'])
components.html("""
    <div style="text-align: center; margin: 0px">
<a href="https://www.buymeacoffee.com/joaoareias7" target="_blank"><img src="https://cdn.buymeacoffee.com/buttons/v2/default-yellow.png" alt="Buy Me A Coffee" style="height: 40px !important;width: 145px !important;" ></a>
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

filters = {
    'volume': volume,
    'low': price,
    'high': price,
}


data = load_data()
filtered_data = apply_ui_filters(data, filters)
ag_grid = format_data(filtered_data)
inject_ga()
