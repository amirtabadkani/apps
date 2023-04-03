#!/usr/bin/env python
# coding: utf-8

# In[1]:

import numpy as np
import pandas as pd

import streamlit as st
from ladybug.epw import EPW
import pathlib
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from typing import List, Tuple
import plotly.graph_objects as go


from ladybug.datacollection import HourlyContinuousCollection
from ladybug.epw import EPWFields
from ladybug.color import Colorset, Color
from ladybug.legend import LegendParameters
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.analysisperiod import AnalysisPeriod


st.set_page_config(page_title='EPW File Reader', layout='wide')

with st.container.image('https://1731290220-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2FZbSo9tzMwlZsIB61RpcZ%2Fuploads%2FbKSSyj7avm80wP7Ymqew%2FEPW%20Map.png?alt=media&token=517fc466-a693-4007-98a8-c35c6a97f8f6')
    
    
with st.sidebar:
    st.header('__EPW File Reader__')
    st.markdown('_Developed by **Amir Tabadkani**, \nPh.D. Computational Design Lead, Sustainability_')
    st.write('Source codes: Ladybug Tools Core SDK Documentation')
#st.sidebar.image('https://www.ceros.com/wp-content/uploads/2019/04/Stantec_Logo.png',use_column_width='auto',output_format='PNG')

# Loading colorsets used in Legend Parameters
#---------------------------------------------------------------------------------
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

# A function to derive the color code when selected in Streamlit
#------------------------------------------------------------------------------

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

# Define a function to extract the epw variable from the class
# Example:
# print(dir(EPWFields))
# EPWFields._fields[7]['name'].name

def epw_hash_func(epw: EPW) -> str:
    """Function to help streamlit hash an EPW object."""
    return epw.location.city

def get_fields() -> dict:
    # A dictionary of EPW variable name to its corresponding field number
    return {EPWFields._fields[i]['name'].name: i for i in range(6, 34)}

# Uploading EPW file
#------------------------------------------------------------------------------

with st.sidebar:
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
    
    st.markdown('---')
    
# Global Colorset - Choose the heatmap color
#------------------------------------------------------------------------------

with st.sidebar:
    with st.expander('Global colorset'):
        global_colorset = st.selectbox('', list(colorsets.keys()))
        
# Hourly Plots
#------------------------------------------------------------------------------
st.markdown('---')
st.write("""
# Hourly Weather Data Analysis
         
***
""")

