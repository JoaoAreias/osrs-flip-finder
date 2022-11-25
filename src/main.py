import config
import etl
import streamlit as st
import pandas as pd

from time import sleep

st.title("OSRS Flip Finder")

table = st.empty()
last_update = st.empty()



while True:
    data = etl.pipeline(config.api.latest)
    table.dataframe(data.reset_index(drop=True), use_container_width=True)
    last_update.text(f"Last update: {pd.Timestamp.now()}")
    sleep(config.refresh_rate)