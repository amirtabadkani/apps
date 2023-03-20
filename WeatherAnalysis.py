#!/usr/bin/env python
# coding: utf-8

# In[1]:


import streamlit as st
from ladybug.epw import EPW
import pathlib
from plotly.graph_objects import Figure
from plotly.subplots import make_subplots
from typing import List
import plotly.graph_objects as go


from ladybug.datacollection import HourlyContinuousCollection
from ladybug.epw import EPW, EPWFields
from ladybug.color import Colorset, Color
from ladybug.legend import LegendParameters
from ladybug.hourlyplot import HourlyPlot
from ladybug.monthlychart import MonthlyChart
from ladybug.analysisperiod import AnalysisPeriod




st.set_page_config(page_title='EPW Reader', layout='wide')

st.sidebar.image('https://media.glassdoor.com/sqlm/21416/stantec-squarelogo-1559931308692.png',use_column_width=True,output_format='PNG')

# Loading colorsets used in Legend Parameters
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

with st.sidebar:
    st.header('__EPW File Reader__')
    st.markdown('_Designed by **Amir Tabadkani**_')
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


# Hourly Plots
#------------------------------------------------------------------------------
with st.sidebar:
    # A dictionary of EPW variable name to its corresponding field number
    fields = get_fields()
    with st.expander('Hourly data'):
        hourly_selected = st.selectbox(
            'Select an environmental variable', options=fields.keys(), key='hourly_data')
        hourly_data = global_epw.import_data_by_field(fields[hourly_selected])
       
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
           
st.markdown('---')

st.write("""
# Hourly Weather Data Analysis
         
***
""")

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


# Global Colorset - Choose the heatmap color
 
with st.sidebar:
    with st.expander('Global colorset'):
        global_colorset = st.selectbox('', list(colorsets.keys()))
    
    fields = get_fields()
    
    with st.container():
        hourly_selected = st.selectbox('Which Variable to PLOT?',options=fields.keys())
        data = global_epw.import_data_by_field(fields[hourly_selected])
        
        min_value = global_epw.import_data_by_field(fields[hourly_selected]).bounds[0]
        max_value = global_epw.import_data_by_field(fields[hourly_selected]).bounds[1]
      
        
        st.markdown(':red[ Thresholds]')
        temp_min = st.sidebar.slider('Minimum {}'.format(hourly_selected), min_value,max_value, step=None)
        temp_max = st.sidebar.slider('Maximum {}'.format(hourly_selected), min_value,max_value, step=None)
    
    st.markdown('---')
        
    
Hourly_Figure = get_hourly_data_figure(data,global_colorset, hourly_data_st_month, hourly_data_st_day,
                hourly_data_st_hour, hourly_data_end_month, hourly_data_end_day,
                hourly_data_end_hour)

st.header(f'{global_epw.location.city}, {global_epw.location.country}')
st.plotly_chart(Hourly_Figure, use_container_width=True)


# Apply Thresholds

st.subheader('_Applied Thresholds_')
  
data_work_hours = data.filter_by_analysis_period(AnalysisPeriod(hourly_data_st_month,hourly_data_st_day,hourly_data_st_hour,hourly_data_end_month,hourly_data_end_day,hourly_data_end_hour)).filter_by_conditional_statement('a>={} and a<={}'.format(temp_min,temp_max))

Hourly_conditional_figure = get_hourly_data_figure(data_work_hours,global_colorset, hourly_data_st_month, hourly_data_st_day,
                hourly_data_st_hour, hourly_data_end_month, hourly_data_end_day,
                hourly_data_end_hour)

st.plotly_chart(Hourly_conditional_figure, use_container_width=True)
    
st.markdown('---')

#Pyschometric Chart
#------------------------------------------------------------------------------

st.write("""
# Psychrometric Chart
         
***
""")

from ladybug.psychchart import PsychrometricChart
from ladybug_charts.utils import Strategy
from ladybug_comfort.chart.polygonpmv import PolygonPMV

