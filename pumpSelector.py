import dash
from dash import dcc, html, dash_table, Input, Output, State, callback, ALL
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import json

# --- Environment Setup ---
load_dotenv("/etc/secrets/secrets.env")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# --- Translation Dictionary ---
translations = {
    "English": {
        # App title and headers
        "Hung Pump": "Hung Pump",
        "Pump Selection Tool": "Pump Selection Tool",
        "Data loaded": "Data loaded: {n_records} records | Last update: {timestamp}",
        
        # Buttons
        "Refresh Data": "🔄 Refresh Data",
        "Reset Inputs": "🔄 Reset Inputs",
        "Search": "🔍 Search",
        "Show Curve": "📈 Show Pump Curve",
        "Update Curves": "📈 Update Curves",
        
        # Step 1
        "Step 1": "Step 1: Select Basic Criteria",
        "Category": "Category:",
        "Frequency": "Frequency (Hz):",
        "Phase": "Phase:",
        "Select...": "Select...",
        "All Categories": "All Categories",
        "Show All Frequency": "Show All Frequency",
        "Show All Phase": "Show All Phase",
        
        # Categories
        "Dirty Water": "Dirty Water",
        "Clean Water": "Clean Water",
        "Speciality Pump": "Speciality Pump",
        "Grinder": "Grinder",
        "Construction": "Construction",
        "Sewage and Wastewater": "Sewage and Wastewater",
        "High Pressure": "High Pressure",
        "Booster": "Booster",
        "BLDC": "BLDC",
        
        # Application section
        "Application Input": "Application Input",
        "Floor Faucet Info": "💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM",
        "Number of Floors": "Number of Floors",
        "Number of Faucets": "Number of Faucets",
        
        # Pond drainage
        "Pond Drainage": "Pond Drainage",
        "Pond Length": "Pond Length (m)",
        "Pond Width": "Pond Width (m)",
        "Pond Height": "Pond Height (m)",
        "Drain Time": "Drain Time (hours)",
        "Pond Volume": "📏 Pond Volume: {volume} L",
        "Required Flow": "💧 Required Flow to drain pond: {flow} {unit}",
        
        # Underground
        "Pump Depth": "Pump Depth Below Ground (m)",
        "Particle Size": "Max Particle Size (mm)",
        
        # Manual Input
        "Manual Input": "Manual Input",
        "Flow Unit": "Flow Unit",
        "Flow Value": "Flow Value",
        "Head Unit": "Head Unit",
        "TDH": "Total Dynamic Head (TDH)",
        
        # Results
        "Result Display": "Result Display Control",
        "Show Percentage": "Show Top Percentage of Results",
        "Matching Pumps": "✅ Matching Pumps",
        "Found Pumps": "Found {count} matching pumps",
        "View Product": "View Product",
        
        # Pump Curves
        "Pump Curves": "Pump Performance Curves",
        "Performance Curve": "Performance Curve - {model}",
        "Flow Rate": "Flow Rate ({unit})",
        "Head": "Head ({unit})",
        "Operating Point": "Your Operating Point",
        "Multiple Curves": "Performance Comparison",
        
        # Units
        "L/min": "L/min",
        "L/sec": "L/sec",
        "m³/hr": "m³/hr",
        "m³/min": "m³/min",
        "US gpm": "US gpm",
        "m": "m",
        "ft": "ft",
        
        # Warnings & Errors
        "No Matches": "⚠️ No pumps match your criteria. Try adjusting the parameters.",
        "Failed Connection": "❌ Failed to connect to Supabase: {error}",
        "No Data": "❌ No pump data available. Please check your connection.",
    },
    "繁體中文": {
        # App title and headers
        "Hung Pump": "宏泵集團",
        "Pump Selection Tool": "水泵選型工具",
        "Data loaded": "已載入資料: {n_records} 筆記錄 | 最後更新: {timestamp}",
        
        # Buttons
        "Refresh Data": "🔄 刷新資料",
        "Reset Inputs": "🔄 重置輸入",
        "Search": "🔍 搜尋",
        "Show Curve": "📈 顯示泵浦曲線",
        "Update Curves": "📈 更新曲線",
        
        # Step 1
        "Step 1": "步驟一: 選擇基本條件",
        "Category": "類別:",
        "Frequency": "頻率 (赫茲):",
        "Phase": "相數:",
        "Select...": "請選擇...",
        "All Categories": "所有類別",
        "Show All Frequency": "顯示所有頻率",
        "Show All Phase": "顯示所有相數",
        
        # Categories - translated to Traditional Chinese
        "Dirty Water": "污水泵",
        "Clean Water": "清水泵",
        "Speciality Pump": "特殊用途泵",
        "Grinder": "研磨泵",
        "Construction": "工業泵",
        "Sewage and Wastewater": "污水和廢水泵",
        "High Pressure": "高壓泵",
        "Booster": "加壓泵",
        "BLDC": "無刷直流泵",
        
        # Application section
        "Application Input": "應用輸入",
        "Floor Faucet Info": "💡 每樓層 = 3.5 米揚程 | 每水龍頭 = 15 LPM",
        "Number of Floors": "樓層數量",
        "Number of Faucets": "水龍頭數量",
        
        # Pond drainage
        "Pond Drainage": "池塘排水",
        "Pond Length": "池塘長度 (米)",
        "Pond Width": "池塘寬度 (米)",
        "Pond Height": "池塘高度 (米)",
        "Drain Time": "排水時間 (小時)",
        "Pond Volume": "📏 池塘體積: {volume} 升",
        "Required Flow": "💧 所需排水流量: {flow} {unit}",
        
        # Underground
        "Pump Depth": "幫浦地下深度 (米)",
        "Particle Size": "最大固體顆粒尺寸 (毫米)",
        
        # Manual Input
        "Manual Input": "手動輸入",
        "Flow Unit": "流量單位",
        "Flow Value": "流量值",
        "Head Unit": "揚程單位",
        "TDH": "總動態揚程 (TDH)",
        
        # Results
        "Result Display": "結果顯示控制",
        "Show Percentage": "顯示前百分比的結果",
        "Matching Pumps": "✅ 符合條件的幫浦",
        "Found Pumps": "找到 {count} 個符合的幫浦",
        "View Product": "查看產品",
        
        # Pump Curves
        "Pump Curves": "幫浦性能曲線",
        "Performance Curve": "性能曲線 - {model}",
        "Flow Rate": "流量 ({unit})",
        "Head": "揚程 ({unit})",
        "Operating Point": "您的操作點",
        "Multiple Curves": "性能比較",
        
        # Units
        "L/min": "公升/分鐘",
        "L/sec": "公升/秒",
        "m³/hr": "立方米/小時",
        "m³/min": "立方米/分鐘",
        "US gpm": "美制加侖/分鐘",
        "m": "米",
        "ft": "英尺",
        
        # Warnings & Errors
        "No Matches": "⚠️ 沒有符合您條件的幫浦。請調整參數。",
        "Failed Connection": "❌ 連接到 Supabase 失敗: {error}",
        "No Data": "❌ 無可用幫浦資料。請檢查您的連接。",
    }
}

