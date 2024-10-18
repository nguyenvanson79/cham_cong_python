import streamlit as st
import pandas as pd
import time
from datetime import datetime


tg = time.time()
date = datetime.fromtimestamp(tg).strftime("%d-%m-%Y")
time_str = datetime.fromtimestamp(tg).strftime("%H:%M:%S")


df=pd.read_csv(f'luu_thoi_gian/luu{date}.csv')




st.dataframe(df.style.highlight_max(axis=0))
