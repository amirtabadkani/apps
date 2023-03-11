#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from ladybug.epw import EPW
import pathlib

from ladybug.datacollection import HourlyContinuousCollection
from ladybug_comfort.chart.polygonpmv import PolygonPMV
from ladybug.epw import EPW, EPWFields
from ladybug.color import Colorset, Color
from ladybug.legend import LegendParameters
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.sunpath import Sunpath
from ladybug import analysisperiod
from ladybug.analysisperiod import AnalysisPeriod
from ladybug.windrose import WindRose
from ladybug.psychchart import PsychrometricChart

from typing import List, Tuple
from plotly.graph_objects import Figure

st.set_page_config(page_title='Climatic Analysis', layout='wide')

st.write("""
# Temperature Analysis
         
***
""")

colorsets = {
    'original': Colorset.original(),
    'nuanced': Colorset.nuanced(),
    'annual_comfort': Colorset.annual_comfort(),
    'benefit': Colorset.benefit(),
    'benefit_harm': Colorset.benefit_harm(),
    'black_to_white': Colorset.black_to_white(),
    'blue_green_red': Colorset.blue_green_red(),
    'cloud_cover': Colorset.cloud_cover(),
    'cold_sensation': Colorset.cold_sensation(),
    'ecotect': Colorset.ecotect(),
    'energy_balance': Colorset.energy_balance(),
    'energy_balance_storage': Colorset.energy_balance_storage(),
    'glare_study': Colorset.glare_study(),
    'harm': Colorset.harm(),
    'heat_sensation': Colorset.heat_sensation(),
    'multi_colored': Colorset.multi_colored(),
    'multicolored_2': Colorset.multicolored_2(),
    'multicolored_3': Colorset.multicolored_3(),
    'openstudio_palette': Colorset.openstudio_palette(),
    'peak_load_balance': Colorset.peak_load_balance(),
    'shade_benefit': Colorset.shade_benefit(),
    'shade_benefit_harm': Colorset.shade_benefit_harm(),
    'shade_harm': Colorset.shade_harm(),
    'shadow_study': Colorset.shadow_study(),
    'therm': Colorset.therm(),
    'thermal_comfort': Colorset.thermal_comfort(),
    'view_study': Colorset.view_study()
}

def get_colors(switch: bool, global_colorset: str) -> List[Color]:
    """Get switched colorset if requested.
    Args:
        switch: Boolean to switch colorset.
        global_colorset: Global colorset to use.
    Returns:
        List of colors.
    """

    if switch:
        colors = list(colorsets[global_colorset])
        colors.reverse()
    else:
        colors = colorsets[global_colorset]
    return colors


def get_fields() -> dict:
    # A dictionary of EPW variable name to its corresponding field number
    return {EPWFields._fields[i]['name'].name: i for i in range(6, 34)}


def get_hourly_data_figure(
        data: HourlyContinuousCollection, global_colorset: str,st_month: int, st_day: int, st_hour: int, end_month: int,
        end_day: int, end_hour: int) -> Figure:
    """Create heatmap from hourly data.
    Args:
        data: HourlyContinuousCollection object.
        global_colorset: A string representing the name of a Colorset.
        conditional_statement: A string representing a conditional statement.
        min: A string representing the lower bound of the data range.
        max: A string representing the upper bound of the data range.
        st_month: start month.
        st_day: start day.
        st_hour: start hour.
        end_month: end month.
        end_day: end day.
        end_hour: end hour.
    Returns:
        A plotly figure.
    """
    lb_lp = LegendParameters(colors=colorsets[global_colorset])
    
    lb_ap = AnalysisPeriod(st_month, st_day, st_hour, end_month, end_day, end_hour)
    data = data.filter_by_analysis_period(lb_ap)
    
    hourly_plot = HourlyPlot(data, legend_parameters=lb_lp)

    return hourly_plot.plot(title=str(data.header.data_type), show_title=True)


with st.sidebar:
    # A dictionary of EPW variable name to its corresponding field number
    fields = get_fields()
    # epw file #####################################################################
    with st.expander('Upload EPW file'):
        epw_data = st.file_uploader('', type='epw')
        if epw_data:
            epw_file = pathlib.Path(f'./data/{epw_data.name}')
            epw_file.parent.mkdir(parents=True, exist_ok=True)
            epw_file.write_bytes(epw_data.read())
        else:
            epw_file = './assets/sample.epw'

        global_epw = EPW(epw_file)
    # Global Colorset ##############################################################
    with st.expander('Global colorset'):
        global_colorset = st.selectbox('', list(colorsets.keys()))

    st.markdown('---')


    with st.expander('Hourly data'):
                hourly_selected = st.selectbox(
                    'Select an environmental variable', options=fields.keys(), key='hourly_data')
                hourly_data = global_epw._get_data_by_field(fields[hourly_selected])
               
                hourly_data_st_month = st.number_input(
                    'Start month', min_value=1, max_value=12, value=1, key='hourly_data_st_month')
                hourly_data_end_month = st.number_input(
                    'End month', min_value=1, max_value=12, value=12, key='hourly_data_end_month')
    
                hourly_data_st_day = st.number_input(
                    'Start day', min_value=1, max_value=31, value=1, key='hourly_data_st_day')
                hourly_data_end_day = st.number_input(
                    'End day', min_value=1, max_value=31, value=31, key='hourly_data_end_day')
    
                hourly_data_st_hour = st.number_input(
                    'Start hour', min_value=0, max_value=23, value=0, key='hourly_data_st_hour')
                hourly_data_end_hour = st.number_input(
                    'End hour', min_value=0, max_value=23, value=23, key='hourly_data_end_hour')
            
global_epw = EPW(epw_file)

dbt = global_epw.dry_bulb_temperature

Figure = get_hourly_data_figure(dbt,global_colorset, hourly_data_st_month, hourly_data_st_day,
                hourly_data_st_hour, hourly_data_end_month, hourly_data_end_day,
                hourly_data_end_hour)

# Apply Conditions
# temp_min = st.sidebar.slider('Minimum Temperature', -20,22, step=1)
# temp_max = st.sidebar.slider('Maximum Temperature', 22,45, step=1)

# dbt_work_hours = dbt.filter_by_analysis_period(AnalysisPeriod(hourly_data_st_month,hourly_data_st_day,hourly_data_st_hour,hourly_data_end_month,hourly_data_end_day,hourly_data_end_hour)).filter_by_conditional_statement('a>={} and a<={}'.format(temp_min,temp_max))

# figure = dbt_work_hours.heatmap()

st.header(f'{global_epw.location.city}, {global_epw.location.country}')

st.plotly_chart(Figure, use_container_width=True)

# st.markdown('---')
