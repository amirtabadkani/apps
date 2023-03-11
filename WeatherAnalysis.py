#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from ladybug.epw import EPW
import pathlib
from ladybug import analysisperiod


st.set_page_config(page_title='Climatic Analysis', layout='wide')

st.write("""
# Analyze Your Climate
         
***
""")

epw_data = st.file_uploader("Choose an epw file", type='epw')
temp_min = st.sidebar.slider('Minimum Temperature', -20,22, step=1)
temp_max = st.sidebar.slider('Maximum Temperature', 22,45, step=1)

if epw_data:
    epw_file = pathlib.Path(f'./data/{epw_data.name}')
    epw_file.parent.mkdir(parents=True, exist_ok=True)
    epw_file.write_bytes(epw_data.read())
else:
    epw_file = './assets/sample.epw'

global_epw = EPW(epw_file)

dbt = global_epw.dry_bulb_temperature

dbt_work_hours = dbt.filter_by_analysis_period(analysisperiod.AnalysisPeriod(1,1,8,12,31,18)).filter_by_conditional_statement('a>={} and a<={}'.format(temp_min,temp_max))

figure = dbt_work_hours.heat_map()

st.header("Dry Bulb Tempereture")
st.header(f'{global_epw.location.city}, {global_epw.location.country}')

st.plotly_chart(figure, use_container_width=True)

st.markdown('---')
