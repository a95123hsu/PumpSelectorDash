import dash
from dash import dcc, html, dash_table, Input, Output, State, callback, ALL, ctx
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from supabase import create_client
import os
from dotenv import load_dotenv
from datetime import datetime
import json
import logging
import traceback

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Environment Setup ---
# Try loading from different locations for local development
try:
    load_dotenv("/etc/secrets/secrets.env")
except:
    pass

try:
    load_dotenv(".env")
except:
    pass

# Get environment variables (Render sets these automatically)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Debug: Print environment variables (without exposing sensitive data)
print(f"Environment: {'Render' if os.getenv('RENDER') else 'Local'}")
print(f"SUPABASE_URL: {'✓ Set' if SUPABASE_URL else '✗ Not set'}")
print(f"SUPABASE_KEY: {'✓ Set' if SUPABASE_KEY else '✗ Not set'}")

# --- Enhanced Translation Dictionary ---
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
        
        # Column Selection - NEW
        "Column Selection": "Column Selection",
        "Select Columns": "Select columns to display in results:",
        "Select All": "Select All",
        "Deselect All": "Deselect All", 
        "Essential Columns": "Essential Columns (always shown)",
        
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
        
        # Estimated application - NEW
        "Estimated Application": "Estimated Application (based on Manual Input)",
        "Estimated Floors": "Estimated Floors",
        "Estimated Faucets": "Estimated Faucets",
        
        # Results
        "Result Display": "Result Display Control",
        "Show Percentage": "Show Top Percentage of Results",
        "Matching Pumps": "✅ Matching Pumps",
        "Found Pumps": "Found {count} matching pumps",
        "View Product": "View Product",
        "Select Pumps": "Select pumps from the table below to view their performance curves",
        "Showing Results": "Showing {count} results out of {total} total",
        
        # Pump Curves - ENHANCED
        "Pump Curves": "Pump Performance Curves",
        "Performance Curve": "Performance Curve - {model}",
        "Flow Rate": "Flow Rate ({unit})",
        "Head": "Head ({unit})",
        "Operating Point": "Your Operating Point",
        "Multiple Curves": "Performance Comparison",
        "Compare Pumps": "Compare Selected Pumps",
        "Select Multiple": "Select multiple pumps to compare:",
        "Selected Pumps": "Selected {count} pump(s) for curve visualization",
        "No Curve Data": "No curve data available for this pump model",
        "Curve Data Loaded": "Curve data loaded: {count} pumps with curve data",
        "Individual Curves": "Individual Pump Curves",
        "View Individual": "View Individual Curves",
        
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
        "Select Warning": "Please select Frequency and Phase to proceed.",
        "Failed Data": "❌ Failed to load data from Supabase: {error}",
        "Failed CSV": "❌ Failed to load CSV file: {error}",
        "Failed Curve Data": "❌ Failed to load curve data: {error}",
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
        
        # Column Selection - NEW
        "Column Selection": "欄位選擇",
        "Select Columns": "選擇要在結果中顯示的欄位:",
        "Select All": "全選",
        "Deselect All": "全部取消",
        "Essential Columns": "必要欄位 (總是顯示)",
        
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
        
        # Estimated application - NEW
        "Estimated Application": "估計應用 (基於手動輸入)",
        "Estimated Floors": "估計樓層",
        "Estimated Faucets": "估計水龍頭",
        
        # Results
        "Result Display": "結果顯示控制",
        "Show Percentage": "顯示前百分比的結果",
        "Matching Pumps": "✅ 符合條件的幫浦",
        "Found Pumps": "找到 {count} 個符合的幫浦",
        "View Product": "查看產品",
        "Select Pumps": "從下表選擇幫浦以查看其性能曲線",
        "Showing Results": "顯示 {count} 筆結果，共 {total} 筆",
        
        # Pump Curves - ENHANCED
        "Pump Curves": "幫浦性能曲線",
        "Performance Curve": "性能曲線 - {model}",
        "Flow Rate": "流量 ({unit})",
        "Head": "揚程 ({unit})",
        "Operating Point": "您的操作點",
        "Multiple Curves": "性能比較",
        "Compare Pumps": "比較選定的幫浦",
        "Select Multiple": "選擇多個幫浦進行比較:",
        "Selected Pumps": "已選擇 {count} 個幫浦進行曲線視覺化",
        "No Curve Data": "此幫浦型號無曲線資料",
        "Curve Data Loaded": "曲線資料已載入: {count} 個幫浦有曲線資料",
        "Individual Curves": "個別幫浦曲線",
        "View Individual": "查看個別曲線",
        
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
        "Select Warning": "請選擇頻率和相數以繼續。",
        "Failed Data": "❌ 從 Supabase 載入資料失敗: {error}",
        "Failed CSV": "❌ 載入 CSV 檔案失敗: {error}",
        "Failed Curve Data": "❌ 載入曲線資料失敗: {error}",
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