with st.sidebar:
    # A dictionary of EPW variable name to its corresponding field number
    
    fields = get_fields()
    with st.expander('Hourly data'):
        hourly_selected = st.selectbox('Which variable to plot?',options=fields.keys())
        hourly_data = global_epw.import_data_by_field(fields[hourly_selected])
        
        data_plot_radio = st.radio('How to plot the data?', ['Hourly Plot','Mean Daily Plot', 'Line Plot'], index =0, key='data_plot')
        st.markdown('*:red[Warning: Analysis Period below is ONLY applicable to the Hourly Plot!]*')
        if (data_plot_radio == 'Mean Daily Plot') or (data_plot_radio == 'Hourly Plot') or (data_plot_radio == 'Line Plot'):
            data_final = hourly_data        
        else: 
            data_final = None #Never Happens!
            
                
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
                   
    
def get_hourly_data_figure(data_type:str,
        hourly_data: HourlyContinuousCollection, global_colorset: str,st_month: int, st_day: int, st_hour: int, end_month: int,
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
    hourly_data = hourly_data.filter_by_analysis_period(lb_ap)
    
    colors = colorsets[global_colorset] 
    
    if data_type == 'Hourly Plot':
        
        hourly_plot = HourlyPlot(hourly_data, legend_parameters=lb_lp)
    
        return hourly_plot.plot(title=str(hourly_data.header.data_type), show_title=True)
    
    elif data_type == 'Mean Daily Plot':
        return hourly_data.diurnal_average_chart(
            title=hourly_data.header.data_type.name, show_title=True,color=colors[-1])
    
    elif data_type == 'Line Plot':
        return hourly_data.line_chart(title=hourly_data.header.data_type.name,show_title=True,color=colors[-1])
    
Hourly_figure = get_hourly_data_figure(data_plot_radio,data_final,global_colorset, hourly_data_st_month, hourly_data_st_day,
                hourly_data_st_hour, hourly_data_end_month, hourly_data_end_day,
                hourly_data_end_hour)

st.header(f'{global_epw.location.city}, {global_epw.location.country}')
st.plotly_chart(Hourly_figure, use_container_width=True)


# CONDITIONAL HOURLY PLOTS
#------------------------------------------------------------------------------

with st.sidebar: 
    with st.expander('Conditional Statement'):
        fields = get_fields()
        st.markdown(':red[**Min/Max Thresholds**]')
        
        min_value = global_epw.import_data_by_field(fields[hourly_selected]).bounds[0]
        max_value = global_epw.import_data_by_field(fields[hourly_selected]).bounds[1]
      
        temp_min = st.slider('Minimum {}'.format(hourly_selected), min_value, max_value, value = ((max_value+min_value)/4),  step=None)
        temp_max = st.slider('Maximum {}'.format(hourly_selected), min_value,max_value,value =((max_value+min_value)/2),  step=None)
        
def get_hourly_data_figure_conditional(hourly_data: HourlyContinuousCollection, global_colorset: str,st_month: int, st_day: int, st_hour: int, end_month: int,
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
    hourly_data = hourly_data.filter_by_analysis_period(lb_ap)
    
           
    hourly_plot = HourlyPlot(hourly_data, legend_parameters=lb_lp)

    return hourly_plot.plot(title=str(hourly_data.header.data_type), show_title=True)

st.subheader('_Applied Thresholds_')
st.markdown('Please choose the thresholds from the min/max sliders on the left to plot the filtered data below:')
  
data_work_hours = hourly_data.filter_by_analysis_period(AnalysisPeriod(hourly_data_st_month,hourly_data_st_day,hourly_data_st_hour,hourly_data_end_month,hourly_data_end_day,hourly_data_end_hour)).filter_by_conditional_statement('a>={} and a<={}'.format(temp_min,temp_max))

Hourly_conditional_figure = get_hourly_data_figure_conditional(data_work_hours,global_colorset, hourly_data_st_month, hourly_data_st_day,
                hourly_data_st_hour, hourly_data_end_month, hourly_data_end_day,
                hourly_data_end_hour)
st.plotly_chart(Hourly_conditional_figure, use_container_width=True)

num_hours = len(data_work_hours)
st.metric(':blue[**Number of hours meeting the {} thresholds:**]'.format(hourly_selected), value = num_hours)

   
st.markdown('---')

#Pyschometric Chart
#------------------------------------------------------------------------------

st.write("""
# Psychrometric Chart
         
***
""")

import ladybug.psychrometrics
from ladybug.psychchart import PsychrometricChart
from ladybug_charts.utils import Strategy
from ladybug_comfort.chart.polygonpmv import PolygonPMV


with st.sidebar:
    
    with st.expander('Psychrometric chart'):
    
        fields = get_fields()
        
        psy_radio = st.radio('',['Load Hourly Data', 'Extracting Psychrometrics'],index = 0, key='psy_radio')
        
        if psy_radio == 'Load Hourly Data':
            psy_selected = st.selectbox('Select an environmental variable', options=fields.keys())
            psy_data = global_epw.import_data_by_field(fields[psy_selected])
            psy_draw_polygons = st.checkbox('Draw comfort polygons')
            psy_strategy_options = ['Comfort', 'Evaporative Cooling',
                                    'Mass + Night Ventilation', 'Occupant use of fans',
                                    'Capture internal heat', 'Passive solar heating', 'All']
            psy_selected_strategy = st.selectbox(
                'Select a passive strategy', options=psy_strategy_options)
        else:
            psy_selected_strategy = None
            psy_draw_polygons = None
            psy_data = None
            psy_db = st.number_input('Insert DBT value',min_value =-20, max_value = 50, value = 24)
            psy_rh = st.number_input('Insert RH value',min_value =0, max_value = 100, value = 45)
        
        
def get_psy_chart_figure(epw: EPW, global_colorset: str, selected_strategy: str,
                         load_data: str, draw_polygons: bool,
                         data: HourlyContinuousCollection) -> Figure:
    """Create psychrometric chart figure.
    Args:
        epw: An EPW object.
        global_colorset: A string representing the name of a Colorset.
        selected_strategy: A string representing the name of a psychrometric strategy.
        load_data: A boolean to indicate whether to load the data.
        draw_polygons: A boolean to indicate whether to draw the polygons.
        data: Hourly data to load on psychrometric chart.
    Returns:
        A plotly figure.
    """

    lb_lp = LegendParameters(colors=colorsets[global_colorset])
    lb_psy = PsychrometricChart(epw.dry_bulb_temperature,
                                epw.relative_humidity, legend_parameters=lb_lp)

    if selected_strategy == 'All':
        strategies = [Strategy.comfort, Strategy.evaporative_cooling,
                      Strategy.mas_night_ventilation, Strategy.occupant_use_of_fans,
                      Strategy.capture_internal_heat, Strategy.passive_solar_heating]
    elif selected_strategy == 'Comfort':
        strategies = [Strategy.comfort]
    elif selected_strategy == 'Evaporative Cooling':
        strategies = [Strategy.evaporative_cooling]
    elif selected_strategy == 'Mass + Night Ventilation':
        strategies = [Strategy.mas_night_ventilation]
    elif selected_strategy == 'Occupant use of fans':
        strategies = [Strategy.occupant_use_of_fans]
    elif selected_strategy == 'Capture internal heat':
        strategies = [Strategy.capture_internal_heat]
    elif selected_strategy == 'Passive solar heating':
        strategies = [Strategy.passive_solar_heating]

    pmv = PolygonPMV(lb_psy)

    if load_data == 'Load Hourly Data':
        if draw_polygons:
            figure = lb_psy.plot(data=data, polygon_pmv=pmv,
                                 strategies=strategies,title='PSYCHROMETRIC CHART', show_title=True)
        else:
            figure = lb_psy.plot(data=data, show_title=True)
        return figure
    
    else:
      
        lb_psy_ext = PsychrometricChart(psy_db,psy_rh)
        figure = lb_psy_ext.plot(title='PSYCHROMETRIC CHART', show_title=True)
        
        dew_pt = round(ladybug.psychrometrics.dew_point_from_db_rh(psy_db, psy_rh),2)
        hr_pt = round(ladybug.psychrometrics.humid_ratio_from_db_rh(psy_db, psy_rh),2)
        wb_pt = round(ladybug.psychrometrics.wet_bulb_from_db_rh(psy_db, psy_rh),2)
        ent_pt = round(ladybug.psychrometrics.enthalpy_from_db_hr(psy_db, hr_pt),2)
        psy_db_kelvin = psy_db + 274.15
        sat_p = round(ladybug.psychrometrics.saturated_vapor_pressure(psy_db_kelvin),2)
        
        col1,col2,col3,col4,col5,col6,col7 = st.columns(7)
        
        with col1:
            
            st.metric('Dry Bulb Temperature (°C)', value = psy_db)
            
        with col2:
            
            st.metric('Relative Humidity (%)', value = psy_rh)
            
        with col3:
            
            st.metric('Dew Point Temperature (°C)', value = dew_pt)
            
        with col4:
            
            st.metric('Humidty Ratio (kg_H₂O kg_Air⁻¹)', value = hr_pt)
            
        with col5:
            
            st.metric('Wet Bulb Temperature (°C)', value = wb_pt)
            
        with col6:
            
            st.metric('Enthalpy (J kg⁻¹)', value = ent_pt)
            
        with col7:
            
            st.metric('Saturated Vapour Pressure (Pa)', value = sat_p)
    
        return figure

def get_figure_config(title: str) -> dict:
    """Set figure config so that a figure can be downloaded as SVG."""

    return {
        'toImageButtonOptions': {
            'format': 'svg',  # one of png, svg, jpeg, webp
            'filename': title,
            'height': 700,
            'width': 700,
            'scale': 1  # Multiply title/legend/axis/canvas sizes by this factor
        }
    }
  
with st.container():
    
    st.markdown(
        'A psychrometric chart can be used in two different ways. The first is done by plotting multiple data points, that represent the air conditions at a specific time, on the chart. Then, overlaying an area that identifies the “comfort zone.”  The comfort zone is defined as the range within occupants are satisfied with the surrounding thermal conditions. After plotting the air conditions and overlaying the comfort zone, it becomes possible to see how passive design strategies can extend the comfort zone.')
    
    psy_chart_figure = get_psy_chart_figure(
        global_epw, global_colorset, psy_selected_strategy, psy_radio,
        psy_draw_polygons, psy_data)
    
    st.plotly_chart(psy_chart_figure, use_container_width=True, config=get_figure_config(f'Psychrometric_chart_{global_epw.location.city}'))

             
    # st.image('https://github.com/psychrometrics/psychrolib/raw/master/assets/psychrolib_relationships.svg',use_column_width='True',output_format='PNG')

st.markdown('---')
st.write("""
# Wind Rose
""")
st.markdown('---')

# WINDROSE
#------------------------------------------------------------------------------
from ladybug.windrose import WindRose

with st.sidebar:
    
    with st.expander('Windrose'):
    
        windrose_st_month = st.number_input(
            'Start month', min_value=1, max_value=12, value=1, key='windrose_st_month')
        windrose_end_month = st.number_input(
            'End month', min_value=1, max_value=12, value=12, key='windrose_end_month')

        windrose_st_day = st.number_input(
            'Start day', min_value=1, max_value=31, value=1, key='windrose_st_day')
        windrose_end_day = st.number_input(
            'End day', min_value=1, max_value=31, value=31, key='windrose_end_day')

        windrose_st_hour = st.number_input(
            'Start hour', min_value=0, max_value=23, value=0, key='windrose_st_hour')
        windrose_end_hour = st.number_input(
            'End hour', min_value=0, max_value=23, value=23, key='windrose_end_hour')
    
   
          
def get_windrose_figure(st_month: int, st_day: int, st_hour: int, end_month: int,
                        end_day: int, end_hour: int, epw, global_colorset) -> Figure:
    
    """Create windrose figure.
    Args:
        st_month: A number representing the start month.
        st_day: A number representing the start day.
        st_hour: A number representing the start hour.
        end_month: A number representing the end month.
        end_day: A number representing the end day.
        end_hour: A number representing the end hour.
        epw: An EPW object.
        global_colorset: A string representing the name of a Colorset.
    Returns:
        A plotly figure.
    """
            
    lb_ap = AnalysisPeriod(st_month, st_day, st_hour, end_month, end_day, end_hour)
    wind_dir = epw.wind_direction.filter_by_analysis_period(lb_ap)
    wind_spd = epw.wind_speed.filter_by_analysis_period(lb_ap)
    
    lb_lp = LegendParameters(colors=colorsets[global_colorset])
    
    lb_wind_rose = WindRose(wind_dir, wind_spd)
    lb_wind_rose.legend_parameters = lb_lp
    
    return lb_wind_rose.plot(title='Windrose',show_title=True)

def get_windrose_figure_temp(st_month: int, st_day: int, st_hour: int, end_month: int,
                    end_day: int, end_hour: int, epw, global_colorset) -> Figure:
    
    """Create windrose figure.
    Args:
        st_month: A number representing the start month.
        st_day: A number representing the start day.
        st_hour: A number representing the start hour.
        end_month: A number representing the end month.
        end_day: A number representing the end day.
        end_hour: A number representing the end hour.
        epw: An EPW object.
        global_colorset: A string representing the name of a Colorset.
    Returns:
        A plotly figure.
    """
    
    lb_ap = AnalysisPeriod(st_month, st_day, st_hour, end_month, end_day, end_hour)        
    
    fields = get_fields()
        
    windrose_data = global_epw.import_data_by_field(fields['Dry Bulb Temperature'])
    
    wind_dir = epw.wind_direction.filter_by_analysis_period(lb_ap)
    windrose_data_ = windrose_data.filter_by_analysis_period(lb_ap)
    
    lb_lp = LegendParameters(colors=colorsets[global_colorset])
    
    lb_windrose_temp = WindRose(wind_dir,windrose_data_)
    lb_windrose_temp.legend_parameters = lb_lp
    
    return lb_windrose_temp.plot(title='Wind Direction vs. Dry Bulb Temperature', show_title=True)
 

with st.container():
    
    st.markdown('Generate a wind rose to summarise the occurrence of winds at a location, showing their strength, direction and frequency, for the selected period and environmental parameter!')
    
    col1,col2 = st.columns(2)
    with col1:
        
        windrose_figure = get_windrose_figure(windrose_st_month, windrose_st_day, windrose_st_hour, windrose_end_month,
                                              windrose_end_day, windrose_end_hour, global_epw, global_colorset)
    
        st.plotly_chart(windrose_figure, use_container_width=True,
                        config=get_figure_config(f'Windrose_{global_epw.location.city}'))
    with col2:
        windrose_figure_temp = get_windrose_figure_temp(windrose_st_month, windrose_st_day, windrose_st_hour, windrose_end_month,
                                              windrose_end_day, windrose_end_hour, global_epw, global_colorset)
    
        st.plotly_chart(windrose_figure_temp, use_container_width=True,
                        config=get_figure_config(f'Windrose_{global_epw.location.city}'))
    st.markdown('---')

#SUNPATH
#-----------------------------------------------------------------------------
from ladybug.sunpath import Sunpath

st.write("""
# Sunpath Diagram
         
***
""")

def get_sunpath_figure(sunpath_type: str, global_colorset: str, epw: EPW = None,
                       switch: bool = False,
                       data: HourlyContinuousCollection = None, ) -> Figure:
    """Create sunpath figure.
    Args:
        sunpath_type: A string representing the type of sunpath to be plotted.
        global_colorset: A string representing the name of a Colorset.
        epw: An EPW object.
        switch: A boolean to indicate whether to reverse the colorset.
        data: Hourly data to load on sunpath.
    Returns:
        A plotly figure.
    """
    if sunpath_type == 'from epw location':
        lb_sunpath = Sunpath.from_location(epw.location)
        colors = get_colors(switch, global_colorset)
        return lb_sunpath.plot(title='Sunpath Diagram',colorset=colors,show_title=True)
    else:
        lb_sunpath = Sunpath.from_location(epw.location)
        colors = colorsets[global_colorset]
        return lb_sunpath.plot(title=str(data.header.data_type),colorset=colors, data=data, show_title=True)


with st.sidebar:
    
    with st.expander('Sunpath'):
    
        sunpath_radio = st.radio(
            '', ['from epw location', 'with epw data'],
            index=0, key='sunpath_'
        )
    
        if sunpath_radio == 'from epw location':
            sunpath_switch = st.checkbox('Switch colors', key='sunpath_switch',
                                         help='Reverse the colorset')
            sunpath_data = None
    
        else:
            sunpath_selected = st.selectbox(
                'Select an environmental variable', options=fields.keys(), key='sunpath')
            sunpath_data = global_epw._get_data_by_field(fields[sunpath_selected])
            sunpath_switch = None

                
with st.container():

    st.markdown('Generate a sunpath using EPW location. Additionally, you can'
                ' also load one of the environmental variables from the EPW file'
                ' on the sunpath.'
                )
    
    sunpath_figure = get_sunpath_figure(sunpath_radio, global_colorset, global_epw, sunpath_switch, sunpath_data)
    
    st.plotly_chart(sunpath_figure, use_container_width=True,
                    config=get_figure_config(
                        f'Sunpath_{global_epw.location.city}'))

#Degree Days
#------------------------------------------------------------------------------


from ladybug.datatype.temperaturetime import HeatingDegreeTime, CoolingDegreeTime
from ladybug_comfort.degreetime import heating_degree_time, cooling_degree_time

with st.sidebar:
    with st.expander('Degree days'):
    
          
        degree_days_heat_base = st.number_input('Base heating temperature',
                                                value=18)

    
        degree_days_cool_base = st.number_input('Base cooling temperature',
                                                value=23)

def get_degree_days_figure(
    dbt: HourlyContinuousCollection, _heat_base_: int, _cool_base_: int,
    global_colorset: str) -> Tuple[Figure,HourlyContinuousCollection,HourlyContinuousCollection]:
    """Create HDD and CDD figure.
    Args:
        dbt: A HourlyContinuousCollection object.
        _heat_base_: A number representing the heat base temperature.
        _cool_base_: A number representing the cool base temperature.
        stack: A boolean to indicate whether to stack the data.
        switch: A boolean to indicate whether to reverse the colorset.
        global_colorset: A string representing the name of a Colorset.
    Returns:
        A tuple of three items:
        -   A plotly figure.
        -   Heating degree days as a HourlyContinuousCollection.
        -   Cooling degree days as a HourlyContinuousCollection.
    """

    hourly_heat = HourlyContinuousCollection.compute_function_aligned(
        heating_degree_time, [dbt, _heat_base_],
        HeatingDegreeTime(), 'degC-hours')
    hourly_heat.convert_to_unit('degC-days')

    hourly_cool = HourlyContinuousCollection.compute_function_aligned(
        cooling_degree_time, [dbt, _cool_base_],
        CoolingDegreeTime(), 'degC-hours')
    hourly_cool.convert_to_unit('degC-days')

    colors = colorsets[global_colorset]

    lb_lp = LegendParameters(colors=colors)
    monthly_chart = MonthlyChart([hourly_cool.total_monthly(),
                                  hourly_heat.total_monthly()], legend_parameters=lb_lp)

    return monthly_chart.plot(title='Degree Days'), hourly_heat, hourly_cool

with st.container():
    st.markdown('---')
    st.header('Degree Days')
    st.markdown('---')
    st.markdown('**Degree days** is another way of combining time and temperature, but it has different implications for heating and cooling than does design temperature.')
                
    st.markdown('**Heating degree days (HDD)** – This is the number that tells you' 
                'how long a location stays below a special temperature called the base'
                'temperature. I find it easiest to start with degree hours.'
                'For example, the most commonly used base temperature for heating is 18°C.'
                'So if the temperature at your house is 12° F for one hour, you just'
                'accumulated 6 degree hours. If the temperature is 15°C for the next hour'
                ',you’ve got another 3 degree hours and 9 degree hours total.'
                'To find the number of degree days, you divide it by 24,'
                ' so you’ve got one degree day in this example.'
                'You can do that for every hour of the year to find the total and then divide by 24.'
                ' Or you can use the average temperature for each day to get degree days directly.')
    st.markdown('**Cooling degree days (CDD)** – Same principle as for heating degree days but usually'
                'with a different base temperature which is here set as 24°C by default.') 
                

    degree_days_figure, hourly_heat, hourly_cool = get_degree_days_figure(
        global_epw.dry_bulb_temperature, degree_days_heat_base,
        degree_days_cool_base,global_colorset)

    st.plotly_chart(degree_days_figure, use_container_width=True,
                    config=get_figure_config(
                        f'Degree days_{global_epw.location.city}'))
    st.markdown(
        f':blue[**Total Cooling degree days are {round(hourly_cool.total)}**]'
        f' **AND** :red[**total heating degree days {round(hourly_heat.total)}**].')
