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
            line=dict(color='#0066CC', width=4), 
            marker=dict(size=10, color='#0066CC'),
            hovertemplate=f'<b>Flow:</b> %{{x:.2f}} {flow_unit}<br><b>Head:</b> %{{y:.2f}} {head_unit}<extra></extra>'
        ))
    
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        display_flow = convert_flow_from_lpm(user_flow, flow_unit)
        display_head = convert_head_from_m(user_head, head_unit)
        fig.add_trace(go.Scatter(
            x=[display_flow], y=[display_head], mode='markers',
            name=get_text("Operating Point", lang),
            marker=dict(size=20, color='#FF4444', symbol='star'),
            hovertemplate=f'<b>Operating Point</b><br>Flow: {display_flow:.2f} {flow_unit}<br>Head: {display_head:.2f} {head_unit}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=get_text("Performance Curve", lang, model=model_no),
            font=dict(size=20, color='#2c3e50'),
            x=0.5
        ),
        xaxis=dict(
            title=get_text("Flow Rate", lang, unit=flow_unit),
            gridcolor='#e1e5e9',
            linecolor='#bdc3c7',
            title_font=dict(size=16, color='#34495e'),
            tickfont=dict(size=14, color='#34495e')
        ),
        yaxis=dict(
            title=get_text("Head", lang, unit=head_unit),
            gridcolor='#e1e5e9',
            linecolor='#bdc3c7',
            title_font=dict(size=16, color='#34495e'),
            tickfont=dict(size=14, color='#34495e')
        ),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        hovermode='closest', 
        showlegend=True,
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#bdc3c7',
            borderwidth=1
        ),
        height=500,
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    return fig

def create_comparison_chart(curve_data, model_nos, user_flow=None, user_head=None, flow_unit="L/min", head_unit="m", lang="English"):
    """Create comparison chart for multiple pumps"""
    fig = go.Figure()
    colors = ['#0066CC', '#FF6B35', '#28A745', '#FFC107', '#6F42C1', '#FD7E14', '#E83E8C', '#20C997']
    
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
                marker=dict(size=8, color=colors[i % len(colors)]),
                hovertemplate=f'<b>{model_no}</b><br>Flow: %{{x:.2f}} {flow_unit}<br>Head: %{{y:.2f}} {head_unit}<extra></extra>'
            ))
    
    if user_flow and user_head and user_flow > 0 and user_head > 0:
        display_flow = convert_flow_from_lpm(user_flow, flow_unit)
        display_head = convert_head_from_m(user_head, head_unit)
        fig.add_trace(go.Scatter(
            x=[display_flow], y=[display_head], mode='markers',
            name=get_text("Operating Point", lang),
            marker=dict(size=20, color='#FF4444', symbol='star'),
            hovertemplate=f'<b>Operating Point</b><br>Flow: {display_flow:.2f} {flow_unit}<br>Head: {display_head:.2f} {head_unit}<extra></extra>'
        ))
    
    fig.update_layout(
        title=dict(
            text=get_text("Multiple Curves", lang),
            font=dict(size=20, color='#2c3e50'),
            x=0.5
        ),
        xaxis=dict(
            title=get_text("Flow Rate", lang, unit=flow_unit),
            gridcolor='#e1e5e9',
            linecolor='#bdc3c7',
            title_font=dict(size=16, color='#34495e'),
            tickfont=dict(size=14, color='#34495e')
        ),
        yaxis=dict(
            title=get_text("Head", lang, unit=head_unit),
            gridcolor='#e1e5e9',
            linecolor='#bdc3c7',
            title_font=dict(size=16, color='#34495e'),
            tickfont=dict(size=14, color='#34495e')
        ),
        plot_bgcolor='#f8f9fa',
        paper_bgcolor='white',
        hovermode='closest', 
        showlegend=True,
        legend=dict(
            bgcolor='rgba(255,255,255,0.9)',
            bordercolor='#bdc3c7',
            borderwidth=1
        ),
        height=500,
        margin=dict(l=60, r=30, t=60, b=60)
    )
    
    return fig