def get_text(key, lang="English", **kwargs):
    """Get translated text"""
    if key in translations[lang]:
        text = translations[lang][key]
        return text.format(**kwargs) if kwargs else text
    # fallback to English
    if key in translations["English"]:
        return translations["English"][key].format(**kwargs) if kwargs else translations["English"][key]
    return key

# --- Unit Conversion Functions ---
def convert_flow_from_lpm(value, to_unit):
    """Convert flow from LPM to specified unit"""
    if to_unit == "L/min":
        return value
    elif to_unit == "L/sec":
        return value / 60
    elif to_unit == "m³/hr":
        return value * 60 / 1000
    elif to_unit == "m³/min":
        return value / 1000
    elif to_unit == "US gpm":
        return value / 3.785
    return value

def convert_flow_to_lpm(value, from_unit):
    """Convert flow to LPM from specified unit"""
    if from_unit == "L/min":
        return value
    elif from_unit == "L/sec":
        return value * 60
    elif from_unit == "m³/hr":
        return value * 1000 / 60
    elif from_unit == "m³/min":
        return value * 1000
    elif from_unit == "US gpm":
        return value * 3.785
    return value

def convert_head_from_m(value, to_unit):
    """Convert head from meters to specified unit"""
    if to_unit == "m":
        return value
    elif to_unit == "ft":
        return value * 3.28084
    return value

def convert_head_to_m(value, from_unit):
    """Convert head to meters from specified unit"""
    if from_unit == "m":
        return value
    elif from_unit == "ft":
        return value * 0.3048
    return value