def get_psy_chart_figure(epw: EPW, global_colorset: str, selected_strategy: str,
                         load_data: bool, draw_polygons: bool,
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

    if load_data:
        if draw_polygons:
            figure = lb_psy.plot(data=data, polygon_pmv=pmv,
                                 strategies=strategies,
                                 solar_data=epw.direct_normal_radiation,title='PSYCHROMETRIC CHART', show_title=True)
        else:
            figure = lb_psy.plot(data=data, show_title=True)
    else:
        if draw_polygons:
            figure = lb_psy.plot(polygon_pmv=pmv, strategies=strategies,
                                 solar_data=epw.direct_normal_radiation,title='PSYCHROMETRIC CHART', show_title=True)
        else:
            figure = lb_psy.plot(title='PSYCHROMETRIC CHART',show_title=True)

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

with st.sidebar:
    
    with st.expander('Psychrometric chart'):
    
        fields = get_fields()
        
        psy_load_data = st.checkbox('Load data')
        
        if psy_load_data:
            psy_selected = st.selectbox('Select an environmental variable', options=fields.keys())
            psy_data = global_epw.import_data_by_field(fields[psy_selected])
        else:
            psy_data = None
    
        psy_draw_polygons = st.checkbox('Draw comfort polygons')
        psy_strategy_options = ['Comfort', 'Evaporative Cooling',
                                'Mass + Night Ventilation', 'Occupant use of fans',
                                'Capture internal heat', 'Passive solar heating', 'All']
        psy_selected_strategy = st.selectbox(
            'Select a passive strategy', options=psy_strategy_options)
    
with st.container():
    
    st.markdown(
        'A psychrometric chart can be used in two different ways. The first is done by plotting multiple data points, that represent the air conditions at a specific time, on the chart. Then, overlaying an area that identifies the “comfort zone.”  The comfort zone is defined as the range within occupants are satisfied with the surrounding thermal conditions. After plotting the air conditions and overlaying the comfort zone, it becomes possible to see how passive design strategies can extend the comfort zone.')
    
    psy_chart_figure = get_psy_chart_figure(
        global_epw, global_colorset, psy_selected_strategy, psy_load_data,
        psy_draw_polygons, psy_data)
    
    st.plotly_chart(psy_chart_figure, use_container_width=True, config=get_figure_config(f'Psychrometric_chart_{global_epw.location.city}'))

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
    
        windrose_radio = st.radio(
            '', ['from epw location', 'Visualize DBT on the Windrose!'],
            index=0, key='windrose_'
        )
    
        if windrose_radio == 'from epw location':
            
            windrose_data = None
    
        else:
            windrose_data = global_epw._get_data_by_field(fields['Dry Bulb Temperature'])
            
          
# print(dir(HourlyContinuousCollection))
def get_windrose_figure(windrose_type:str,st_month: int, st_day: int, st_hour: int, end_month: int,
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
    if windrose_type == 'from epw location':
        
        lb_ap = AnalysisPeriod(st_month, st_day, st_hour, end_month, end_day, end_hour)
        wind_dir = epw.wind_direction.filter_by_analysis_period(lb_ap)
        wind_spd = epw.wind_speed.filter_by_analysis_period(lb_ap)
        
        lb_lp = LegendParameters(colors=colorsets[global_colorset])
        
        lb_wind_rose = WindRose(wind_dir, wind_spd)
        lb_wind_rose.legend_parameters = lb_lp
    
        return lb_wind_rose.plot(title='Windrose',show_title=True)
    
    else:
        lb_ap = AnalysisPeriod(st_month, st_day, st_hour, end_month, end_day, end_hour)        
        
        fields = get_fields()
            
        windrose_data = global_epw.import_data_by_field(fields['Dry Bulb Temperature'])
        
        wind_dir = epw.wind_direction.filter_by_analysis_period(lb_ap)
        windrose_data_ = windrose_data.filter_by_analysis_period(lb_ap)
        
        lb_lp = LegendParameters(colors=colorsets[global_colorset])
        
        lb_windrose_data = WindRose(wind_dir,windrose_data_)
        lb_windrose_data.legend_parameters = lb_lp
        
        return lb_windrose_data.plot(title='Wind Direction vs. Dry Bulb Temperature', show_title=True)
 

with st.container():
    
    st.markdown('Generate a wind rose to summarise the occurrence of winds at a location, showing their strength, direction and frequency, for the selected period and environmental parameter!')
      
    windrose_figure = get_windrose_figure(windrose_radio, windrose_st_month, windrose_st_day, windrose_st_hour, windrose_end_month,
                                          windrose_end_day, windrose_end_hour, global_epw, global_colorset)
    
    st.plotly_chart(windrose_figure, use_container_width=True,
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
