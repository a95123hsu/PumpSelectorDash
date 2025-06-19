import os
import pandas as pd
import plotly.graph_objs as go
from dash import Dash, html, dcc, Input, Output, State, ctx, dash_table
from supabase import create_client
from dotenv import load_dotenv

# --- Environment Setup ---
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- Translation dictionary ---
translations = {
    "English": {
        "app_title": "Pump Selection Tool",
        "select_category": "Category",
        "select_frequency": "Frequency (Hz)",
        "select_phase": "Phase",
        "search": "Search",
        "reset": "Reset",
        "results": "Matching Pumps",
        "select_language": "Language",
        "flow": "Flow (L/min)",
        "head": "Head (m)",
        "compare": "Compare Selected Pumps",
    },
    "繁體中文": {
        "app_title": "水泵選型工具",
        "select_category": "類別",
        "select_frequency": "頻率 (Hz)",
        "select_phase": "相數",
        "search": "搜尋",
        "reset": "重置",
        "results": "符合條件的幫浦",
        "select_language": "語言",
        "flow": "流量 (L/min)",
        "head": "揚程 (m)",
        "compare": "比較所選幫浦",
    }
}

def t(key, lang):
    return translations.get(lang, translations["English"]).get(key, key)

# --- Data Load ---
def load_pump_data():
    try:
        data = supabase.table("pump_selection_data").select("*").execute()
        return pd.DataFrame(data.data)
    except:
        return pd.read_csv("Pump Selection Data.csv")

def load_curve_data():
    try:
        data = supabase.table("pump_curve_data").select("*").execute()
        return pd.DataFrame(data.data)
    except:
        return pd.read_csv("pump_curve_data_rows 1.csv")

pumps_df = load_pump_data()
curves_df = load_curve_data()

# --- App Setup ---
app = Dash(__name__)
app.title = "Pump Selector"

# --- Layout ---
languages = list(translations.keys())

app.layout = html.Div([
    html.H1(id="app-title"),

    html.Div([
        html.Label(id="lang-label"),
        dcc.Dropdown(
            id="lang-dropdown",
            options=[{"label": l, "value": l} for l in languages],
            value="English",
            clearable=False
        )
    ], style={"marginBottom": 20}),

    html.Div([
        html.Label(id="cat-label"),
        dcc.Dropdown(id="category", options=[], value=None),

        html.Label(id="freq-label"),
        dcc.Dropdown(id="frequency", options=[], value=None),

        html.Label(id="phase-label"),
        dcc.Dropdown(id="phase", options=[], value=None),

        html.Br(),
        html.Button(id="search-btn", n_clicks=0),
        html.Button(id="reset-btn", n_clicks=0)
    ]),

    html.Hr(),
    html.H3(id="results-title"),
    dash_table.DataTable(id="results-table", page_size=20, style_table={"overflowX": "auto"}),
])

# --- Callbacks ---
@app.callback(
    Output("app-title", "children"),
    Output("lang-label", "children"),
    Output("cat-label", "children"),
    Output("freq-label", "children"),
    Output("phase-label", "children"),
    Output("search-btn", "children"),
    Output("reset-btn", "children"),
    Output("results-title", "children"),
    Output("category", "options"),
    Output("frequency", "options"),
    Output("phase", "options"),
    Input("lang-dropdown", "value")
)
def translate_ui(lang):
    categories = sorted(pumps_df["Category"].dropna().unique())
    freqs = sorted(pumps_df["Frequency (Hz)"].dropna().unique())
    phases = sorted(pumps_df["Phase"].dropna().unique())
    return (
        t("app_title", lang), t("select_language", lang), t("select_category", lang),
        t("select_frequency", lang), t("select_phase", lang), t("search", lang),
        t("reset", lang), t("results", lang),
        [{"label": t(c, lang), "value": c} for c in categories],
        [{"label": str(f), "value": f} for f in freqs],
        [{"label": str(p), "value": p} for p in phases]
    )

@app.callback(
    Output("results-table", "data"),
    Output("results-table", "columns"),
    Input("search-btn", "n_clicks"),
    Input("reset-btn", "n_clicks"),
    State("category", "value"),
    State("frequency", "value"),
    State("phase", "value")
)
def filter_data(search_clicks, reset_clicks, cat, freq, phase):
    triggered = ctx.triggered_id
    if triggered == "reset-btn":
        return [], []

    df = pumps_df.copy()
    if cat:
        df = df[df["Category"] == cat]
    if freq:
        df = df[df["Frequency (Hz)"] == freq]
    if phase:
        df = df[df["Phase"] == phase]
    cols = [{"name": i, "id": i} for i in df.columns]
    return df.to_dict("records"), cols

app.server = app.server

if __name__ == "__main__":
    app.run_server(debug=True)