# --- Data Loading Functions ---
def init_connection():
    """Initialize Supabase connection"""
    try:
        return create_client(SUPABASE_URL, SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to connect to Supabase: {e}")
        return None

def load_pump_data():
    """Load pump data from Supabase or CSV fallback"""
    try:
        supabase = init_connection()
        if supabase:
            all_records, page_size, current_page = [], 1000, 0
            while True:
                response = supabase.table("pump_selection_data").select("*") \
                    .range(current_page * page_size, (current_page + 1) * page_size - 1).execute()
                if not response.data:
                    break
                all_records.extend(response.data)
                current_page += 1
                if len(response.data) < page_size:
                    break
            return pd.DataFrame(all_records)
    except Exception as e:
        print(f"Failed to load from Supabase: {e}")
    
    try:
        return pd.read_csv("Pump Selection Data.csv")
    except Exception as e:
        print(f"Failed to load CSV: {e}")
        return pd.DataFrame()

def load_pump_curve_data():
    """Load pump curve data from Supabase or CSV fallback"""
    try:
        supabase = init_connection()
        if supabase:
            all_records, page_size, current_page = [], 1000, 0
            while True:
                response = supabase.table("pump_curve_data").select("*") \
                    .range(current_page * page_size, (current_page + 1) * page_size - 1).execute()
                if not response.data:
                    break
                all_records.extend(response.data)
                current_page += 1
                if len(response.data) < page_size:
                    break
            return pd.DataFrame(all_records)
    except Exception as e:
        print(f"Failed to load curve data from Supabase: {e}")
    
    try:
        return pd.read_csv("pump_curve_data_rows 1.csv")
    except Exception as e:
        print(f"Failed to load curve CSV: {e}")
        return pd.DataFrame()

# --- Chart Creation Functions ---
def create_pump_curve_chart(curve_data, model_no, user_flow=None, user_head=None, flow_unit="L/min", head_unit="m", lang="English"):
    """Create performance curve chart for a single pump"""
    head_columns = [col for col in curve_data.columns if col.endswith('M') and col not in ['Max Head(M)']]
    fig = go.Figure()
    
    pump_data = curve_data[curve_data['Model No.'] == model_no]
    if pump_data.empty:
        return None
    
    pump_row = pump_data.iloc[0]
    flows, heads = [], []
    
    for col in head_columns:
        try:
            head_value = float(col.replace('M', ''))
            flow_value = pd.to_numeric(pump_row[col], errors='coerce')
            if not pd.isna(flow_value) and flow_value > 0:
                flows.append(convert_flow_from_lpm(flow_value, flow_unit))
                heads.append(convert_head_from_m(head_value, head_unit))
        except:
            continue
    
    if flows and heads:
        sorted_data = sorted(zip(flows, heads))
        flows, heads = zip(*sorted_data)
        
        fig.add_trace(go.Scatter(
            x=flows, y=heads, mode='lines+markers',
            name=f'{model_no} - Head Curve',
            line=dict(color='blue', width=3), 
            marker=dict(size=8),
            hovertemplate=f'Flow: %{{x:.2f}} {flow_unit}<br>Head: %{{y:.2f}} {head_unit}<extra></extra>'
        ))
    
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        display_flow = convert_flow_from_lpm(user_flow, flow_unit)
        display_head = convert_head_from_m(user_head, head_unit)
        fig.add_trace(go.Scatter(
            x=[display_flow], y=[display_head], mode='markers',
            name=get_text("Operating Point", lang),
            marker=dict(size=15, color='red', symbol='star'),
            hovertemplate=f'Flow: {display_flow:.2f} {flow_unit}<br>Head: {display_head:.2f} {head_unit}<extra></extra>'
        ))
    
    fig.update_layout(
        title=get_text("Performance Curve", lang, model=model_no),
        xaxis_title=get_text("Flow Rate", lang, unit=flow_unit), 
        yaxis_title=get_text("Head", lang, unit=head_unit),
        hovermode='closest', 
        showlegend=True, 
        height=500, 
        template='plotly_white'
    )
    
    return fig

def create_comparison_chart(curve_data, model_nos, user_flow=None, user_head=None, flow_unit="L/min", head_unit="m", lang="English"):
    """Create comparison chart for multiple pumps"""
    fig = go.Figure()
    colors = ['blue', 'red', 'green', 'orange', 'purple', 'brown', 'pink', 'gray']
    
    for i, model_no in enumerate(model_nos):
        pump_data = curve_data[curve_data['Model No.'] == model_no]
        if pump_data.empty:
            continue
        
        pump_row = pump_data.iloc[0]
        head_columns = [col for col in curve_data.columns if col.endswith('M') and col not in ['Max Head(M)']]
        flows, heads = [], []
        
        for col in head_columns:
            try:
                head_value = float(col.replace('M', ''))
                flow_value = pd.to_numeric(pump_row[col], errors='coerce')
                if not pd.isna(flow_value) and flow_value > 0:
                    flows.append(convert_flow_from_lpm(flow_value, flow_unit))
                    heads.append(convert_head_from_m(head_value, head_unit))
            except:
                continue
        
        if flows and heads:
            sorted_data = sorted(zip(flows, heads))
            flows, heads = zip(*sorted_data)
            fig.add_trace(go.Scatter(
                x=flows, y=heads, mode='lines+markers',
                name=model_no,
                line=dict(color=colors[i % len(colors)], width=3),
                marker=dict(size=6),
                hovertemplate=f'Flow: %{{x:.2f}} {flow_unit}<br>Head: %{{y:.2f}} {head_unit}<extra></extra>'
            ))
    
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        display_flow = convert_flow_from_lpm(user_flow, flow_unit)
        display_head = convert_head_from_m(user_head, head_unit)
        fig.add_trace(go.Scatter(
            x=[display_flow], y=[display_head], mode='markers',
            name=get_text("Operating Point", lang),
            marker=dict(size=15, color='red', symbol='star'),
            hovertemplate=f'Flow: {display_flow:.2f} {flow_unit}<br>Head: {display_head:.2f} {head_unit}<extra></extra>'
        ))
    
    fig.update_layout(
        title=get_text("Multiple Curves", lang),
        xaxis_title=get_text("Flow Rate", lang, unit=flow_unit),
        yaxis_title=get_text("Head", lang, unit=head_unit),
        hovermode='closest', 
        showlegend=True, 
        height=500, 
        template='plotly_white'
    )
    
    return fig

# --- Initialize Dash App ---
app = dash.Dash(__name__)
app.title = "Pump Selection Tool"

# Load initial data
pumps_df = load_pump_data()
curve_df = load_pump_curve_data()

# --- App Layout ---
app.layout = html.Div([
    # Store components for state management
    dcc.Store(id='language-store', data='English'),
    dcc.Store(id='pumps-data-store', data=pumps_df.to_dict('records') if not pumps_df.empty else []),
    dcc.Store(id='curve-data-store', data=curve_df.to_dict('records') if not curve_df.empty else []),
    dcc.Store(id='filtered-pumps-store', data=[]),
    dcc.Store(id='selected-pumps-store', data=[]),
    dcc.Store(id='user-operating-point-store', data={'flow': 0, 'head': 0}),
    
    # Header Section
    html.Div([
        html.Div([
            html.Img(src="https://www.hungpump.com/images/340357", style={'height': '80px', 'width': 'auto'}),
        ], style={'width': '15%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            html.H1(id='app-title', children="Hung Pump", 
                   style={'color': '#0057B8', 'margin': '0', 'padding-left': '15px'})
        ], style={'width': '60%', 'display': 'inline-block', 'vertical-align': 'top'}),
        
        html.Div([
            dcc.Dropdown(
                id='language-dropdown',
                options=[
                    {'label': 'English', 'value': 'English'},
                    {'label': '繁體中文', 'value': '繁體中文'}
                ],
                value='English',
                clearable=False,
                style={'width': '150px'}
            )
        ], style={'width': '25%', 'display': 'inline-block', 'vertical-align': 'top', 'text-align': 'right'}),
    ], style={'padding': '20px', 'background-color': '#f8f9fa'}),
    
    # Main title
    html.H2(id='main-title', children="Pump Selection Tool", style={'text-align': 'center', 'margin': '20px 0'}),
    
    # Data info and control buttons
    html.Div([
        html.Div([
            html.P(id='data-info', children="Data loading...", style={'margin': '5px 0', 'font-size': '14px'}),
            html.P(id='curve-info', children="", style={'margin': '5px 0', 'font-size': '14px'}),
        ], style={'width': '70%', 'display': 'inline-block'}),
        
        html.Div([
            html.Button(id='refresh-button', children="🔄 Refresh Data", 
                       style={'margin-right': '10px', 'padding': '8px 16px'}),
            html.Button(id='reset-button', children="🔄 Reset Inputs", 
                       style={'padding': '8px 16px'}),
        ], style={'width': '30%', 'display': 'inline-block', 'text-align': 'right'}),
    ], style={'padding': '10px 20px', 'background-color': '#f8f9fa', 'margin-bottom': '20px'}),
    
    # Main content
    html.Div([
        # Left column - Input controls
        html.Div([
            # Step 1: Basic Criteria
            html.Div([
                html.H3(id='step1-title', children="🔧 Step 1: Select Basic Criteria"),
                
                html.Label(id='category-label', children="Category:"),
                dcc.Dropdown(id='category-dropdown', placeholder="Select...", style={'margin-bottom': '15px'}),
                
                html.Label(id='frequency-label', children="Frequency (Hz):"),
                dcc.Dropdown(id='frequency-dropdown', placeholder="Select...", style={'margin-bottom': '15px'}),
                
                html.Label(id='phase-label', children="Phase:"),
                dcc.Dropdown(id='phase-dropdown', placeholder="Select...", style={'margin-bottom': '20px'}),
            ], style={'padding': '15px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'}),
            
            # Application Input (for Booster category)
            html.Div(id='application-section', children=[
                html.H4(id='application-title', children="🏢 Application Input"),
                html.P(id='floor-faucet-info', children="💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM"),
                
                html.Label(id='floors-label', children="Number of Floors"),
                dcc.Input(id='floors-input', type='number', value=0, min=0, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Label(id='faucets-label', children="Number of Faucets"),
                dcc.Input(id='faucets-input', type='number', value=0, min=0, style={'width': '100%', 'margin-bottom': '15px'}),
            ], style={'padding': '15px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px', 'display': 'none'}),
            
            # Pond Drainage
            html.Div([
                html.H4(id='pond-title', children="🌊 Pond Drainage"),
                
                html.Label(id='length-label', children="Pond Length (m)"),
                dcc.Input(id='length-input', type='number', value=0, min=0, step=0.1, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Label(id='width-label', children="Pond Width (m)"),
                dcc.Input(id='width-input', type='number', value=0, min=0, step=0.1, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Label(id='height-label', children="Pond Height (m)"),
                dcc.Input(id='height-input', type='number', value=0, min=0, step=0.1, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Label(id='drain-time-label', children="Drain Time (hours)"),
                dcc.Input(id='drain-time-input', type='number', value=1, min=0.01, step=0.1, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Div(id='pond-volume-display', style={'margin': '10px 0', 'font-weight': 'bold', 'color': '#28a745'}),
                html.Div(id='required-flow-display', style={'margin': '10px 0', 'font-weight': 'bold', 'color': '#007bff'}),
            ], style={'padding': '15px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'}),
            
            # Underground & Particle Size
            html.Div([
                html.Label(id='depth-label', children="Pump Depth Below Ground (m)"),
                dcc.Input(id='depth-input', type='number', value=0, min=0, step=0.1, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Label(id='particle-label', children="Max Particle Size (mm)"),
                dcc.Input(id='particle-input', type='number', value=0, min=0, step=1, style={'width': '100%', 'margin-bottom': '15px'}),
            ], style={'padding': '15px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'}),
            
            # Manual Input
            html.Div([
                html.H4(id='manual-title', children="Manual Input"),
                
                html.Label(id='flow-unit-label', children="Flow Unit"),
                dcc.RadioItems(
                    id='flow-unit-radio',
                    options=[
                        {'label': 'L/min', 'value': 'L/min'},
                        {'label': 'L/sec', 'value': 'L/sec'},
                        {'label': 'm³/hr', 'value': 'm³/hr'},
                        {'label': 'm³/min', 'value': 'm³/min'},
                        {'label': 'US gpm', 'value': 'US gpm'}
                    ],
                    value='L/min',
                    inline=True,
                    style={'margin-bottom': '10px'}
                ),
                
                html.Label(id='flow-value-label', children="Flow Value"),
                dcc.Input(id='flow-value-input', type='number', value=0, min=0, step=10, style={'width': '100%', 'margin-bottom': '10px'}),
                
                html.Label(id='head-unit-label', children="Head Unit"),
                dcc.RadioItems(
                    id='head-unit-radio',
                    options=[
                        {'label': 'm', 'value': 'm'},
                        {'label': 'ft', 'value': 'ft'}
                    ],
                    value='m',
                    inline=True,
                    style={'margin-bottom': '10px'}
                ),
                
                html.Label(id='head-value-label', children="Total Dynamic Head (TDH)"),
                dcc.Input(id='head-value-input', type='number', value=0, min=0, step=1, style={'width': '100%', 'margin-bottom': '15px'}),
            ], style={'padding': '15px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'}),
            
            # Result percentage and search
            html.Div([
                html.Label(id='percentage-label', children="Show Top Percentage of Results"),
                dcc.Slider(
                    id='percentage-slider',
                    min=5, max=100, step=1, value=100,
                    marks={i: f'{i}%' for i in range(10, 101, 20)},
                    tooltip={"placement": "bottom", "always_visible": True}
                ),
            ], style={'margin-bottom': '20px'}),
            
            html.Button(id='search-button', children="🔍 Search", 
                       style={'width': '100%', 'padding': '12px', 'font-size': '16px', 
                             'background-color': '#007bff', 'color': 'white', 'border': 'none', 'border-radius': '5px'}),
        ], style={'width': '35%', 'display': 'inline-block', 'vertical-align': 'top', 'padding-right': '20px'}),
        
        # Right column - Results and charts
        html.Div([
            # Results section
            html.Div(id='results-section', children=[
                html.H3(id='results-title', children="Search Results"),
                html.Div(id='results-info', children="Run a search to see results.", 
                        style={'padding': '20px', 'text-align': 'center', 'color': '#666'}),
                html.Div(id='results-table-container'),
            ], style={'margin-bottom': '30px'}),
            
            # Pump curves section
            html.Div(id='curves-section', children=[
                html.H3(id='curves-title', children="📈 Pump Performance Curves"),
                html.Div(id='curves-info', children="Select pumps from the table above to view their performance curves.",
                        style={'padding': '20px', 'text-align': 'center', 'color': '#666'}),
                html.Div(id='curves-container'),
            ]),
        ], style={'width': '65%', 'display': 'inline-block', 'vertical-align': 'top'}),
    ], style={'padding': '0 20px'}),
    
    # Hidden div to trigger callbacks
    html.Div(id='trigger-div', style={'display': 'none'}),
])

# --- Callbacks ---

@app.callback(
    [Output('language-store', 'data'),
     Output('app-title', 'children'),
     Output('main-title', 'children'),
     Output('step1-title', 'children'),
     Output('category-label', 'children'),
     Output('frequency-label', 'children'),
     Output('phase-label', 'children'),
     Output('application-title', 'children'),
     Output('floor-faucet-info', 'children'),
     Output('floors-label', 'children'),
     Output('faucets-label', 'children'),
     Output('pond-title', 'children'),
     Output('length-label', 'children'),
     Output('width-label', 'children'),
     Output('height-label', 'children'),
     Output('drain-time-label', 'children'),
     Output('depth-label', 'children'),
     Output('particle-label', 'children'),
     Output('manual-title', 'children'),
     Output('flow-unit-label', 'children'),
     Output('flow-value-label', 'children'),
     Output('head-unit-label', 'children'),
     Output('head-value-label', 'children'),
     Output('percentage-label', 'children'),
     Output('search-button', 'children'),
     Output('refresh-button', 'children'),
     Output('reset-button', 'children'),
     Output('results-title', 'children'),
     Output('curves-title', 'children')],
    [Input('language-dropdown', 'value')]
)
def update_language(selected_language):
    """Update all text based on selected language"""
    lang = selected_language
    
    return (
        lang,
        get_text("Hung Pump", lang),
        get_text("Pump Selection Tool", lang),
        get_text("Step 1", lang),
        get_text("Category", lang),
        get_text("Frequency", lang),
        get_text("Phase", lang),
        get_text("Application Input", lang),
        get_text("Floor Faucet Info", lang),
        get_text("Number of Floors", lang),
        get_text("Number of Faucets", lang),
        get_text("Pond Drainage", lang),
        get_text("Pond Length", lang),
        get_text("Pond Width", lang),
        get_text("Pond Height", lang),
        get_text("Drain Time", lang),
        get_text("Pump Depth", lang),
        get_text("Particle Size", lang),
        get_text("Manual Input", lang),
        get_text("Flow Unit", lang),
        get_text("Flow Value", lang),
        get_text("Head Unit", lang),
        get_text("TDH", lang),
        get_text("Show Percentage", lang),
        get_text("Search", lang),
        get_text("Refresh Data", lang),
        get_text("Reset Inputs", lang),
        get_text("Matching Pumps", lang),
        get_text("Pump Curves", lang)
    )

@app.callback(
    [Output('data-info', 'children'),
     Output('curve-info', 'children')],
    [Input('trigger-div', 'children'),
     Input('language-store', 'data')]
)
def update_data_info(trigger, lang):
    """Update data information display"""
    pumps_count = len(pumps_df) if not pumps_df.empty else 0
    curve_count = len(curve_df) if not curve_df.empty else 0
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    data_text = get_text("Data loaded", lang, n_records=pumps_count, timestamp=timestamp)
    curve_text = f"Curve data loaded: {curve_count} pumps with curve data" if curve_count > 0 else ""
    
    return data_text, curve_text

@app.callback(
    [Output('category-dropdown', 'options'),
     Output('category-dropdown', 'value')],
    [Input('language-store', 'data')]
)
def update_category_options(lang):
    """Update category dropdown options based on language and data"""
    if pumps_df.empty:
        return [], None
    
    # Clean category data
    if "Category" in pumps_df.columns:
        pumps_df["Category"] = pumps_df["Category"].astype(str).str.strip().replace(["nan", "None", "NaN"], "")
        unique_categories = [c for c in pumps_df["Category"].unique() if c and c.strip() and c.lower() not in ["nan", "none"]]
        
        options = [{'label': get_text("All Categories", lang), 'value': 'All Categories'}]
        for cat in sorted(unique_categories):
            translated_cat = get_text(cat, lang)
            options.append({'label': translated_cat, 'value': cat})
        
        return options, 'All Categories'
    
    return [{'label': get_text("All Categories", lang), 'value': 'All Categories'}], 'All Categories'

@app.callback(
    [Output('frequency-dropdown', 'options'),
     Output('frequency-dropdown', 'value')],
    [Input('language-store', 'data')]
)
def update_frequency_options(lang):
    """Update frequency dropdown options"""
    if pumps_df.empty or "Frequency (Hz)" not in pumps_df.columns:
        return [{'label': get_text("Show All Frequency", lang), 'value': 'All'}], 'All'
    
    freq_series = pd.to_numeric(pumps_df["Frequency (Hz)"], errors='coerce')
    freq_options = sorted(freq_series.dropna().unique())
    
    options = [{'label': get_text("Show All Frequency", lang), 'value': 'All'}]
    for freq in freq_options:
        options.append({'label': str(freq), 'value': freq})
    
    return options, 'All'

@app.callback(
    [Output('phase-dropdown', 'options'),
     Output('phase-dropdown', 'value')],
    [Input('language-store', 'data')]
)
def update_phase_options(lang):
    """Update phase dropdown options"""
    if pumps_df.empty or "Phase" not in pumps_df.columns:
        return [{'label': get_text("Show All Phase", lang), 'value': 'All'}], 'All'
    
    phase_series = pd.to_numeric(pumps_df["Phase"], errors='coerce')
    phase_options = [p for p in sorted(phase_series.dropna().unique()) if p in [1, 3]]
    
    options = [{'label': get_text("Show All Phase", lang), 'value': 'All'}]
    for phase in phase_options:
        options.append({'label': str(int(phase)), 'value': phase})
    
    return options, 'All'

@app.callback(
    [Output('application-section', 'style'),
     Output('flow-value-input', 'value'),
     Output('head-value-input', 'value')],
    [Input('category-dropdown', 'value'),
     Input('floors-input', 'value'),
     Input('faucets-input', 'value'),
     Input('length-input', 'value'),
     Input('width-input', 'value'),
     Input('height-input', 'value'),
     Input('drain-time-input', 'value'),
     Input('depth-input', 'value'),
     Input('flow-unit-radio', 'value'),
     Input('head-unit-radio', 'value')]
)
def update_calculations(category, floors, faucets, length, width, height, drain_time, depth, flow_unit, head_unit):
    """Update automatic calculations and show/hide application section"""
    # Show application section only for Booster category
    app_style = {'padding': '15px', 'border': '1px solid #ddd', 'border-radius': '5px', 'margin-bottom': '20px'}
    if category != "Booster":
        app_style['display'] = 'none'
    
    # Calculate pond drainage
    pond_volume = length * width * height * 1000 if all([length, width, height]) else 0
    drain_time_min = drain_time * 60 if drain_time > 0 else 0.01
    pond_lpm = pond_volume / drain_time_min if drain_time_min > 0 else 0
    
    # Calculate auto values
    if category == "Booster":
        auto_flow = max((faucets or 0) * 15, pond_lpm)
        auto_tdh = max((floors or 0) * 3.5, height or 0)
    else:
        auto_flow = pond_lpm
        auto_tdh = depth if depth > 0 else (height or 0)
    
    # Convert to display units
    auto_flow_display = convert_flow_from_lpm(auto_flow, flow_unit) if auto_flow > 0 else 0
    auto_tdh_display = convert_head_from_m(auto_tdh, head_unit) if auto_tdh > 0 else 0
    
    return app_style, round(auto_flow_display, 2), round(auto_tdh_display, 2)

@app.callback(
    [Output('pond-volume-display', 'children'),
     Output('required-flow-display', 'children')],
    [Input('length-input', 'value'),
     Input('width-input', 'value'),
     Input('height-input', 'value'),
     Input('drain-time-input', 'value'),
     Input('flow-unit-radio', 'value'),
     Input('language-store', 'data')]
)
def update_pond_calculations(length, width, height, drain_time, flow_unit, lang):
    """Update pond volume and required flow calculations"""
    if not all([length, width, height, drain_time]) or any(v <= 0 for v in [length, width, height, drain_time]):
        return "", ""
    
    pond_volume = length * width * height * 1000
    drain_time_min = drain_time * 60
    pond_lpm = pond_volume / drain_time_min
    pond_flow_display = convert_flow_from_lpm(pond_lpm, flow_unit)
    
    volume_text = get_text("Pond Volume", lang, volume=round(pond_volume))
    flow_text = get_text("Required Flow", lang, flow=round(pond_flow_display, 2), unit=flow_unit)
    
    return volume_text, flow_text

@app.callback(
    [Output('floors-input', 'value'),
     Output('faucets-input', 'value'),
     Output('length-input', 'value'),
     Output('width-input', 'value'),
     Output('height-input', 'value'),
     Output('drain-time-input', 'value'),
     Output('depth-input', 'value'),
     Output('particle-input', 'value'),
     Output('category-dropdown', 'value'),
     Output('frequency-dropdown', 'value'),
     Output('phase-dropdown', 'value'),
     Output('flow-unit-radio', 'value'),
     Output('head-unit-radio', 'value'),
     Output('percentage-slider', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def reset_inputs(n_clicks):
    """Reset all input values"""
    if n_clicks:
        return 0, 0, 0, 0, 0, 1, 0, 0, 'All Categories', 'All', 'All', 'L/min', 'm', 100
    return dash.no_update

@app.callback(
    [Output('filtered-pumps-store', 'data'),
     Output('user-operating-point-store', 'data'),
     Output('results-info', 'children'),
     Output('results-table-container', 'children')],
    [Input('search-button', 'n_clicks')],
    [State('category-dropdown', 'value'),
     State('frequency-dropdown', 'value'),
     State('phase-dropdown', 'value'),
     State('flow-value-input', 'value'),
     State('head-value-input', 'value'),
     State('particle-input', 'value'),
     State('flow-unit-radio', 'value'),
     State('head-unit-radio', 'value'),
     State('percentage-slider', 'value'),
     State('language-store', 'data')]
)
def perform_search(n_clicks, category, frequency, phase, flow_value, head_value, particle_size, 
                  flow_unit, head_unit, percentage, lang):
    """Perform pump search based on criteria"""
    if not n_clicks or pumps_df.empty:
        return [], {'flow': 0, 'head': 0}, "Run a search to see results.", html.Div()
    
    # Filter pumps
    filtered_pumps = pumps_df.copy()
    
    # Apply filters
    if category and category != 'All Categories':
        filtered_pumps = filtered_pumps[filtered_pumps["Category"] == category]
    
    if frequency and frequency != 'All':
        filtered_pumps["Frequency (Hz)"] = pd.to_numeric(filtered_pumps["Frequency (Hz)"], errors='coerce')
        filtered_pumps = filtered_pumps[filtered_pumps["Frequency (Hz)"] == frequency]
    
    if phase and phase != 'All':
        filtered_pumps["Phase"] = pd.to_numeric(filtered_pumps["Phase"], errors='coerce')
        filtered_pumps = filtered_pumps[filtered_pumps["Phase"] == phase]
    
    # Convert user input to LPM and meters for filtering
    flow_lpm = convert_flow_to_lpm(flow_value or 0, flow_unit)
    head_m = convert_head_to_m(head_value or 0, head_unit)
    
    # Filter by flow and head
    if "Q Rated/LPM" in filtered_pumps.columns:
        filtered_pumps["Q Rated/LPM"] = pd.to_numeric(filtered_pumps["Q Rated/LPM"], errors="coerce").fillna(0)
        if flow_lpm > 0:
            filtered_pumps = filtered_pumps[filtered_pumps["Q Rated/LPM"] >= flow_lpm]
    
    if "Head Rated/M" in filtered_pumps.columns:
        filtered_pumps["Head Rated/M"] = pd.to_numeric(filtered_pumps["Head Rated/M"], errors="coerce").fillna(0)
        if head_m > 0:
            filtered_pumps = filtered_pumps[filtered_pumps["Head Rated/M"] >= head_m]
    
    # Filter by particle size
    if particle_size and particle_size > 0 and "Pass Solid Dia(mm)" in filtered_pumps.columns:
        filtered_pumps["Pass Solid Dia(mm)"] = pd.to_numeric(filtered_pumps["Pass Solid Dia(mm)"], errors="coerce").fillna(0)
        filtered_pumps = filtered_pumps[filtered_pumps["Pass Solid Dia(mm)"] >= particle_size]
    
    if filtered_pumps.empty:
        return [], {'flow': flow_lpm, 'head': head_m}, get_text("No Matches", lang), html.Div()
    
    # Apply percentage limit
    max_to_show = max(1, int(len(filtered_pumps) * (percentage / 100)))
    filtered_pumps = filtered_pumps.head(max_to_show).reset_index(drop=True)
    
    # Add converted columns for display
    if "Q Rated/LPM" in filtered_pumps.columns:
        filtered_pumps[f"Q Rated ({flow_unit})"] = filtered_pumps["Q Rated/LPM"].apply(
            lambda x: round(convert_flow_from_lpm(x, flow_unit), 2)
        )
    
    if "Head Rated/M" in filtered_pumps.columns:
        filtered_pumps[f"Head Rated ({head_unit})"] = filtered_pumps["Head Rated/M"].apply(
            lambda x: round(convert_head_from_m(x, head_unit), 2)
        )
    
    # Prepare table columns
    essential_columns = ["Model", "Model No."]
    columns_to_show = []
    
    for col in essential_columns:
        if col in filtered_pumps.columns:
            columns_to_show.append(col)
    
    # Add converted flow and head columns
    if f"Q Rated ({flow_unit})" in filtered_pumps.columns:
        columns_to_show.append(f"Q Rated ({flow_unit})")
    if f"Head Rated ({head_unit})" in filtered_pumps.columns:
        columns_to_show.append(f"Head Rated ({head_unit})")
    
    # Add other important columns
    other_cols = ["Category", "Frequency (Hz)", "Phase", "Max Head(M)", "Product Link"]
    for col in other_cols:
        if col in filtered_pumps.columns and col not in columns_to_show:
            columns_to_show.append(col)
    
    # Create DataTable
    display_df = filtered_pumps[columns_to_show].copy()
    
    # Add selection column
    model_column = "Model" if "Model" in display_df.columns else "Model No."
    display_df.insert(0, "Select", False)
    
    table_columns = [{"name": "Select", "id": "Select", "type": "boolean"}]
    
    for col in columns_to_show:
        if col == "Product Link":
            table_columns.append({
                "name": get_text("View Product", lang),
                "id": col,
                "type": "text",
                "presentation": "markdown"
            })
        else:
            table_columns.append({"name": col, "id": col})
    
    # Format Product Link column for markdown links
    if "Product Link" in display_df.columns:
        display_df["Product Link"] = display_df["Product Link"].apply(
            lambda x: f"[{get_text('View Product', lang)}]({x})" if pd.notna(x) and x.strip() else ""
        )
    
    results_table = dash_table.DataTable(
        id='results-table',
        data=display_df.to_dict('records'),
        columns=table_columns,
        editable=False,
        row_selectable='multi',
        selected_rows=[],
        style_cell={'textAlign': 'left', 'padding': '10px'},
        style_header={'backgroundColor': '#f8f9fa', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'white'},
        page_size=10,
        sort_action="native",
        filter_action="native"
    )
    
    results_info = get_text("Found Pumps", lang, count=len(filtered_pumps))
    
    return (filtered_pumps.to_dict('records'), 
            {'flow': flow_lpm, 'head': head_m}, 
            results_info, 
            results_table)

@app.callback(
    [Output('selected-pumps-store', 'data')],
    [Input('results-table', 'selected_rows')],
    [State('filtered-pumps-store', 'data')]
)
def update_selected_pumps(selected_rows, filtered_pumps_data):
    """Update selected pumps based on table selection"""
    if not selected_rows or not filtered_pumps_data:
        return [[]]
    
    filtered_df = pd.DataFrame(filtered_pumps_data)
    model_column = "Model" if "Model" in filtered_df.columns else "Model No."
    
    selected_models = []
    for idx in selected_rows:
        if idx < len(filtered_df):
            selected_models.append(filtered_df.iloc[idx][model_column])
    
    return [selected_models]

@app.callback(
    [Output('curves-info', 'children'),
     Output('curves-container', 'children')],
    [Input('selected-pumps-store', 'data')],
    [State('user-operating-point-store', 'data'),
     State('flow-unit-radio', 'value'),
     State('head-unit-radio', 'value'),
     State('language-store', 'data')]
)
def update_pump_curves(selected_models, operating_point, flow_unit, head_unit, lang):
    """Update pump performance curves based on selected pumps"""
    if not selected_models or not selected_models[0] or curve_df.empty:
        return "Select pumps from the table above to view their performance curves.", html.Div()
    
    models = selected_models[0]
    user_flow = operating_point.get('flow', 0)
    user_head = operating_point.get('head', 0)
    
    # Filter available models that have curve data
    available_models = [model for model in models if model in curve_df["Model No."].values]
    
    if not available_models:
        return "The selected pumps do not have curve data available.", html.Div()
    
    charts = []
    
    if len(available_models) == 1:
        # Single pump curve
        fig = create_pump_curve_chart(
            curve_df, available_models[0], user_flow, user_head, flow_unit, head_unit, lang
        )
        if fig:
            charts.append(dcc.Graph(figure=fig, style={'height': '500px'}))
    else:
        # Multiple pump comparison
        fig_comp = create_comparison_chart(
            curve_df, available_models, user_flow, user_head, flow_unit, head_unit, lang
        )
        if fig_comp:
            charts.append(html.H4(f"Performance Comparison - {len(available_models)} Pumps"))
            charts.append(html.P(f"Comparing: {', '.join(available_models)}"))
            charts.append(dcc.Graph(figure=fig_comp, style={'height': '500px'}))
            
            # Individual curves in expandable section
            charts.append(html.Details([
                html.Summary("View Individual Pump Curves", style={'font-weight': 'bold', 'margin': '20px 0 10px 0'}),
                html.Div([
                    html.Div([
                        html.H5(f"Performance Curve - {model}"),
                        dcc.Graph(
                            figure=create_pump_curve_chart(
                                curve_df, model, user_flow, user_head, flow_unit, head_unit, lang
                            ),
                            style={'height': '400px'}
                        )
                    ], style={'margin-bottom': '20px'})
                    for model in available_models
                    if create_pump_curve_chart(curve_df, model, user_flow, user_head, flow_unit, head_unit, lang)
                ])
            ]))
    
    info_text = f"Selected {len(available_models)} pump(s) for curve visualization"
    return info_text, html.Div(charts)

# --- Run the App ---
server = app.server
if __name__ == '__main__':
    app.run_server(debug=True)