# --- Initialize Dash App ---
app = dash.Dash(__name__)
app.title = "Hung Pump - Professional Pump Selection Tool"

# Custom CSS for modern styling
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
        <style>
            :root {
                --primary-color: #0066CC;
                --secondary-color: #4A90E2;
                --accent-color: #FF6B35;
                --success-color: #28A745;
                --warning-color: #FFC107;
                --danger-color: #DC3545;
                --dark-color: #2C3E50;
                --light-color: #F8F9FA;
                --border-color: #E2E8F0;
                --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
                --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
                --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
                --border-radius: 12px;
            }
            
            * {
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif !important;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
                margin: 0 !important;
                padding: 0 !important;
                min-height: 100vh;
            }
            
            #react-entry-point {
                background: transparent;
            }
            
            ._dash-undo-redo {
                display: none;
            }
            
            .main-container {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 20px;
                margin: 20px;
                box-shadow: var(--shadow-lg);
                overflow: hidden;
            }
            
            .modern-card {
                background: white;
                border-radius: var(--border-radius);
                box-shadow: var(--shadow-md);
                padding: 24px;
                margin-bottom: 24px;
                border: 1px solid var(--border-color);
                transition: all 0.3s ease;
            }
            
            .modern-card:hover {
                box-shadow: var(--shadow-lg);
                transform: translateY(-2px);
            }
            
            .header-card {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
                color: white;
                border: none;
                margin-bottom: 0;
            }
            
            .status-bar {
                background: linear-gradient(90deg, var(--light-color) 0%, #ffffff 100%);
                border-bottom: 1px solid var(--border-color);
                padding: 16px 24px;
                display: flex;
                align-items: center;
                justify-content: space-between;
            }
            
            .modern-input {
                width: 100% !important;
                padding: 12px 16px !important;
                border: 2px solid var(--border-color) !important;
                border-radius: 8px !important;
                font-size: 14px !important;
                font-family: inherit !important;
                transition: all 0.2s ease !important;
                background: white !important;
            }
            
            .modern-input:focus {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
                outline: none !important;
            }
            
            .Select-control {
                border: 2px solid var(--border-color) !important;
                border-radius: 8px !important;
                padding: 4px !important;
                font-size: 14px !important;
                font-family: inherit !important;
                transition: all 0.2s ease !important;
            }
            
            .Select--is-focused .Select-control {
                border-color: var(--primary-color) !important;
                box-shadow: 0 0 0 3px rgba(0, 102, 204, 0.1) !important;
            }
            
            .modern-button-primary {
                background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
                color: white !important;
                border: none !important;
                border-radius: 8px !important;
                padding: 12px 24px !important;
                font-size: 16px !important;
                font-weight: 600 !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                font-family: inherit !important;
                box-shadow: var(--shadow-md) !important;
            }
            
            .modern-button-primary:hover {
                transform: translateY(-2px) !important;
                box-shadow: var(--shadow-lg) !important;
            }
            
            .modern-button-secondary {
                background: white !important;
                color: var(--dark-color) !important;
                border: 2px solid var(--border-color) !important;
                border-radius: 8px !important;
                padding: 10px 20px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                cursor: pointer !important;
                transition: all 0.2s ease !important;
                font-family: inherit !important;
            }
            
            .modern-button-secondary:hover {
                border-color: var(--primary-color) !important;
                color: var(--primary-color) !important;
                transform: translateY(-1px) !important;
            }
            
            .section-title {
                font-size: 20px !important;
                font-weight: 700 !important;
                color: var(--dark-color) !important;
                margin-bottom: 16px !important;
                display: flex !important;
                align-items: center !important;
            }
            
            .section-title i {
                margin-right: 12px !important;
                color: var(--primary-color) !important;
            }
            
            .info-badge {
                background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%) !important;
                color: var(--primary-color) !important;
                padding: 8px 16px !important;
                border-radius: 20px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                display: inline-flex !important;
                align-items: center !important;
                margin-bottom: 16px !important;
            }
            
            .success-badge {
                background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%) !important;
                color: var(--success-color) !important;
                padding: 8px 16px !important;
                border-radius: 20px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                display: inline-flex !important;
                align-items: center !important;
                margin-bottom: 16px !important;
            }
            
            .warning-badge {
                background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%) !important;
                color: #92400e !important;
                padding: 8px 16px !important;
                border-radius: 20px !important;
                font-size: 14px !important;
                font-weight: 500 !important;
                display: inline-flex !important;
                align-items: center !important;
                margin-bottom: 16px !important;
            }
            
            .data-table-container {
                border-radius: var(--border-radius) !important;
                overflow: hidden !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
            }
            
            .dash-table-container table {
                border-radius: var(--border-radius) !important;
            }
            
            .dash-table-container .dash-spreadsheet-container {
                border-radius: var(--border-radius) !important;
            }
            
            .dash-table-container .dash-spreadsheet-container .dash-spreadsheet-inner table {
                border-collapse: separate !important;
                border-spacing: 0 !important;
            }
            
            .dash-table-container .dash-header {
                background: linear-gradient(135deg, var(--light-color) 0%, #ffffff 100%) !important;
                font-weight: 600 !important;
                color: var(--dark-color) !important;
                border-bottom: 2px solid var(--border-color) !important;
            }
            
            .dash-table-container .dash-cell {
                padding: 12px !important;
                font-size: 14px !important;
                border-right: 1px solid var(--border-color) !important;
            }
            
            .dash-table-container tr:hover {
                background: rgba(0, 102, 204, 0.05) !important;
            }
            
            .slider-container .rc-slider {
                margin: 16px 0 !important;
            }
            
            .slider-container .rc-slider-track {
                background: linear-gradient(90deg, var(--primary-color) 0%, var(--secondary-color) 100%) !important;
                height: 6px !important;
            }
            
            .slider-container .rc-slider-handle {
                border: 3px solid var(--primary-color) !important;
                background: white !important;
                width: 20px !important;
                height: 20px !important;
                margin-top: -7px !important;
                box-shadow: var(--shadow-md) !important;
            }
            
            .radio-group label {
                margin-right: 20px !important;
                font-weight: 500 !important;
                color: var(--dark-color) !important;
            }
            
            .radio-group input[type="radio"] {
                margin-right: 8px !important;
                transform: scale(1.2) !important;
                accent-color: var(--primary-color) !important;
            }
            
            .sidebar {
                background: rgba(255, 255, 255, 0.9) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: var(--border-radius) !important;
                padding: 24px !important;
                margin-right: 24px !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
            }
            
            .content-area {
                background: rgba(255, 255, 255, 0.9) !important;
                backdrop-filter: blur(10px) !important;
                border-radius: var(--border-radius) !important;
                padding: 24px !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
            }
            
            .status-indicator {
                display: inline-flex !important;
                align-items: center !important;
                font-size: 14px !important;
                color: var(--dark-color) !important;
            }
            
            .status-indicator i {
                margin-right: 8px !important;
                color: var(--primary-color) !important;
            }
            
            .language-selector {
                min-width: 160px !important;
            }
            
            .logo-container {
                display: flex !important;
                align-items: center !important;
            }
            
            .logo-container img {
                filter: brightness(0) invert(1) !important;
                height: 60px !important;
                width: auto !important;
            }
            
            .app-title {
                color: white !important;
                margin: 0 0 4px 24px !important;
                font-size: 32px !important;
                font-weight: 700 !important;
            }
            
            .app-subtitle {
                color: rgba(255, 255, 255, 0.9) !important;
                margin: 0 0 0 24px !important;
                font-size: 16px !important;
                font-weight: 400 !important;
            }
            
            /* Animations */
            @keyframes fadeIn {
                from { opacity: 0; transform: translateY(20px); }
                to { opacity: 1; transform: translateY(0); }
            }
            
            .modern-card {
                animation: fadeIn 0.5s ease-out !important;
            }
            
            /* Loading states */
            .loading-spinner {
                display: inline-block !important;
                width: 20px !important;
                height: 20px !important;
                border: 3px solid rgba(0, 102, 204, 0.3) !important;
                border-radius: 50% !important;
                border-top-color: var(--primary-color) !important;
                animation: spin 1s ease-in-out infinite !important;
            }
            
            @keyframes spin {
                to { transform: rotate(360deg); }
            }
            
            /* Responsive design */
            @media (max-width: 768px) {
                .main-container {
                    margin: 10px !important;
                    border-radius: 10px !important;
                }
                
                .modern-card {
                    padding: 16px !important;
                }
                
                .sidebar, .content-area {
                    margin-right: 0 !important;
                    margin-bottom: 20px !important;
                }
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''

# Load initial data
pumps_df = load_pump_data()
curve_df = load_pump_curve_data()

# --- Modern App Layout ---
app.layout = html.Div([
    # Store components for state management
    dcc.Store(id='language-store', data='English'),
    dcc.Store(id='pumps-data-store', data=pumps_df.to_dict('records') if not pumps_df.empty else []),
    dcc.Store(id='curve-data-store', data=curve_df.to_dict('records') if not curve_df.empty else []),
    dcc.Store(id='filtered-pumps-store', data=[]),
    dcc.Store(id='selected-pumps-store', data=[]),
    dcc.Store(id='user-operating-point-store', data={'flow': 0, 'head': 0}),
    
    # Main Container
    html.Div(className='main-container', children=[
        # Modern Header Section
        html.Div(className='modern-card header-card', children=[
            html.Div([
                html.Div(className='logo-container', children=[
                    html.Img(src="https://www.hungpump.com/images/340357"),
                ]),
                
                html.Div([
                    html.H1(id='app-title', className='app-title', children="Hung Pump"),
                    html.P(id='main-title', className='app-subtitle', children="Professional Pump Selection Tool"),
                ], style={'flex': '1'}),
                
                html.Div([
                    dcc.Dropdown(
                        id='language-dropdown',
                        className='language-selector',
                        options=[
                            {'label': '🇺🇸 English', 'value': 'English'},
                            {'label': '🇹🇼 繁體中文', 'value': '繁體中文'}
                        ],
                        value='English',
                        clearable=False,
                    )
                ], style={'display': 'flex', 'alignItems': 'center'}),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between'
            })
        ]),
        
        # Status Bar
        html.Div(className='status-bar', children=[
            html.Div([
                html.Div(className='status-indicator', children=[
                    html.I(className="fas fa-database"),
                    html.Span(id='data-info', children="Loading data...")
                ]),
                html.Div(className='status-indicator', children=[
                    html.I(className="fas fa-chart-line"),
                    html.Span(id='curve-info', children="")
                ], style={'marginLeft': '24px'}),
            ], style={'display': 'flex', 'alignItems': 'center'}),
            
            html.Div([
                html.Button(
                    id='refresh-button',
                    className='modern-button-secondary',
                    children=[html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}), "Refresh Data"]
                ),
                html.Button(
                    id='reset-button',
                    className='modern-button-secondary',
                    children=[html.I(className="fas fa-undo", style={'marginRight': '8px'}), "Reset"],
                    style={'marginLeft': '12px'}
                ),
            ], style={'display': 'flex', 'alignItems': 'center'}),
        ]),
        
        # Main Content Area
        html.Div([
            # Sidebar - Input Controls
            html.Div(className='sidebar', children=[
                # Step 1: Basic Criteria
                html.Div(className='modern-card', children=[
                    html.H3(id='step1-title', className='section-title', children=[
                        html.I(className="fas fa-cog"),
                        "Step 1: Select Basic Criteria"
                    ]),
                    
                    html.Label(id='category-label', children="Category:", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Dropdown(id='category-dropdown', placeholder="Select...", className='modern-input'),
                    
                    html.Label(id='frequency-label', children="Frequency (Hz):", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Dropdown(id='frequency-dropdown', placeholder="Select...", className='modern-input'),
                    
                    html.Label(id='phase-label', children="Phase:", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Dropdown(id='phase-dropdown', placeholder="Select...", className='modern-input'),
                ]),
                
                # Application Input (for Booster category)
                html.Div(id='application-section', className='modern-card', children=[
                    html.H4(id='application-title', className='section-title', children=[
                        html.I(className="fas fa-building"),
                        "Application Input"
                    ]),
                    html.Div(id='floor-faucet-info', className='info-badge', children="💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM"),
                    
                    html.Label(id='floors-label', children="Number of Floors", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='floors-input', type='number', value=0, min=0, className='modern-input'),
                    
                    html.Label(id='faucets-label', children="Number of Faucets", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='faucets-input', type='number', value=0, min=0, className='modern-input'),
                ], style={'display': 'none'}),
                
                # Pond Drainage
                html.Div(className='modern-card', children=[
                    html.H4(id='pond-title', className='section-title', children=[
                        html.I(className="fas fa-water"),
                        "Pond Drainage"
                    ]),
                    
                    html.Label(id='length-label', children="Pond Length (m)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='length-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='width-label', children="Pond Width (m)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='width-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='height-label', children="Pond Height (m)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='height-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='drain-time-label', children="Drain Time (hours)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='drain-time-input', type='number', value=1, min=0.01, step=0.1, className='modern-input'),
                    
                    html.Div(id='pond-volume-display', className='success-badge', style={'margin': '16px 0 8px 0'}),
                    html.Div(id='required-flow-display', className='info-badge', style={'margin': '8px 0 16px 0'}),
                ]),
                
                # Underground & Particle Size
                html.Div(className='modern-card', children=[
                    html.H4(className='section-title', children=[
                        html.I(className="fas fa-arrow-down"),
                        "Additional Parameters"
                    ]),
                    
                    html.Label(id='depth-label', children="Pump Depth Below Ground (m)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='depth-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='particle-label', children="Max Particle Size (mm)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='particle-input', type='number', value=0, min=0, step=1, className='modern-input'),
                ]),
                
                # Manual Input
                html.Div(className='modern-card', children=[
                    html.H4(id='manual-title', className='section-title', children=[
                        html.I(className="fas fa-edit"),
                        "Manual Input"
                    ]),
                    
                    html.Label(id='flow-unit-label', children="Flow Unit", style={'fontWeight': '500', 'marginBottom': '12px', 'display': 'block'}),
                    dcc.RadioItems(
                        id='flow-unit-radio',
                        className='radio-group',
                        options=[
                            {'label': 'L/min', 'value': 'L/min'},
                            {'label': 'L/sec', 'value': 'L/sec'},
                            {'label': 'm³/hr', 'value': 'm³/hr'},
                            {'label': 'm³/min', 'value': 'm³/min'},
                            {'label': 'US gpm', 'value': 'US gpm'}
                        ],
                        value='L/min',
                        inline=True,
                        style={'marginBottom': '16px'}
                    ),
                    
                    html.Label(id='flow-value-label', children="Flow Value", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='flow-value-input', type='number', value=0, min=0, step=10, className='modern-input'),
                    
                    html.Label(id='head-unit-label', children="Head Unit", style={'fontWeight': '500', 'marginBottom': '12px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.RadioItems(
                        id='head-unit-radio',
                        className='radio-group',
                        options=[
                            {'label': 'm', 'value': 'm'},
                            {'label': 'ft', 'value': 'ft'}
                        ],
                        value='m',
                        inline=True,
                        style={'marginBottom': '16px'}
                    ),
                    
                    html.Label(id='head-value-label', children="Total Dynamic Head (TDH)", style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='head-value-input', type='number', value=0, min=0, step=1, className='modern-input'),
                ]),
                
                # Result percentage and search
                html.Div(className='modern-card', children=[
                    html.Label(id='percentage-label', children="Show Top Percentage of Results", style={'fontWeight': '500', 'marginBottom': '16px', 'display': 'block'}),
                    html.Div(className='slider-container', children=[
                        dcc.Slider(
                            id='percentage-slider',
                            min=5, max=100, step=1, value=100,
                            marks={i: f'{i}%' for i in range(10, 101, 20)},
                            tooltip={"placement": "bottom", "always_visible": True}
                        ),
                    ]),
                    
                    html.Button(
                        id='search-button',
                        className='modern-button-primary',
                        children=[
                            html.I(className="fas fa-search", style={'marginRight': '8px'}),
                            "Search Pumps"
                        ],
                        style={'width': '100%', 'marginTop': '24px'}
                    ),
                ]),
            ], style={'width': '35%', 'display': 'inline-block', 'verticalAlign': 'top'}),
            
            # Content Area - Results and charts
            html.Div(className='content-area', children=[
                # Results section
                html.Div(id='results-section', children=[
                    html.H3(id='results-title', className='section-title', children=[
                        html.I(className="fas fa-list"),
                        "Search Results"
                    ]),
                    html.Div(id='results-info', className='info-badge', children="Run a search to see results."),
                    html.Div(id='results-table-container', className='data-table-container'),
                ], style={'marginBottom': '32px'}),
                
                # Pump curves section
                html.Div(id='curves-section', children=[
                    html.H3(id='curves-title', className='section-title', children=[
                        html.I(className="fas fa-chart-line"),
                        "Pump Performance Curves"
                    ]),
                    html.Div(id='curves-info', className='info-badge', children="Select pumps from the table above to view their performance curves."),
                    html.Div(id='curves-container'),
                ]),
            ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'display': 'flex', 'gap': '0', 'padding': '24px'}),
    ]),
    
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
    
    search_children = [
        html.I(className="fas fa-search", style={'marginRight': '8px'}),
        get_text("Search", lang)
    ]
    
    refresh_children = [
        html.I(className="fas fa-sync-alt", style={'marginRight': '8px'}),
        get_text("Refresh Data", lang)
    ]
    
    reset_children = [
        html.I(className="fas fa-undo", style={'marginRight': '8px'}),
        get_text("Reset Inputs", lang)
    ]
    
    results_title_children = [
        html.I(className="fas fa-list"),
        get_text("Matching Pumps", lang)
    ]
    
    curves_title_children = [
        html.I(className="fas fa-chart-line"),
        get_text("Pump Curves", lang)
    ]
    
    return (
        lang,
        get_text("Hung Pump", lang),
        get_text("Pump Selection Tool", lang),
        [html.I(className="fas fa-cog"), get_text("Step 1", lang)],
        get_text("Category", lang),
        get_text("Frequency", lang),
        get_text("Phase", lang),
        [html.I(className="fas fa-building"), get_text("Application Input", lang)],
        get_text("Floor Faucet Info", lang),
        get_text("Number of Floors", lang),
        get_text("Number of Faucets", lang),
        [html.I(className="fas fa-water"), get_text("Pond Drainage", lang)],
        get_text("Pond Length", lang),
        get_text("Pond Width", lang),
        get_text("Pond Height", lang),
        get_text("Drain Time", lang),
        get_text("Pump Depth", lang),
        get_text("Particle Size", lang),
        [html.I(className="fas fa-edit"), get_text("Manual Input", lang)],
        get_text("Flow Unit", lang),
        get_text("Flow Value", lang),
        get_text("Head Unit", lang),
        get_text("TDH", lang),
        get_text("Show Percentage", lang),
        search_children,
        refresh_children,
        reset_children,
        results_title_children,
        curves_title_children
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
    curve_text = f"Curve data: {curve_count} pumps" if curve_count > 0 else ""
    
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
    app_style = {}
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
        return [], {'flow': flow_lpm, 'head': head_m}, get_text("No Matches", lang), html.Div(className='warning-badge', children=get_text("No Matches", lang))
    
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
        style_cell={
            'textAlign': 'left', 
            'padding': '12px',
            'fontFamily': 'Inter, sans-serif',
            'fontSize': '14px'
        },
        style_header={
            'backgroundColor': '#f8f9fa',
            'fontWeight': '600',
            'color': '#2c3e50',
            'border': '1px solid #e2e8f0'
        },
        style_data={
            'backgroundColor': 'white',
            'border': '1px solid #e2e8f0'
        },
        style_data_conditional=[
            {
                'if': {'row_index': 'odd'},
                'backgroundColor': '#f8f9fa'
            }
        ],
        page_size=10,
        sort_action="native",
        filter_action="native",
        style_as_list_view=True,
    )
    
    results_info = html.Div(className='success-badge', children=[
        html.I(className="fas fa-check-circle", style={'marginRight': '8px'}),
        get_text("Found Pumps", lang, count=len(filtered_pumps))
    ])
    
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
        return html.Div(className='info-badge', children=[
            html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
            "Select pumps from the table above to view their performance curves."
        ]), html.Div()
    
    models = selected_models[0]
    user_flow = operating_point.get('flow', 0)
    user_head = operating_point.get('head', 0)
    
    # Filter available models that have curve data
    available_models = [model for model in models if model in curve_df["Model No."].values]
    
    if not available_models:
        return html.Div(className='warning-badge', children=[
            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
            "The selected pumps do not have curve data available."
        ]), html.Div()
    
    charts = []
    
    if len(available_models) == 1:
        # Single pump curve
        fig = create_pump_curve_chart(
            curve_df, available_models[0], user_flow, user_head, flow_unit, head_unit, lang
        )
        if fig:
            charts.append(
                html.Div(className='modern-card', children=[
                    dcc.Graph(figure=fig, style={'height': '500px'})
                ])
            )
    else:
        # Multiple pump comparison
        fig_comp = create_comparison_chart(
            curve_df, available_models, user_flow, user_head, flow_unit, head_unit, lang
        )
        if fig_comp:
            charts.append(
                html.Div(className='modern-card', children=[
                    html.H4(f"Performance Comparison - {len(available_models)} Pumps", 
                           style={'color': '#2c3e50', 'marginBottom': '8px'}),
                    html.P(f"Comparing: {', '.join(available_models)}", 
                          style={'color': '#6b7280', 'fontSize': '14px', 'marginBottom': '16px'}),
                    dcc.Graph(figure=fig_comp, style={'height': '500px'})
                ])
            )
            
            # Individual curves in expandable section
            individual_charts = []
            for model in available_models:
                fig = create_pump_curve_chart(
                    curve_df, model, user_flow, user_head, flow_unit, head_unit, lang
                )
                if fig:
                    individual_charts.append(
                        html.Div(className='modern-card', style={'marginBottom': '20px'}, children=[
                            html.H5(f"Performance Curve - {model}", 
                                   style={'color': '#2c3e50', 'marginBottom': '16px'}),
                            dcc.Graph(figure=fig, style={'height': '400px'})
                        ])
                    )
            
            if individual_charts:
                charts.append(
                    html.Details([
                        html.Summary("View Individual Pump Curves", 
                                   style={'fontWeight': 'bold', 'margin': '20px 0 10px 0', 
                                         'cursor': 'pointer', 'color': '#0066CC'}),
                        html.Div(individual_charts)
                    ])
                )
    
    info_text = html.Div(className='success-badge', children=[
        html.I(className="fas fa-chart-line", style={'marginRight': '8px'}),
        f"Displaying curves for {len(available_models)} pump(s)"
    ])
    
    return info_text, html.Div(charts)

# --- Run the App ---
server = app.server
if __name__ == '__main__':
    app.run_server(debug=True, host='0.0.0.0', port=8050)