# --- Enhanced Data Loading Functions ---
def init_connection():
    """Initialize Supabase connection with fallback support"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("❌ Supabase credentials not found in environment variables")
        return None
    
    try:
        print("🔄 Attempting Supabase connection...")
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test the connection with a simple query
        print("🔍 Testing connection with simple query...")
        test_response = client.table("pump_selection_data").select("*").limit(1).execute()
        print("✅ Supabase connection successful!")
        return client
        
    except Exception as e:
        print(f"❌ Supabase connection failed: {str(e)}")
        return None

def load_pump_data():
    """Load pump data from Supabase with CSV fallback"""
    print("\n📊 Loading pump data...")
    
    try:
        supabase = init_connection()
        if not supabase:
            print("⚠️ No Supabase connection, trying CSV fallback...")
            return load_csv_fallback("pump_selection_data_rows 6.csv")
            
        print("🔄 Fetching pump data from Supabase...")
        all_records = []
        page_size = 1000
        current_page = 0
        
        while True:
            print(f"   📄 Fetching page {current_page + 1}...")
            
            response = supabase.table("pump_selection_data").select("*") \
                .range(current_page * page_size, (current_page + 1) * page_size - 1).execute()
            
            if not response.data:
                print(f"   ✅ No more data on page {current_page + 1}")
                break
                
            all_records.extend(response.data)
            print(f"   ✅ Got {len(response.data)} records from page {current_page + 1}")
            
            current_page += 1
            if len(response.data) < page_size:
                print("   🏁 Reached end of data")
                break
        
        if all_records:
            df = pd.DataFrame(all_records)
            print(f"✅ Successfully loaded {len(df)} pump records from Supabase")
            return df
        else:
            print("⚠️ No pump data found in Supabase, trying CSV fallback...")
            return load_csv_fallback("pump_selection_data_rows 6.csv")
            
    except Exception as e:
        print(f"❌ Error loading pump data from Supabase: {str(e)}")
        print("⚠️ Trying CSV fallback...")
        return load_csv_fallback("pump_selection_data_rows 6.csv")

def load_pump_curve_data():
    """Load pump curve data from Supabase with CSV fallback"""
    print("\n📈 Loading curve data...")
    
    try:
        supabase = init_connection()
        if not supabase:
            print("⚠️ No Supabase connection, trying CSV fallback...")
            return load_csv_fallback("pump_curve_data_rows 3.csv")
            
        print("🔄 Fetching curve data from Supabase...")
        all_records = []
        page_size = 1000
        current_page = 0
        
        while True:
            print(f"   📄 Fetching page {current_page + 1}...")
            
            response = supabase.table("pump_curve_data").select("*") \
                .range(current_page * page_size, (current_page + 1) * page_size - 1).execute()
            
            if not response.data:
                print(f"   ✅ No more data on page {current_page + 1}")
                break
                
            all_records.extend(response.data)
            print(f"   ✅ Got {len(response.data)} records from page {current_page + 1}")
            
            current_page += 1
            if len(response.data) < page_size:
                print("   🏁 Reached end of data")
                break
        
        if all_records:
            df = pd.DataFrame(all_records)
            print(f"✅ Successfully loaded {len(df)} curve records from Supabase")
            return df
        else:
            print("⚠️ No curve data found in Supabase, trying CSV fallback...")
            return load_csv_fallback("pump_curve_data_rows 3.csv")
            
    except Exception as e:
        print(f"❌ Error loading curve data from Supabase: {str(e)}")
        print("⚠️ Trying CSV fallback...")
        return load_csv_fallback("pump_curve_data_rows 3.csv")

def load_csv_fallback(filename):
    """Load data from CSV file as fallback"""
    try:
        df = pd.read_csv(filename)
        print(f"✅ Successfully loaded {len(df)} records from CSV: {filename}")
        return df
    except Exception as e:
        print(f"❌ Error loading CSV {filename}: {str(e)}")
        return pd.DataFrame()

# --- FIXED Chart Creation Functions for Your Data Structure ---
def clean_curve_data(curve_df):
    """Clean and prepare curve data for your specific CSV structure"""
    print("🧹 Cleaning curve data...")
    
    # Create a copy to avoid modifying original
    cleaned_df = curve_df.copy()
    
    # Clean Model No. column
    if 'Model No.' in cleaned_df.columns:
        cleaned_df['Model No.'] = cleaned_df['Model No.'].astype(str).str.strip()
        print(f"✅ Cleaned {len(cleaned_df)} model numbers")
    
    # Get all head columns (both M and Kg/cm² columns)
    head_columns_m = [col for col in cleaned_df.columns if 
                      (col.endswith('M') or col == '10.5') and 
                      col not in ['Max Head(M)']]
    
    pressure_columns = [col for col in cleaned_df.columns if col.endswith('Kg/cm²')]
    
    print(f"📊 Found head columns: {head_columns_m}")
    print(f"📊 Found pressure columns: {pressure_columns}")
    
    # Clean head columns - convert to numeric and handle mixed types
    for col in head_columns_m:
        # Convert to numeric, replacing non-numeric values with NaN
        cleaned_df[col] = pd.to_numeric(cleaned_df[col], errors='coerce')
        # Replace negative values and zeros with NaN (invalid flow rates)
        cleaned_df[col] = cleaned_df[col].where(cleaned_df[col] > 0)
        
        non_null_count = cleaned_df[col].notna().sum()
        print(f"  {col}: {non_null_count} valid values")
    
    return cleaned_df

def get_head_value_from_column(column_name):
    """Extract head value from column name, handling your specific format"""
    try:
        if column_name == '10.5':
            return 10.5
        elif column_name.endswith('M'):
            return float(column_name.replace('M', ''))
        elif column_name.endswith('Kg/cm²'):
            # Convert pressure to head (approximate: 1 Kg/cm² ≈ 10.2 meters)
            pressure = float(column_name.replace('Kg/cm²', ''))
            return pressure * 10.2
        else:
            return None
    except:
        return None

def create_pump_curve_chart_fixed(curve_data, model_no, user_flow=None, user_head=None, 
                                 flow_unit="L/min", head_unit="m", lang="English"):
    """Create pump curve chart adapted for your data structure"""
    print(f"\n🎨 Creating chart for model: {model_no}")
    
    try:
        if not curve_data:
            print("❌ No curve data provided")
            return None
        
        curve_df = pd.DataFrame(curve_data)
        cleaned_df = clean_curve_data(curve_df)
        
        # Find the pump data
        pump_data = cleaned_df[cleaned_df['Model No.'] == model_no]
        if pump_data.empty:
            print(f"❌ No data found for model: {model_no}")
            print(f"Available models sample: {cleaned_df['Model No.'].head().tolist()}")
            return None
        
        pump_row = pump_data.iloc[0]
        print(f"✅ Found pump data for: {model_no}")
        
        # Get head columns with the correct format for your data
        head_columns = [col for col in cleaned_df.columns if 
                       (col.endswith('M') or col == '10.5') and 
                       col not in ['Max Head(M)']]
        
        print(f"📊 Processing head columns: {head_columns}")
        
        flows, heads = [], []
        
        for col in head_columns:
            try:
                head_value = get_head_value_from_column(col)
                if head_value is None:
                    continue
                
                flow_value = pd.to_numeric(pump_row[col], errors='coerce')
                
                print(f"  {col}: Head={head_value}, Flow={flow_value}")
                
                if not pd.isna(flow_value) and flow_value > 0:
                    # Convert from LPM and M to user's units
                    converted_flow = convert_flow_from_lpm(flow_value, flow_unit)
                    converted_head = convert_head_from_m(head_value, head_unit)
                    flows.append(converted_flow)
                    heads.append(converted_head)
                    print(f"    ✅ Added point: Flow={converted_flow:.2f} {flow_unit}, Head={converted_head:.2f} {head_unit}")
                else:
                    print(f"    ❌ Invalid flow value: {flow_value}")
                    
            except Exception as e:
                print(f"    ❌ Error processing {col}: {str(e)}")
                continue
        
        print(f"✅ Valid curve points collected: {len(flows)}")
        
        if not flows or len(flows) < 2:
            print("❌ Insufficient valid data points for curve")
            return None
        
        # Create the chart
        fig = go.Figure()
        
        # Sort the data points by flow (ascending)
        sorted_data = sorted(zip(flows, heads))
        flows, heads = zip(*sorted_data)
        
        print(f"📈 Creating curve with {len(flows)} points")
        
        # Add pump curve
        fig.add_trace(go.Scatter(
            x=flows, 
            y=heads, 
            mode='lines+markers',
            name=f'{model_no} - Performance Curve',
            line=dict(color='#0066CC', width=4), 
            marker=dict(size=8, color='#0066CC'),
            hovertemplate=(
                f'<b>{model_no}</b><br>'
                f'Flow: %{{x:.2f}} {flow_unit}<br>'
                f'Head: %{{y:.2f}} {head_unit}<br>'
                '<extra></extra>'
            )
        ))
        
        # Add operating point if provided
        if user_flow and user_head and user_flow > 0 and user_head > 0:
            display_flow = convert_flow_from_lpm(user_flow, flow_unit)
            display_head = convert_head_from_m(user_head, head_unit)
            
            print(f"🎯 Adding operating point: Flow={display_flow:.2f}, Head={display_head:.2f}")
            
            fig.add_trace(go.Scatter(
                x=[display_flow], 
                y=[display_head], 
                mode='markers',
                name=get_text("Operating Point", lang),
                marker=dict(size=20, color='#FF4444', symbol='star'),
                hovertemplate=(
                    f'<b>Your Operating Point</b><br>'
                    f'Flow: {display_flow:.2f} {flow_unit}<br>'
                    f'Head: {display_head:.2f} {head_unit}<br>'
                    '<extra></extra>'
                )
            ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=f"Performance Curve - {model_no}",
                font=dict(size=20, color='#2c3e50'),
                x=0.5
            ),
            xaxis=dict(
                title=f"Flow Rate ({flow_unit})",
                gridcolor='#e1e5e9',
                linecolor='#bdc3c7',
                title_font=dict(size=16, color='#34495e'),
                tickfont=dict(size=14, color='#34495e'),
                range=[0, max(flows) * 1.1] if flows else [0, 100]
            ),
            yaxis=dict(
                title=f"Head ({head_unit})",
                gridcolor='#e1e5e9',
                linecolor='#bdc3c7',
                title_font=dict(size=16, color='#34495e'),
                tickfont=dict(size=14, color='#34495e'),
                range=[0, max(heads) * 1.1] if heads else [0, 50]
            ),
            plot_bgcolor='#f8f9fa',
            paper_bgcolor='white',
            hovermode='closest', 
            showlegend=True,
            legend=dict(
                bgcolor='rgba(255,255,255,0.9)',
                bordercolor='#bdc3c7',
                borderwidth=1,
                x=0.02,
                y=0.98
            ),
            height=500,
            margin=dict(l=60, r=30, t=60, b=60)
        )
        
        print("✅ Chart created successfully")
        return fig
        
    except Exception as e:
        print(f"❌ Error creating chart for {model_no}: {str(e)}")
        print(f"Full traceback: {traceback.format_exc()}")
        return None

def create_comparison_chart_fixed(curve_data, model_nos, user_flow=None, user_head=None, 
                                 flow_unit="L/min", head_unit="m", lang="English"):
    """Create comparison chart for multiple pumps - fixed for your data"""
    print(f"\n📊 Creating comparison chart for: {model_nos}")
    
    try:
        curve_df = pd.DataFrame(curve_data)
        cleaned_df = clean_curve_data(curve_df)
        
        fig = go.Figure()
        colors = ['#0066CC', '#FF6B35', '#28A745', '#FFC107', '#6F42C1', '#FD7E14', '#E83E8C', '#20C997']
        
        curves_added = 0
        
        for i, model_no in enumerate(model_nos):
            pump_data = cleaned_df[cleaned_df['Model No.'] == model_no]
            if pump_data.empty:
                print(f"❌ No data found for {model_no}")
                continue
            
            pump_row = pump_data.iloc[0]
            
            # Get head columns
            head_columns = [col for col in cleaned_df.columns if 
                           (col.endswith('M') or col == '10.5') and 
                           col not in ['Max Head(M)']]
            
            flows, heads = [], []
            
            for col in head_columns:
                try:
                    head_value = get_head_value_from_column(col)
                    if head_value is None:
                        continue
                    
                    flow_value = pd.to_numeric(pump_row[col], errors='coerce')
                    
                    if not pd.isna(flow_value) and flow_value > 0:
                        converted_flow = convert_flow_from_lpm(flow_value, flow_unit)
                        converted_head = convert_head_from_m(head_value, head_unit)
                        flows.append(converted_flow)
                        heads.append(converted_head)
                        
                except Exception as e:
                    continue
            
            if flows and len(flows) >= 2:
                # Sort the data points
                sorted_data = sorted(zip(flows, heads))
                flows, heads = zip(*sorted_data)
                
                fig.add_trace(go.Scatter(
                    x=flows, 
                    y=heads, 
                    mode='lines+markers',
                    name=model_no,
                    line=dict(color=colors[i % len(colors)], width=3),
                    marker=dict(size=6, color=colors[i % len(colors)]),
                    hovertemplate=(
                        f'<b>{model_no}</b><br>'
                        f'Flow: %{{x:.2f}} {flow_unit}<br>'
                        f'Head: %{{y:.2f}} {head_unit}<br>'
                        '<extra></extra>'
                    )
                ))
                curves_added += 1
                print(f"✅ Added curve for {model_no} with {len(flows)} points")
            else:
                print(f"❌ Insufficient data for {model_no}")
        
        if curves_added == 0:
            print("❌ No valid curves to display")
            return None
        
        # Add operating point if provided
        if user_flow and user_head and user_flow > 0 and user_head > 0:
            display_flow = convert_flow_from_lpm(user_flow, flow_unit)
            display_head = convert_head_from_m(user_head, head_unit)
            
            fig.add_trace(go.Scatter(
                x=[display_flow], 
                y=[display_head], 
                mode='markers',
                name=get_text("Operating Point", lang),
                marker=dict(size=20, color='#FF4444', symbol='star'),
                hovertemplate=(
                    f'<b>Your Operating Point</b><br>'
                    f'Flow: {display_flow:.2f} {flow_unit}<br>'
                    f'Head: {display_head:.2f} {head_unit}<br>'
                    '<extra></extra>'
                )
            ))
        
        # Update layout
        fig.update_layout(
            title=dict(
                text=get_text("Multiple Curves", lang),
                font=dict(size=20, color='#2c3e50'),
                x=0.5
            ),
            xaxis=dict(
                title=f"Flow Rate ({flow_unit})",
                gridcolor='#e1e5e9',
                linecolor='#bdc3c7',
                title_font=dict(size=16, color='#34495e'),
                tickfont=dict(size=14, color='#34495e')
            ),
            yaxis=dict(
                title=f"Head ({head_unit})",
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
        
        print(f"✅ Comparison chart created with {curves_added} curves")
        return fig
        
    except Exception as e:
        print(f"❌ Error creating comparison chart: {str(e)}")
        return None

# --- Initialize Dash App ---
app = dash.Dash(__name__)
app.title = "Hung Pump - Professional Pump Selection Tool"

# Enhanced CSS styling
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
            
            * { box-sizing: border-box; }
            
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
            
            .estimation-card {
                background: linear-gradient(135deg, #f3f4f6 0%, #ffffff 100%) !important;
                border-left: 4px solid var(--primary-color) !important;
                padding: 16px !important;
                border-radius: 8px !important;
                margin: 16px 0 !important;
            }
            
            .estimation-metric {
                display: flex !important;
                justify-content: space-between !important;
                align-items: center !important;
                padding: 8px 0 !important;
                border-bottom: 1px solid #e5e7eb !important;
            }
            
            .estimation-metric:last-child {
                border-bottom: none !important;
            }
            
            .estimation-label {
                font-weight: 500 !important;
                color: var(--dark-color) !important;
            }
            
            .estimation-value {
                font-weight: 700 !important;
                color: var(--primary-color) !important;
                font-size: 18px !important;
            }
            
            .data-table-container {
                border-radius: var(--border-radius) !important;
                overflow: hidden !important;
                box-shadow: var(--shadow-md) !important;
                border: 1px solid var(--border-color) !important;
                margin-bottom: 24px !important;
            }
            
            .dash-table-container table {
                border-radius: var(--border-radius) !important;
            }
            
            .dash-table-container .dash-spreadsheet-container {
                border-radius: var(--border-radius) !important;
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
            
            input[type="checkbox"] {
                transform: scale(1.2) !important;
                accent-color: var(--primary-color) !important;
                margin-right: 8px !important;
            }
            
            .radio-group label {
                margin-right: 20px !important;
                font-weight: 500 !important;
                color: var(--dark-color) !important;
                display: inline-flex !important;
                align-items: center !important;
            }
            
            .radio-group input[type="radio"] {
                margin-right: 8px !important;
                transform: scale(1.2) !important;
                accent-color: var(--primary-color) !important;
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

# --- Enhanced App Layout ---
app.layout = html.Div([
    # Data loading trigger
    dcc.Interval(id="load-trigger", interval=500, max_intervals=1),
    
    # Store components for state management
    dcc.Store(id='language-store', data='English'),
    dcc.Store(id='pumps-data-store', data=[]),
    dcc.Store(id='curve-data-store', data=[]),
    dcc.Store(id='filtered-pumps-store', data=[]),
    dcc.Store(id='selected-pumps-store', data=[]),
    dcc.Store(id='user-operating-point-store', data={'flow': 0, 'head': 0}),
    dcc.Store(id='selected-columns-store', data=[]),
    dcc.Store(id='estimation-store', data={'floors': 0, 'faucets': 0}),
    
    # Main Container
    html.Div(className='main-container', children=[
        # Modern Header Section
        html.Div(className='modern-card header-card', children=[
            html.Div([
                html.Div(className='logo-container', children=[
                    html.Img(src="https://www.hungpump.com/images/340357",
                           style={'height': '60px', 'marginRight': '20px'}),
                ]),
                
                html.Div([
                    html.H1(id='app-title', className='app-title', 
                           children="Hung Pump",
                           style={'fontSize': '36px', 'fontWeight': '700', 'margin': '0',
                                  'background': 'linear-gradient(135deg, #ffffff 0%, #f0f9ff 100%)',
                                  'webkitBackgroundClip': 'text',
                                  'webkitTextFillColor': 'transparent'}),
                    html.P(id='main-title', className='app-subtitle', 
                          children="Professional Pump Selection Tool",
                          style={'fontSize': '18px', 'margin': '4px 0 0 0', 'opacity': '0.9'}),
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
                        style={'minWidth': '160px', 'backgroundColor': 'rgba(255,255,255,0.2)'}
                    )
                ], style={'display': 'flex', 'alignItems': 'center'}),
            ], style={
                'display': 'flex',
                'alignItems': 'center',
                'justifyContent': 'space-between'
            })
        ]),
        
        # Status Bar with Loading
        dcc.Loading(
            id="loading-status",
            type="circle",
            children=html.Div(className='status-bar', children=[
                html.Div([
                    html.Div(id='data-status-output'),
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
            ])
        ),
        
        # Main Content Area
        html.Div(id='main-content-output'),
    ]),
])

# --- Enhanced Data Loading Callbacks ---
@app.callback(
    [Output('pumps-data-store', 'data'),
     Output('curve-data-store', 'data')],
    [Input('load-trigger', 'n_intervals'),
     Input('refresh-button', 'n_clicks')]
)
def fetch_data(n_intervals, refresh_clicks):
    """Load data from Supabase or CSV fallback"""
    print("🔄 Fetching data for app...")
    
    pumps_df = load_pump_data()
    curve_df = load_pump_curve_data()
    
    pumps_data = pumps_df.to_dict('records') if not pumps_df.empty else []
    curve_data = curve_df.to_dict('records') if not curve_df.empty else []
    
    print(f"📊 Stored {len(pumps_data)} pump records in store")
    print(f"📈 Stored {len(curve_data)} curve records in store")
    
    return pumps_data, curve_data

@app.callback(
    Output('data-status-output', 'children'),
    [Input('pumps-data-store', 'data'),
     Input('curve-data-store', 'data'),
     Input('language-store', 'data')]
)
def update_status_bar(pumps_data, curve_data, lang):
    """Update status bar based on loaded data"""
    if not pumps_data:
        return [
            html.Div(className='status-indicator', children=[
                html.I(className="fas fa-spinner fa-spin", style={'marginRight': '8px'}),
                html.Span("📊 Loading pump data...")
            ])
        ]
    
    pumps_count = len(pumps_data)
    curve_count = len(curve_data)
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    return [
        html.Div(className='status-indicator', children=[
            html.I(className="fas fa-database", style={'color': '#28A745', 'marginRight': '8px'}),
            html.Span(get_text("Data loaded", lang, n_records=pumps_count, timestamp=timestamp))
        ]),
        html.Div(className='status-indicator', children=[
            html.I(className="fas fa-chart-line", style={'color': '#0066CC', 'marginRight': '8px'}),
            html.Span(get_text("Curve Data Loaded", lang, count=curve_count))
        ], style={'marginLeft': '24px'}),
    ]

@app.callback(
    Output('main-content-output', 'children'),
    [Input('pumps-data-store', 'data'),
     Input('curve-data-store', 'data')]
)
def render_main_content(pumps_data, curve_data):
    """Render main content only when data is available"""
    if not pumps_data:
        return html.Div(
            className='modern-card',
            style={'textAlign': 'center', 'padding': '60px'},
            children=[
                html.I(className="fas fa-spinner fa-spin", 
                      style={'fontSize': '48px', 'color': '#0066CC', 'marginBottom': '20px'}),
                html.H3("Loading Pump Data...", style={'color': '#2c3e50'}),
                html.P("Please wait while we fetch the latest pump information from our database.", 
                      style={'color': '#6b7280'})
            ]
        )
    
    return html.Div([
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
                    
                    html.Label(id='category-label', children="Category:", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Dropdown(id='category-dropdown', placeholder="Select...", className='modern-input'),
                    
                    html.Label(id='frequency-label', children="Frequency (Hz):", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Dropdown(id='frequency-dropdown', placeholder="Select...", className='modern-input'),
                    
                    html.Label(id='phase-label', children="Phase:", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Dropdown(id='phase-dropdown', placeholder="Select...", className='modern-input'),
                ]),
                
                # Column Selection Section
                html.Div(id='column-selection-section', className='modern-card', children=[
                    html.H4(id='column-selection-title', className='section-title', children=[
                        html.I(className="fas fa-columns"),
                        "Column Selection"
                    ]),
                    html.P(id='column-selection-desc', 
                          children="Select columns to display in results:", 
                          style={'color': '#6b7280', 'marginBottom': '16px'}),
                    
                    html.Div([
                        html.Button(id='select-all-btn', children="Select All", 
                                   className='modern-button-secondary', 
                                   style={'marginRight': '8px', 'fontSize': '12px', 'padding': '6px 12px'}),
                        html.Button(id='deselect-all-btn', children="Deselect All", 
                                   className='modern-button-secondary',
                                   style={'fontSize': '12px', 'padding': '6px 12px'}),
                    ], style={'marginBottom': '12px'}),
                    
                    html.Div(id='column-checkboxes-container', children=[]),
                    
                    html.Small(id='essential-columns-note', 
                              children="Essential columns (Model, Model No.) are always shown",
                              style={'color': '#6b7280', 'fontStyle': 'italic'})
                ]),
                
                # Application Input (for Booster category)
                html.Div(id='application-section', className='modern-card', children=[
                    html.H4(id='application-title', className='section-title', children=[
                        html.I(className="fas fa-building"),
                        "Application Input"
                    ]),
                    html.Div(id='floor-faucet-info', className='info-badge', 
                            children="💡 Each floor = 3.5 m TDH | Each faucet = 15 LPM"),
                    
                    html.Label(id='floors-label', children="Number of Floors", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='floors-input', type='number', value=0, min=0, className='modern-input'),
                    
                    html.Label(id='faucets-label', children="Number of Faucets", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='faucets-input', type='number', value=0, min=0, className='modern-input'),
                ], style={'display': 'none'}),
                
                # Pond Drainage
                html.Div(className='modern-card', children=[
                    html.H4(id='pond-title', className='section-title', children=[
                        html.I(className="fas fa-water"),
                        "Pond Drainage"
                    ]),
                    
                    html.Label(id='length-label', children="Pond Length (m)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='length-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='width-label', children="Pond Width (m)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='width-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='height-label', children="Pond Height (m)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='height-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='drain-time-label', children="Drain Time (hours)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
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
                    
                    html.Label(id='depth-label', children="Pump Depth Below Ground (m)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='depth-input', type='number', value=0, min=0, step=0.1, className='modern-input'),
                    
                    html.Label(id='particle-label', children="Max Particle Size (mm)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block', 'marginTop': '16px'}),
                    dcc.Input(id='particle-input', type='number', value=0, min=0, step=1, className='modern-input'),
                ]),
                
                # Manual Input
                html.Div(className='modern-card', children=[
                    html.H4(id='manual-title', className='section-title', children=[
                        html.I(className="fas fa-edit"),
                        "Manual Input"
                    ]),
                    
                    html.Label(id='flow-unit-label', children="Flow Unit", 
                              style={'fontWeight': '500', 'marginBottom': '12px', 'display': 'block'}),
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
                    
                    html.Label(id='flow-value-label', children="Flow Value", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='flow-value-input', type='number', value=0, min=0, step=10, className='modern-input'),
                    
                    html.Label(id='head-unit-label', children="Head Unit", 
                              style={'fontWeight': '500', 'marginBottom': '12px', 'display': 'block', 'marginTop': '16px'}),
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
                    
                    html.Label(id='head-value-label', children="Total Dynamic Head (TDH)", 
                              style={'fontWeight': '500', 'marginBottom': '8px', 'display': 'block'}),
                    dcc.Input(id='head-value-input', type='number', value=0, min=0, step=1, className='modern-input'),
                ]),
                
                # Estimated Application Section
                html.Div(id='estimation-section', className='modern-card', children=[
                    html.H4(id='estimation-title', className='section-title', children=[
                        html.I(className="fas fa-calculator"),
                        "Estimated Application"
                    ]),
                    html.P(children="Based on Manual Input", style={'color': '#6b7280', 'marginBottom': '16px'}),
                    html.Div(id='estimation-display', className='estimation-card'),
                ]),
                
                # Result percentage and search
                html.Div(className='modern-card', children=[
                    html.Label(id='percentage-label', children="Show Top Percentage of Results", 
                              style={'fontWeight': '500', 'marginBottom': '16px', 'display': 'block'}),
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
                    html.Div(id='results-info', className='info-badge', 
                            children="Run a search to see results."),
                    html.Div(id='results-table-container', className='data-table-container'),
                ], style={'marginBottom': '32px'}),
                
                # Pump curves section
                html.Div(id='curves-section', children=[
                    html.H3(id='curves-title', className='section-title', children=[
                        html.I(className="fas fa-chart-line"),
                        "Pump Performance Curves"
                    ]),
                    html.Div(id='curves-info', className='info-badge', 
                            children="Select pumps from the table above to view their performance curves."),
                    html.Div(id='curves-container'),
                ]),
            ], style={'width': '65%', 'display': 'inline-block', 'verticalAlign': 'top'}),
        ], style={'display': 'flex', 'gap': '0', 'padding': '24px'}),
    ])

# --- Enhanced Callbacks ---

@app.callback(
    [Output('language-store', 'data'),
     Output('app-title', 'children'),
     Output('main-title', 'children'),
     Output('step1-title', 'children'),
     Output('category-label', 'children'),
     Output('frequency-label', 'children'),
     Output('phase-label', 'children'),
     Output('column-selection-title', 'children'),
     Output('column-selection-desc', 'children'),
     Output('select-all-btn', 'children'),
     Output('deselect-all-btn', 'children'),
     Output('essential-columns-note', 'children'),
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
     Output('estimation-title', 'children'),
     Output('percentage-label', 'children'),
     Output('search-button', 'children'),
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
    
    results_title_children = [
        html.I(className="fas fa-list"),
        get_text("Matching Pumps", lang)
    ]
    
    curves_title_children = [
        html.I(className="fas fa-chart-line"),
        get_text("Pump Curves", lang)
    ]
    
    column_selection_title_children = [
        html.I(className="fas fa-columns"),
        get_text("Column Selection", lang)
    ]
    
    estimation_title_children = [
        html.I(className="fas fa-calculator"),
        get_text("Estimated Application", lang)
    ]
    
    return (
        lang,
        get_text("Hung Pump", lang),
        get_text("Pump Selection Tool", lang),
        [html.I(className="fas fa-cog"), get_text("Step 1", lang)],
        get_text("Category", lang),
        get_text("Frequency", lang),
        get_text("Phase", lang),
        column_selection_title_children,
        get_text("Select Columns", lang),
        get_text("Select All", lang),
        get_text("Deselect All", lang),
        get_text("Essential Columns", lang),
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
        estimation_title_children,
        get_text("Show Percentage", lang),
        search_children,
        results_title_children,
        curves_title_children
    )

@app.callback(
    [Output('category-dropdown', 'options'),
     Output('category-dropdown', 'value')],
    [Input('pumps-data-store', 'data'),
     Input('language-store', 'data')]
)
def update_category_options(pumps_data, lang):
    """Update category dropdown options based on language and data"""
    if not pumps_data:
        return [{'label': 'Loading...', 'value': 'loading'}], 'loading'
    
    pumps_df = pd.DataFrame(pumps_data)
    
    # Clean category data
    if "Category" in pumps_df.columns:
        pumps_df["Category"] = pumps_df["Category"].astype(str).str.strip().replace(["nan", "None", "NaN"], "")
        unique_categories = [c for c in pumps_df["Category"].unique() if c and c.strip() and c.lower() not in ["nan", "none", ""]]
        
        options = [{'label': get_text("All Categories", lang), 'value': 'All Categories'}]
        for cat in sorted(unique_categories):
            translated_cat = get_text(cat, lang)
            options.append({'label': translated_cat, 'value': cat})
        
        return options, 'All Categories'
    
    return [{'label': get_text("All Categories", lang), 'value': 'All Categories'}], 'All Categories'

@app.callback(
    [Output('frequency-dropdown', 'options'),
     Output('frequency-dropdown', 'value')],
    [Input('pumps-data-store', 'data'),
     Input('language-store', 'data')]
)
def update_frequency_options(pumps_data, lang):
    """Update frequency dropdown options"""
    if not pumps_data:
        return [{'label': 'Loading...', 'value': 'loading'}], 'loading'
    
    pumps_df = pd.DataFrame(pumps_data)
    
    if "Frequency (Hz)" not in pumps_df.columns:
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
    [Input('pumps-data-store', 'data'),
     Input('language-store', 'data')]
)
def update_phase_options(pumps_data, lang):
    """Update phase dropdown options"""
    if not pumps_data:
        return [{'label': 'Loading...', 'value': 'loading'}], 'loading'
    
    pumps_df = pd.DataFrame(pumps_data)
    
    if "Phase" not in pumps_df.columns:
        return [{'label': get_text("Show All Phase", lang), 'value': 'All'}], 'All'
    
    phase_series = pd.to_numeric(pumps_df["Phase"], errors='coerce')
    phase_options = [p for p in sorted(phase_series.dropna().unique()) if p in [1, 3]]
    
    options = [{'label': get_text("Show All Phase", lang), 'value': 'All'}]
    for phase in phase_options:
        options.append({'label': str(int(phase)), 'value': phase})
    
    return options, 'All'

# Column Selection Callback
@app.callback(
    Output('column-checkboxes-container', 'children'),
    [Input('pumps-data-store', 'data'),
     Input('language-store', 'data')]
)
def update_column_checkboxes(pumps_data, lang):
    """Create column selection checkboxes"""
    if not pumps_data:
        return []
    
    pumps_df = pd.DataFrame(pumps_data)
    essential_columns = ["Model", "Model No."]
    all_columns = [col for col in pumps_df.columns if col not in ["DB ID"]]
    optional_columns = [col for col in all_columns if col not in essential_columns]
    
    checkboxes = []
    for i, col in enumerate(optional_columns):
        checkboxes.append(
            html.Div([
                dcc.Checklist(
                    id={'type': 'column-checkbox', 'index': col},
                    options=[{'label': col, 'value': col}],
                    value=[],
                    style={'margin': '4px 8px'}
                )
            ], style={'display': 'inline-block'})
        )
    
    return checkboxes

# Column Selection Management
@app.callback(
    Output('selected-columns-store', 'data'),
    [Input('select-all-btn', 'n_clicks'),
     Input('deselect-all-btn', 'n_clicks'),
     Input({'type': 'column-checkbox', 'index': ALL}, 'value')],
    [State('pumps-data-store', 'data'),
     State('selected-columns-store', 'data')]
)
def manage_column_selection(select_all_clicks, deselect_all_clicks, checkbox_values, pumps_data, current_selection):
    """Manage column selection state"""
    if not pumps_data:
        return []
    
    pumps_df = pd.DataFrame(pumps_data)
    essential_columns = ["Model", "Model No."]
    all_columns = [col for col in pumps_df.columns if col not in ["DB ID"]]
    optional_columns = [col for col in all_columns if col not in essential_columns]
    
    triggered = ctx.triggered_id if ctx.triggered else None
    
    if triggered == 'select-all-btn':
        return optional_columns
    elif triggered == 'deselect-all-btn':
        return []
    elif triggered and 'type' in triggered and triggered['type'] == 'column-checkbox':
        # Handle individual checkbox changes
        selected = []
        for i, values in enumerate(checkbox_values):
            if values and i < len(optional_columns):
                selected.extend(values)
        return selected
    
    return current_selection or []

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

# Estimation Display Callback
@app.callback(
    [Output('estimation-display', 'children'),
     Output('estimation-store', 'data')],
    [Input('flow-value-input', 'value'),
     Input('head-value-input', 'value'),
     Input('flow-unit-radio', 'value'),
     Input('head-unit-radio', 'value'),
     Input('language-store', 'data')]
)
def update_estimation_display(flow_value, head_value, flow_unit, head_unit, lang):
    """Update estimation display based on manual input"""
    if not flow_value or not head_value:
        return [], {'floors': 0, 'faucets': 0}
    
    # Convert to base units
    flow_lpm = convert_flow_to_lpm(flow_value, flow_unit)
    head_m = convert_head_to_m(head_value, head_unit)
    
    # Calculate estimates
    estimated_floors = round(head_m / 3.5) if head_m > 0 else 0
    estimated_faucets = round(flow_lpm / 15) if flow_lpm > 0 else 0
    
    estimation_content = [
        html.Div(className='estimation-metric', children=[
            html.Span(get_text("Estimated Floors", lang), className='estimation-label'),
            html.Span(str(estimated_floors), className='estimation-value')
        ]),
        html.Div(className='estimation-metric', children=[
            html.Span(get_text("Estimated Faucets", lang), className='estimation-label'),
            html.Span(str(estimated_faucets), className='estimation-value')
        ])
    ]
    
    return estimation_content, {'floors': estimated_floors, 'faucets': estimated_faucets}

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

# Reset Functionality
@app.callback(
    [Output('floors-input', 'value'),
     Output('faucets-input', 'value'),
     Output('length-input', 'value'),
     Output('width-input', 'value'),
     Output('height-input', 'value'),
     Output('drain-time-input', 'value'),
     Output('depth-input', 'value'),
     Output('particle-input', 'value'),
     Output('flow-unit-radio', 'value'),
     Output('head-unit-radio', 'value'),
     Output('percentage-slider', 'value')],
    [Input('reset-button', 'n_clicks')]
)
def reset_inputs(n_clicks):
    """Reset all input values"""
    if n_clicks:
        return 0, 0, 0, 0, 0, 1, 0, 0, 'L/min', 'm', 100
    return dash.no_update

# Search Callback with Column Selection
@app.callback(
    [Output('filtered-pumps-store', 'data'),
     Output('user-operating-point-store', 'data'),
     Output('results-info', 'children'),
     Output('results-table-container', 'children')],
    [Input('search-button', 'n_clicks')],
    [State('pumps-data-store', 'data'),
     State('category-dropdown', 'value'),
     State('frequency-dropdown', 'value'),
     State('phase-dropdown', 'value'),
     State('flow-value-input', 'value'),
     State('head-value-input', 'value'),
     State('particle-input', 'value'),
     State('flow-unit-radio', 'value'),
     State('head-unit-radio', 'value'),
     State('percentage-slider', 'value'),
     State('selected-columns-store', 'data'),
     State('language-store', 'data')]
)
def perform_search(n_clicks, pumps_data, category, frequency, phase, flow_value, head_value, particle_size, 
                  flow_unit, head_unit, percentage, selected_columns, lang):
    """Perform pump search based on criteria with column selection"""
    if not n_clicks or not pumps_data:
        empty_msg = "Click 'Search Pumps' to find matching pumps."
        return [], {'flow': 0, 'head': 0}, empty_msg, html.Div()
    
    # Convert data back to DataFrame
    pumps_df = pd.DataFrame(pumps_data)
    
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
    total_results = len(filtered_pumps)
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
    
    # Prepare table columns with user selection
    essential_columns = ["Model", "Model No."]
    columns_to_show = []
    
    # Add essential columns
    for col in essential_columns:
        if col in filtered_pumps.columns:
            columns_to_show.append(col)
    
    # Add converted flow and head columns
    if f"Q Rated ({flow_unit})" in filtered_pumps.columns:
        columns_to_show.append(f"Q Rated ({flow_unit})")
    if f"Head Rated ({head_unit})" in filtered_pumps.columns:
        columns_to_show.append(f"Head Rated ({head_unit})")
    
    # Add user-selected columns
    for col in (selected_columns or []):
        if col in filtered_pumps.columns and col not in columns_to_show:
            columns_to_show.append(col)
    
    # Add Product Link column at the end if present
    if "Product Link" in filtered_pumps.columns and "Product Link" not in columns_to_show:
        columns_to_show.append("Product Link")
    
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
        get_text("Showing Results", lang, count=len(filtered_pumps), total=total_results)
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

# ENHANCED: Pump Curves with Fixed Chart Functions
@app.callback(
    [Output('curves-info', 'children'),
     Output('curves-container', 'children')],
    [Input('selected-pumps-store', 'data')],
    [State('curve-data-store', 'data'),
     State('user-operating-point-store', 'data'),
     State('flow-unit-radio', 'value'),
     State('head-unit-radio', 'value'),
     State('language-store', 'data')]
)
def update_pump_curves(selected_models, curve_data, operating_point, flow_unit, head_unit, lang):
    """Update pump performance curves based on selected pumps with fixed chart functions"""
    print(f"\n🔄 Updating pump curves for: {selected_models}")
    
    if not selected_models or not selected_models[0] or not curve_data:
        return html.Div(className='info-badge', children=[
            html.I(className="fas fa-info-circle", style={'marginRight': '8px'}),
            get_text("Select Pumps", lang)
        ]), html.Div()
    
    curve_df = pd.DataFrame(curve_data)
    models = selected_models[0]
    user_flow = operating_point.get('flow', 0)
    user_head = operating_point.get('head', 0)
    
    print(f"📊 Available curve data shape: {curve_df.shape}")
    print(f"📋 Looking for models: {models}")
    print(f"🎯 User operating point: Flow={user_flow} LPM, Head={user_head} M")
    
    # Filter available models that have curve data
    if 'Model No.' in curve_df.columns:
        available_models = [model for model in models if model in curve_df["Model No."].values]
        print(f"✅ Found models with curve data: {available_models}")
    else:
        print("❌ No 'Model No.' column found in curve data")
        return html.Div(className='warning-badge', children=[
            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
            "Curve data structure issue"
        ]), html.Div()
    
    if not available_models:
        print("❌ No available models found with curve data")
        return html.Div(className='warning-badge', children=[
            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
            get_text("No Curve Data", lang)
        ]), html.Div()
    
    charts = []
    
    if len(available_models) == 1:
        print(f"📈 Creating single pump curve for: {available_models[0]}")
        # Single pump curve
        fig = create_pump_curve_chart_fixed(
            curve_data, available_models[0], user_flow, user_head, flow_unit, head_unit, lang
        )
        if fig:
            charts.append(
                html.Div(className='modern-card', children=[
                    dcc.Graph(figure=fig, style={'height': '500px'})
                ])
            )
            print("✅ Single curve chart created successfully")
        else:
            print("❌ Failed to create single curve chart")
    else:
        print(f"📊 Creating comparison chart for: {available_models}")
        # Multiple pump comparison
        fig_comp = create_comparison_chart_fixed(
            curve_data, available_models, user_flow, user_head, flow_unit, head_unit, lang
        )
        if fig_comp:
            charts.append(
                html.Div(className='modern-card', children=[
                    html.H4(get_text("Multiple Curves", lang), 
                           style={'color': '#2c3e50', 'marginBottom': '8px'}),
                    html.P(f"Comparing: {', '.join(available_models)}", 
                          style={'color': '#6b7280', 'fontSize': '14px', 'marginBottom': '16px'}),
                    dcc.Graph(figure=fig_comp, style={'height': '500px'})
                ])
            )
            print("✅ Comparison chart created successfully")
            
            # Individual curves in expandable section
            individual_charts = []
            for model in available_models:
                print(f"📈 Creating individual chart for: {model}")
                fig = create_pump_curve_chart_fixed(
                    curve_data, model, user_flow, user_head, flow_unit, head_unit, lang
                )
                if fig:
                    individual_charts.append(
                        html.Div(className='modern-card', style={'marginBottom': '20px'}, children=[
                            html.H5(get_text("Performance Curve", lang, model=model), 
                                   style={'color': '#2c3e50', 'marginBottom': '16px'}),
                            dcc.Graph(figure=fig, style={'height': '400px'})
                        ])
                    )
                    print(f"✅ Individual chart created for {model}")
                else:
                    print(f"❌ Failed to create individual chart for {model}")
            
            if individual_charts:
                charts.append(
                    html.Details([
                        html.Summary(get_text("View Individual", lang), 
                                   style={'fontWeight': 'bold', 'margin': '20px 0 10px 0', 
                                         'cursor': 'pointer', 'color': '#0066CC'}),
                        html.Div(individual_charts)
                    ])
                )
        else:
            print("❌ Failed to create comparison chart")
    
    if not charts:
        print("❌ No charts were created")
        return html.Div(className='warning-badge', children=[
            html.I(className="fas fa-exclamation-triangle", style={'marginRight': '8px'}),
            "Unable to generate pump curves"
        ]), html.Div()
    
    info_text = html.Div(className='success-badge', children=[
        html.I(className="fas fa-chart-line", style={'marginRight': '8px'}),
        get_text("Selected Pumps", lang, count=len(available_models))
    ])
    
    print(f"✅ Successfully created {len(charts)} chart(s)")
    return info_text, html.Div(charts)

# Update all column checkboxes
@app.callback(
    [Output({'type': 'column-checkbox', 'index': ALL}, 'value')],
    [Input('select-all-btn', 'n_clicks'),
     Input('deselect-all-btn', 'n_clicks')],
    [State('pumps-data-store', 'data')]
)
def update_all_checkboxes(select_all_clicks, deselect_all_clicks, pumps_data):
    """Update all column checkboxes when select/deselect all is clicked"""
    if not pumps_data:
        return [[]]
    
    pumps_df = pd.DataFrame(pumps_data)
    essential_columns = ["Model", "Model No."]
    all_columns = [col for col in pumps_df.columns if col not in ["DB ID"]]
    optional_columns = [col for col in all_columns if col not in essential_columns]
    
    triggered = ctx.triggered_id if ctx.triggered else None
    
    if triggered == 'select-all-btn':
        return [[col] for col in optional_columns]
    elif triggered == 'deselect-all-btn':
        return [[] for _ in optional_columns]
    
    return [[] for _ in optional_columns]

# Translation Updates for Radio Items
@app.callback(
    [Output('flow-unit-radio', 'options'),
     Output('head-unit-radio', 'options')],
    [Input('language-store', 'data')]
)
def update_radio_options(lang):
    """Update radio button options with translations"""
    flow_unit_options = [
        {'label': get_text('L/min', lang), 'value': 'L/min'},
        {'label': get_text('L/sec', lang), 'value': 'L/sec'},
        {'label': get_text('m³/hr', lang), 'value': 'm³/hr'},
        {'label': get_text('m³/min', lang), 'value': 'm³/min'},
        {'label': get_text('US gpm', lang), 'value': 'US gpm'}
    ]
    
    head_unit_options = [
        {'label': get_text('m', lang), 'value': 'm'},
        {'label': get_text('ft', lang), 'value': 'ft'}
    ]
    
    return flow_unit_options, head_unit_options

# Enhanced Error Handling for Data Loading
@app.callback(
    Output('main-content-output', 'children', allow_duplicate=True),
    [Input('pumps-data-store', 'data')],
    [State('language-store', 'data')],
    prevent_initial_call=True
)
def handle_data_loading_errors(pumps_data, lang):
    """Handle data loading errors with proper user feedback"""
    if not pumps_data:
        return html.Div(
            className='modern-card',
            style={'textAlign': 'center', 'padding': '60px'},
            children=[
                html.I(className="fas fa-exclamation-triangle", 
                      style={'fontSize': '48px', 'color': '#FFC107', 'marginBottom': '20px'}),
                html.H3(get_text("No Data", lang), style={'color': '#2c3e50'}),
                html.P("Please check your Supabase connection or ensure CSV files are available.", 
                      style={'color': '#6b7280'}),
                html.Button(
                    "Try Again",
                    id='retry-data-load',
                    className='modern-button-primary',
                    style={'marginTop': '20px'}
                )
            ]
        )
    
    return dash.no_update

# --- Run the App ---
server = app.server

if __name__ == '__main__':
    # Get port from environment variable (Render sets this automatically)
    port = int(os.environ.get('PORT', 8050))
    
    # For Render deployment
    if os.getenv('RENDER'):
        print(f"🚀 Starting enhanced app on Render (port {port})...")
        app.run_server(debug=False, host='0.0.0.0', port=port)
    else:
        print(f"🚀 Starting enhanced app locally (port {port})...")
        app.run_server(debug=True, host='0.0.0.0', port=port)
