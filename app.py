from pathlib import Path
import math
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ---------------------------------------------------------
# Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Autonomous Enterprise Telemetry & Incident System",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "dark"

def toggle_theme():
    st.session_state["theme_mode"] = "light" if st.session_state["theme_mode"] == "dark" else "dark"

is_dark = (st.session_state["theme_mode"] == "dark")

# ---------------------------------------------------------
# Theme Color Tokens & Plotly Templates
# ---------------------------------------------------------
if is_dark:
    bg_color = "#0b0f19"
    card_bg = "#111827"
    sidebar_bg = "#0b0f19"
    card_border = "#1f2937"
    sidebar_border = "#1f2937"
    card_hover = "#374151"
    text_primary = "#f9fafb"
    text_secondary = "#9ca3af"
    accent_blue = "#38bdf8"
    accent_emerald = "#34d399"
    accent_amber = "#fbbf24"
    accent_rose = "#f87171"
    plotly_template = "plotly_dark"
    plot_paper_bg = "rgba(17, 24, 39, 0.4)"
    plot_plot_bg = "rgba(17, 24, 39, 0)"
    grid_color = "rgba(255, 255, 255, 0.08)"
else:
    bg_color = "#f8fafc"
    card_bg = "#ffffff"
    sidebar_bg = "#ffffff"
    card_border = "#e2e8f0"
    sidebar_border = "#e2e8f0"
    card_hover = "#cbd5e1"
    text_primary = "#0f172a"
    text_secondary = "#334155"
    accent_blue = "#0284c7"
    accent_emerald = "#059669"
    accent_amber = "#d97706"
    accent_rose = "#dc2626"
    plotly_template = "plotly_white"
    plot_paper_bg = "#ffffff"
    plot_plot_bg = "rgba(255, 255, 255, 0)"
    grid_color = "rgba(15, 23, 42, 0.08)"

# ---------------------------------------------------------
# Plotly Standard Theme Styler
# ---------------------------------------------------------
def apply_plotly_theme(fig, x_title=None, y_title=None, show_legend=True, legend_y=-0.3):
    """
    Applies consistent, high-contrast typography and colors to Plotly figures.
    Guarantees axis titles, ticks, and legends are prominently visible in both Light and Dark themes.
    """
    fig.update_layout(
        template=plotly_template,
        paper_bgcolor=plot_paper_bg,
        plot_bgcolor=plot_plot_bg,
        font=dict(color=text_primary, family="sans-serif", size=12),
    )
    x_dict = dict(
        tickfont=dict(color=text_primary, size=11),
        gridcolor=grid_color,
    )
    if x_title:
        x_dict["title"] = dict(text=x_title, font=dict(color=text_primary, size=12))
    fig.update_xaxes(**x_dict)

    y_dict = dict(
        tickfont=dict(color=text_primary, size=11),
        gridcolor=grid_color,
    )
    if y_title:
        y_dict["title"] = dict(text=y_title, font=dict(color=text_primary, size=12))
    fig.update_yaxes(**y_dict)

    if show_legend:
        fig.update_layout(
            legend=dict(
                font=dict(color=text_primary, size=11),
                orientation="h",
                yanchor="bottom",
                y=legend_y,
                xanchor="center",
                x=0.5,
            )
        )
    return fig

# ---------------------------------------------------------
# Dynamic CSS Injection
# ---------------------------------------------------------
st.markdown(
    f"""
    <style>
        /* Base page background & text */
        .stApp {{
            background-color: {bg_color};
            color: {text_primary};
        }}

        /* Style stAppHeader top bar */
        header[data-testid="stHeader"], .stAppHeader {{
            background-color: {card_bg} !important;
            border-bottom: 1px solid {card_border} !important;
            height: 3.5rem !important;
            z-index: 999990 !important;
            display: flex !important;
            align-items: center !important;
        }}

        /* Position Title inside stAppHeader (centered across top bar) */
        #st-app-header-title {{
            position: fixed !important;
            top: 0 !important;
            left: 0 !important;
            right: 0 !important;
            width: 100% !important;
            height: 3.5rem !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 10px !important;
            z-index: 999992 !important;
            pointer-events: none !important;
            padding: 0 16rem 0 5rem !important;
            box-sizing: border-box !important;
        }}
        #st-app-header-title * {{
            pointer-events: auto !important;
        }}

        /* Position Single Toggle Button inside stAppHeader on the top right adjacent to Deploy */
        .st-key-theme_toggle_btn {{
            position: fixed !important;
            top: 0.65rem !important;
            right: 8.8rem !important;
            height: 2.2rem !important;
            z-index: 999999 !important;
            width: auto !important;
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
        }}

        .st-key-theme_toggle_btn div[data-testid="stButton"],
        .st-key-theme_toggle_btn .stButton {{
            margin: 0 !important;
            padding: 0 !important;
            display: flex !important;
            align-items: center !important;
        }}

        .st-key-theme_toggle_btn button {{
            height: 2.15rem !important;
            min-height: 2.15rem !important;
            padding: 0 0.85rem !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            border-radius: 8px !important;
            border: 1px solid {card_border} !important;
            background: {"rgba(255, 255, 255, 0.08)" if is_dark else "#f1f5f9"} !important;
            color: {text_primary} !important;
            display: inline-flex !important;
            align-items: center !important;
            justify-content: center !important;
            gap: 6px !important;
            line-height: 1 !important;
            cursor: pointer !important;
            transition: all 0.2s ease !important;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.08) !important;
        }}

        .st-key-theme_toggle_btn button:hover {{
            background: {"rgba(56, 189, 248, 0.15)" if is_dark else "rgba(2, 132, 199, 0.12)"} !important;
            border-color: {accent_blue} !important;
            color: {accent_blue} !important;
            transform: translateY(-1px) !important;
        }}

        .st-key-theme_toggle_btn button:active {{
            transform: translateY(0px) !important;
        }}

        .st-key-theme_toggle_btn button p {{
            margin: 0 !important;
            font-size: 0.82rem !important;
            font-weight: 600 !important;
            color: inherit !important;
            line-height: 1 !important;
        }}

        /* Clean top clearance for main content below stAppHeader (3.5rem header + 1.8rem gap) */
        .main .block-container,
        [data-testid="stMainBlockContainer"] {{
            padding-top: 5.3rem !important;
            padding-bottom: 2.5rem !important;
        }}

        /* Sidebar Theme & Styling for Dark and Light Mode */
        section[data-testid="stSidebar"],
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div:first-child,
        [data-testid="stSidebarContent"],
        [data-testid="stSidebarUserContent"] {{
            background-color: {sidebar_bg} !important;
            color: {text_primary} !important;
        }}

        [data-testid="stSidebar"] h1,
        [data-testid="stSidebar"] h2,
        [data-testid="stSidebar"] h3,
        [data-testid="stSidebar"] h4,
        [data-testid="stSidebar"] p,
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] div {{
            color: {text_primary};
        }}

        [data-testid="stSidebar"] label p {{
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stCaptionContainer"] p,
        [data-testid="stSidebar"] .stCaption {{
            color: {text_secondary} !important;
            font-weight: 600 !important;
        }}

        /* Complete Multiselect & Selectbox Theming */
        [data-testid="stSidebar"] [data-testid="stMultiselect"] [data-baseweb="select"],
        [data-testid="stSidebar"] [data-testid="stMultiselect"] [data-baseweb="select"] > div,
        [data-testid="stSidebar"] [data-testid="stMultiselect"] [data-baseweb="select"] div:not([data-baseweb="tag"]):not([data-baseweb="tag"] *),
        [data-testid="stSidebar"] div[data-baseweb="select"],
        [data-testid="stSidebar"] div[data-baseweb="select"] > div,
        [data-testid="stSidebar"] .e1kig3hy0,
        [data-testid="stSidebar"] .e1kig3hy1,
        [data-testid="stSidebar"] .st-emotion-cache-lhglmf,
        [data-testid="stSidebar"] .st-emotion-cache-1cn0whh,
        [data-baseweb="select"],
        [data-baseweb="select"] > div,
        .e1kig3hy0,
        .e1kig3hy1 {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            border-color: {"#cbd5e1" if not is_dark else "#374151"} !important;
            color: {text_primary} !important;
        }}

        /* Multiselect Outer Border & Rounded Corner */
        [data-testid="stSidebar"] div[data-baseweb="select"] > div:first-child,
        [data-testid="stSidebar"] .e1kig3hy1,
        div[data-baseweb="select"] > div:first-child,
        .e1kig3hy1 {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            border: 1px solid {"#cbd5e1" if not is_dark else "#374151"} !important;
            border-radius: 8px !important;
            box-shadow: {"0 1px 2px rgba(0, 0, 0, 0.05)" if not is_dark else "none"} !important;
        }}

        [data-testid="stSidebar"] div[data-baseweb="select"] > div:first-child:focus-within,
        [data-testid="stSidebar"] .e1kig3hy1:focus-within,
        div[data-baseweb="select"] > div:first-child:focus-within {{
            border-color: {accent_blue} !important;
            box-shadow: {"0 0 0 2px rgba(2, 132, 199, 0.2)" if not is_dark else "0 0 0 2px rgba(56, 189, 248, 0.25)"} !important;
        }}

        [data-baseweb="select"] input,
        [data-testid="stSidebar"] [data-baseweb="select"] input {{
            color: {text_primary} !important;
        }}

        /* Multiselect Tag / Pill Styling */
        [data-testid="stSidebar"] [data-baseweb="tag"],
        [data-testid="stSidebar"] span[data-baseweb="tag"],
        [data-testid="stSidebar"] .e1kig3hy5,
        [data-testid="stSidebar"] .st-emotion-cache-1goh6io,
        [data-baseweb="tag"],
        span[data-baseweb="tag"],
        .e1kig3hy5 {{
            background-color: {"#e0f2fe" if not is_dark else "rgba(56, 189, 248, 0.18)"} !important;
            border: 1px solid {"#bae6fd" if not is_dark else "rgba(56, 189, 248, 0.35)"} !important;
            border-radius: 6px !important;
            padding: 2px 6px !important;
            height: auto !important;
        }}

        [data-testid="stSidebar"] [data-baseweb="tag"] *,
        [data-baseweb="tag"] * {{
            background-color: transparent !important;
            color: {"#0369a1" if not is_dark else "#38bdf8"} !important;
            font-weight: 600 !important;
            font-size: 0.8rem !important;
        }}

        /* The 'x' close icon inside the tag */
        [data-testid="stSidebar"] [data-baseweb="tag"] svg,
        [data-testid="stSidebar"] [data-baseweb="tag"] path,
        [data-baseweb="tag"] svg,
        [data-baseweb="tag"] path {{
            fill: {"#0369a1" if not is_dark else "#38bdf8"} !important;
        }}

        /* Multiselect icons (Clear All 'x' and Dropdown arrow) */
        [data-testid="stSidebar"] [data-baseweb="select"] svg,
        [data-testid="stSidebar"] [data-baseweb="select"] path,
        [data-baseweb="select"] svg,
        [data-baseweb="select"] path {{
            fill: {"#64748b" if not is_dark else "#9ca3af"} !important;
        }}

        /* Dropdown popover list items */
        [data-baseweb="popover"],
        [data-baseweb="menu"],
        ul[role="listbox"] {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            border: 1px solid {"#e2e8f0" if not is_dark else "#1f2937"} !important;
            box-shadow: 0 4px 14px rgba(0, 0, 0, 0.1) !important;
        }}
        li[role="option"] {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            color: {text_primary} !important;
        }}
        li[role="option"]:hover,
        li[role="option"][aria-selected="true"] {{
            background-color: {"#f1f5f9" if not is_dark else "#1f2937"} !important;
            color: {accent_blue} !important;
        }}

        [data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stThumbValue"] {{
            color: {text_primary} !important;
            font-weight: 700 !important;
        }}

        [data-testid="stSidebar"] [data-testid="stSlider"] [data-testid="stSliderTickBar"] {{
            color: {text_secondary} !important;
        }}

        [data-testid="stSidebar"] div[data-testid="stButton"] button {{
            background-color: {"#f1f5f9" if not is_dark else "#111827"} !important;
            border: 1px solid {card_border} !important;
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}

        [data-testid="stSidebar"] div[data-testid="stButton"] button:hover {{
            background-color: {"rgba(2, 132, 199, 0.15)" if not is_dark else "rgba(56, 189, 248, 0.15)"} !important;
            border-color: {accent_blue} !important;
            color: {accent_blue} !important;
        }}

        [data-testid="stSidebar"] div[data-testid="stDownloadButton"] button {{
            background-color: {"#f1f5f9" if not is_dark else "#111827"} !important;
            border: 1px solid {card_border} !important;
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}

        [data-testid="stSidebar"] div[data-testid="stDownloadButton"] button:hover {{
            background-color: {"rgba(2, 132, 199, 0.15)" if not is_dark else "rgba(56, 189, 248, 0.15)"} !important;
            border-color: {accent_blue} !important;
            color: {accent_blue} !important;
        }}

        [data-testid="stSidebar"] div[data-testid="stVerticalBlockBorderWrapper"] > div {{
            background-color: {"#f8fafc" if not is_dark else "#111827"} !important;
            border: 1px solid {card_border} !important;
        }}

        [data-testid="stSidebar"] hr {{
            border-color: {sidebar_border} !important;
        }}

        /* =========================================================
           Main Content Form Controls & Inputs (Light & Dark Theming)
           ========================================================= */
        /* Text Inputs */
        [data-testid="stTextInput"] > div:first-child,
        [data-testid="stTextInput"] input,
        .eqy66r52,
        .st-emotion-cache-bm5zf0 {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            color: {text_primary} !important;
            border: 1px solid {"#cbd5e1" if not is_dark else "#374151"} !important;
            border-radius: 8px !important;
        }}
        [data-testid="stTextInput"] input::placeholder {{
            color: {"#94a3b8" if not is_dark else "#6b7280"} !important;
        }}
        [data-testid="stTextInput"] > div:first-child:focus-within {{
            border-color: {accent_blue} !important;
            box-shadow: {"0 0 0 2px rgba(2, 132, 199, 0.2)" if not is_dark else "0 0 0 2px rgba(56, 189, 248, 0.25)"} !important;
        }}

        /* Selectboxes (Dropdowns) */
        [data-testid="stSelectbox"] [data-baseweb="select"],
        [data-testid="stSelectbox"] [data-baseweb="select"] > div,
        [data-testid="stSelectbox"] .react-aria-ComboBox,
        [data-testid="stSelectbox"] .e1fp86qc0,
        [data-testid="stSelectbox"] .st-emotion-cache-eex4dd,
        .e1fp86qc0,
        .st-emotion-cache-eex4dd {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            color: {text_primary} !important;
            border: 1px solid {"#cbd5e1" if not is_dark else "#374151"} !important;
            border-radius: 8px !important;
        }}
        [data-testid="stSelectbox"] input,
        [data-testid="stSelectbox"] .e1fp86qc1,
        [data-testid="stSelectbox"] .st-emotion-cache-167n3l0,
        [data-testid="stSelectbox"] [data-baseweb="select"] div {{
            color: {text_primary} !important;
            -webkit-text-fill-color: {text_primary} !important;
        }}
        [data-testid="stSelectbox"] button,
        [data-testid="stSelectbox"] .e1fp86qc2,
        [data-testid="stSelectbox"] .st-emotion-cache-1mhrr7i {{
            background: transparent !important;
            background-color: transparent !important;
            color: {text_primary} !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stSelectbox"] svg,
        [data-testid="stSelectbox"] path {{
            fill: {"#64748b" if not is_dark else "#9ca3af"} !important;
            stroke: {"#64748b" if not is_dark else "#9ca3af"} !important;
        }}

        /* Number Inputs (Pagination) */
        [data-testid="stNumberInput"] > div:first-child,
        [data-testid="stNumberInput"] input,
        .e1rv0tzo0,
        .st-emotion-cache-lshewc {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            color: {text_primary} !important;
            border: 1px solid {"#cbd5e1" if not is_dark else "#374151"} !important;
            border-radius: 8px !important;
        }}
        [data-testid="stNumberInput"] button {{
            background-color: {"#f1f5f9" if not is_dark else "#1f2937"} !important;
            color: {text_primary} !important;
            border-color: {"#cbd5e1" if not is_dark else "#374151"} !important;
        }}
        [data-testid="stNumberInput"] button svg {{
            fill: {text_primary} !important;
        }}

        /* Download Buttons & Secondary Action Buttons */
        [data-testid="stDownloadButton"] button,
        .stDownloadButton button,
        .main div[data-testid="stButton"] button:not([kind="primary"]) {{
            background-color: {"#ffffff" if not is_dark else "#111827"} !important;
            color: {text_primary} !important;
            border: 1px solid {"#cbd5e1" if not is_dark else "#374151"} !important;
            border-radius: 8px !important;
            font-weight: 600 !important;
            box-shadow: {"0 1px 2px rgba(0, 0, 0, 0.05)" if not is_dark else "none"} !important;
        }}
        [data-testid="stDownloadButton"] button p,
        .stDownloadButton button p,
        .main div[data-testid="stButton"] button:not([kind="primary"]) p {{
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}
        [data-testid="stDownloadButton"] button:hover,
        .stDownloadButton button:hover,
        .main div[data-testid="stButton"] button:not([kind="primary"]):hover {{
            background-color: {"#f1f5f9" if not is_dark else "#1f2937"} !important;
            border-color: {accent_blue} !important;
            color: {accent_blue} !important;
        }}

        /* Sliders */
        [data-testid="stSlider"] [data-baseweb="slider"] div {{
            color: {text_primary} !important;
        }}
        [data-testid="stSlider"] [data-testid="stThumbValue"] {{
            color: {text_primary} !important;
            font-weight: 700 !important;
        }}
        [data-testid="stSlider"] [data-testid="stSliderTickBar"] {{
            color: {text_secondary} !important;
        }}

        /* Glide Data Grid Dataframes (Tables) */
        {"[data-testid='stDataFrame'] canvas { filter: invert(0.92) hue-rotate(180deg) brightness(1.05) contrast(0.95) !important; }" if not is_dark else ""}
        [data-testid="stDataFrame"] {{
            border: 1px solid {card_border} !important;
            border-radius: 8px !important;
            background-color: {card_bg} !important;
        }}
        [data-testid="stElementToolbarButtonContainer"] {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 6px !important;
        }}
        [data-testid="stElementToolbarButtonContainer"] button {{
            color: {text_primary} !important;
        }}
        [data-testid="stElementToolbarButtonContainer"] svg {{
            fill: {text_primary} !important;
        }}

        /* Expanders */
        details[data-testid="stExpander"] {{
            background-color: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 8px !important;
        }}
        details[data-testid="stExpander"] summary {{
            color: {text_primary} !important;
            font-weight: 600 !important;
        }}
        details[data-testid="stExpander"] svg {{
            fill: {text_primary} !important;
        }}

        /* Main Content Text Prominence */
        [data-testid="stMainBlockContainer"],
        [data-testid="stMainBlockContainer"] p,
        [data-testid="stMainBlockContainer"] span,
        [data-testid="stMarkdownContainer"] p,
        [data-testid="stMarkdownContainer"] span,
        [data-testid="stMarkdownContainer"] li {{
            color: {text_primary} !important;
        }}

        /* Force equal height on KPI metric columns */
        [data-testid="column"] {{
            display: flex !important;
            flex-direction: column !important;
        }}
        [data-testid="column"] > div {{
            display: flex !important;
            flex-direction: column !important;
            flex: 1 1 100% !important;
        }}

        /* Metric Card Container */
        .metric-card {{
            background: {card_bg} !important;
            border: 1px solid {card_border} !important;
            border-radius: 12px;
            padding: 18px 20px;
            min-height: 155px;
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            box-shadow: 0 4px 14px 0 rgba(0, 0, 0, 0.08);
            transition: transform 0.2s ease, border-color 0.2s ease, box-shadow 0.2s ease;
            position: relative;
            overflow: hidden;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: {card_hover} !important;
            box-shadow: 0 8px 24px 0 rgba(0, 0, 0, 0.14);
        }}
        .metric-header {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 8px;
            min-height: 42px;
            margin-bottom: 4px;
        }}
        .metric-title {{
            font-size: 0.78rem;
            font-weight: 700 !important;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            color: {text_secondary} !important;
            margin: 0;
            line-height: 1.3;
        }}
        .metric-badge {{
            font-size: 0.72rem;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 20px;
            white-space: nowrap;
            flex-shrink: 0;
        }}
        .metric-value {{
            font-size: 1.95rem;
            font-weight: 800 !important;
            letter-spacing: -0.02em;
            color: {text_primary} !important;
            margin: 2px 0 4px 0;
            line-height: 1.1;
        }}
        .metric-subtext {{
            font-size: 0.78rem;
            color: {text_secondary} !important;
            font-weight: 600 !important;
            margin: 0;
            display: flex;
            align-items: center;
            gap: 6px;
            white-space: nowrap;
        }}

        /* Section Headers */
        .section-header {{
            font-size: 1.15rem;
            font-weight: 800 !important;
            color: {text_primary} !important;
            margin-top: 1.25rem;
            margin-bottom: 0.6rem;
            display: flex;
            align-items: center;
            gap: 8px;
        }}

        /* Tab styling */
        .stTabs [data-baseweb="tab-list"] {{
            background-color: transparent !important;
            border-bottom: 2px solid {card_border} !important;
            gap: 8px !important;
        }}
        .stTabs [data-baseweb="tab"] {{
            border-radius: 8px 8px 0 0 !important;
            padding: 10px 18px !important;
            background-color: {"#f1f5f9" if not is_dark else "rgba(255, 255, 255, 0.04)"} !important;
            border: 1px solid {card_border} !important;
            border-bottom: none !important;
            transition: all 0.2s ease !important;
        }}
        .stTabs [data-baseweb="tab"] p,
        .stTabs [data-baseweb="tab"] span,
        .stTabs [data-baseweb="tab"] div {{
            color: {text_secondary} !important;
            font-weight: 700 !important;
            font-size: 0.95rem !important;
        }}
        .stTabs [data-baseweb="tab"]:hover {{
            background-color: {"#e2e8f0" if not is_dark else "rgba(255, 255, 255, 0.08)"} !important;
        }}
        .stTabs [data-baseweb="tab"]:hover p,
        .stTabs [data-baseweb="tab"]:hover span {{
            color: {text_primary} !important;
        }}
        .stTabs [aria-selected="true"] {{
            background-color: {card_bg} !important;
            border-top: 2px solid {accent_blue} !important;
        }}
        .stTabs [aria-selected="true"] p,
        .stTabs [aria-selected="true"] span,
        .stTabs [aria-selected="true"] div {{
            color: {accent_blue} !important;
            font-weight: 800 !important;
        }}
        .stTabs [data-baseweb="tab-highlight"] {{
            background-color: {accent_blue} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# Placement of Title & Single Toggle Button in stAppHeader
# ---------------------------------------------------------
st.html(
    f"""
    <div id="st-app-header-title">
        <span style="font-size: 1.35rem; display: inline-flex; align-items: center;">🛡️</span>
        <span style="font-size: 1.12rem; font-weight: 800; letter-spacing: -0.015em; color: {text_primary}; white-space: nowrap;">
            Autonomous Enterprise Telemetry &amp; Incident System
        </span>
        <span style="font-size: 0.72rem; font-weight: 700; background: rgba(56, 189, 248, 0.16); color: {accent_blue}; padding: 2px 7px; border-radius: 4px; letter-spacing: 0.04em; margin-left: 4px;">
            AETIS Core
        </span>
    </div>
    """
)

# Single Toggle Button placed in stAppHeader adjacent to Deploy
st.button(
    "☀️ Light Mode" if is_dark else "🌙 Dark Mode",
    key="theme_toggle_btn",
    on_click=toggle_theme,
    help="Toggle between Dark and Light mode",
)

# ---------------------------------------------------------
# Data Ingestion with Caching
# ---------------------------------------------------------
@st.cache_data(show_spinner="Loading telemetry and security audit logs...")
def load_data(file_path: str = "data/api_security_audit_logs.csv") -> pd.DataFrame:
    """
    Reads the security audit logs CSV file using pandas with caching.
    Ensures safe path resolution and optimized datatypes.
    """
    resolved_path = Path(file_path)
    if not resolved_path.exists():
        resolved_path = Path(__file__).resolve().parent / file_path
    if not resolved_path.exists():
        raise FileNotFoundError(f"Audit log dataset not found at '{file_path}' or '{resolved_path}'")

    df = pd.read_csv(
        resolved_path,
        dtype={
            "trace_id": "string",
            "service_name": "category",
            "region": "category",
            "http_method": "category",
            "endpoint": "category",
            "status_code": "int32",
            "latency_ms": "int32",
            "response_bytes": "int32",
            "client_ip": "string",
            "user_agent": "string",
            "payload_snippet": "string",
            "label": "category",
        },
    )
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    return df


try:
    df_raw = load_data()
except Exception as e:
    st.error(f"Failed to load dataset: {e}")
    st.stop()

# ---------------------------------------------------------
# Sidebar Filter Controls
# ---------------------------------------------------------
st.sidebar.markdown(
    f"""
    <div style="margin-bottom: 0.8rem;">
        <h3 style="margin: 0; font-size: 1.05rem; font-weight: 700; color: {text_primary};">
            🔍 Telemetry Filters
        </h3>
        <p style="margin: 0; font-size: 0.78rem; color: {text_secondary};">
            Filter multi-service log ingestion
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Available categories
all_services = sorted(df_raw["service_name"].cat.categories.tolist())
all_regions = sorted(df_raw["region"].cat.categories.tolist())

# 1. Multi-select for service_name
selected_services = st.sidebar.multiselect(
    "Service Name",
    options=all_services,
    default=all_services,
    help="Select one or more microservices to inspect.",
)

# 2. Multi-select for region
selected_regions = st.sidebar.multiselect(
    "Region",
    options=all_regions,
    default=all_regions,
    help="Select one or more deployment cloud regions.",
)

# 3. Slider for latency_ms
min_latency = int(df_raw["latency_ms"].min())
max_latency = int(df_raw["latency_ms"].max())

selected_latency = st.sidebar.slider(
    "Latency Threshold (ms)",
    min_value=min_latency,
    max_value=max_latency,
    value=(min_latency, max_latency),
    step=10,
    help="Filter requests within the designated latency range.",
)

total_raw_rows = len(df_raw)

# ---------------------------------------------------------
# Data Filtering Execution
# ---------------------------------------------------------
if not selected_services or not selected_regions:
    filtered_df = df_raw.iloc[0:0]
else:
    filtered_df = df_raw[
        (df_raw["service_name"].isin(selected_services))
        & (df_raw["region"].isin(selected_regions))
        & (df_raw["latency_ms"] >= selected_latency[0])
        & (df_raw["latency_ms"] <= selected_latency[1])
    ]

# ---------------------------------------------------------
# Sidebar Incident Action & Triage Summary Controls
# ---------------------------------------------------------
st.sidebar.markdown("---")
st.sidebar.markdown(
    f"""
    <div style="margin-bottom: 0.6rem;">
        <h3 style="margin: 0; font-size: 1.02rem; font-weight: 700; color: {text_primary};">
            ⚡ Incident Actions
        </h3>
        <p style="margin: 0; font-size: 0.78rem; color: {text_secondary};">
            Generate on-demand incident triage report
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

if "show_incident_summary" not in st.session_state:
    st.session_state["show_incident_summary"] = False

if st.sidebar.button(
    "Incident Summary",
    help="Generate Incident Triage Summary",
    key="btn_incident_summary",
    use_container_width=True,
):
    st.session_state["show_incident_summary"] = True

if st.session_state.get("show_incident_summary", False):
    incident_mask = (filtered_df["status_code"] >= 400) | (filtered_df["label"] != "BENIGN")
    incident_df = filtered_df[incident_mask]

    with st.sidebar.container(border=True):
        if incident_df.empty:
            st.info("ℹ️ No incident records (HTTP 4xx/5xx or security threats) detected within the current filter scope.")
        else:
            top_ips = incident_df["client_ip"].value_counts().head(3)
            top_fail_endpoints = incident_df["endpoint"].value_counts().head(3)
            avg_inc_latency = float(incident_df["latency_ms"].mean()) if not incident_df.empty else 0.0

            summary_md = [
                "### 📋 Incident Triage Summary",
                "",
                f"- **Average Incident Latency:** `{avg_inc_latency:,.1f} ms`",
                f"- **Total Filtered Incidents:** `{len(incident_df):,}` records",
                "",
                "#### 🚨 Top 3 Offending IPs",
            ]
            for rank, (ip, count) in enumerate(top_ips.items(), start=1):
                summary_md.append(f"{rank}. `{ip}` — **{count:,}** events")

            summary_md.extend([
                "",
                "#### ⚠️ Most Frequent Failure Endpoints",
            ])
            for rank, (ep, count) in enumerate(top_fail_endpoints.items(), start=1):
                summary_md.append(f"{rank}. `{ep}` — **{count:,}** failures")

            st.markdown("\n".join(summary_md))

            incident_csv_bytes = incident_df.to_csv(index=False).encode("utf-8")
            st.download_button(
                label="Download Filtered Incident CSV",
                data=incident_csv_bytes,
                file_name="filtered_incident_logs.csv",
                mime="text/csv",
                key="download_filtered_incident_csv",
                use_container_width=True,
                help="Download filtered incident events as CSV",
            )

        if st.button("✕ Dismiss Summary", key="dismiss_incident_summary", use_container_width=True):
            st.session_state["show_incident_summary"] = False
            st.rerun()

# Baseline Ingest Size always at the bottom of the sidebar
st.sidebar.markdown("---")
st.sidebar.caption(f"**Baseline Ingest Size:** {total_raw_rows:,} records")

# Empty State Notice
if filtered_df.empty:
    st.warning("⚠️ No telemetry records match the selected filter criteria. Please adjust your filters in the sidebar.")
    st.stop()

# ---------------------------------------------------------
# KPI Metrics Computation
# ---------------------------------------------------------
total_requests = len(filtered_df)
avg_latency = float(filtered_df["latency_ms"].mean()) if total_requests > 0 else 0.0

# HTTP 4xx / 5xx error rate
error_mask = filtered_df["status_code"] >= 400
total_errors = int(error_mask.sum())
error_rate = (total_errors / total_requests * 100.0) if total_requests > 0 else 0.0

# Total Anomalous Events detected (label != 'BENIGN')
anomalous_mask = filtered_df["label"] != "BENIGN"
total_anomalies = int(anomalous_mask.sum())
anomaly_rate = (total_anomalies / total_requests * 100.0) if total_requests > 0 else 0.0

# Percent of total global volume
pct_of_global = (total_requests / total_raw_rows * 100.0)

# Latency 95th percentile
p95_latency = float(filtered_df["latency_ms"].quantile(0.95))

# ---------------------------------------------------------
# 4 Summary KPI Metric Cards Across Top (Equal Height Guaranteed)
# ---------------------------------------------------------
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 3px solid {accent_blue};">
            <div class="metric-header">
                <span class="metric-title">Total Requests</span>
                <span class="metric-badge" style="background: rgba(56, 189, 248, 0.18); color: {accent_blue};">
                    {pct_of_global:.1f}% Scope
                </span>
            </div>
            <div class="metric-value">{total_requests:,}</div>
            <p class="metric-subtext">
                <span>📊</span> {total_raw_rows:,} total global ingest
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 3px solid {accent_emerald};">
            <div class="metric-header">
                <span class="metric-title">Average Latency (ms)</span>
                <span class="metric-badge" style="background: rgba(52, 211, 153, 0.18); color: {accent_emerald};">
                    p95: {p95_latency:.0f} ms
                </span>
            </div>
            <div class="metric-value">{avg_latency:.1f} <span style="font-size: 1.1rem; font-weight: 500;">ms</span></div>
            <p class="metric-subtext">
                <span>⚡</span> Min: {int(filtered_df["latency_ms"].min())}ms | Max: {int(filtered_df["latency_ms"].max())}ms
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col3:
    error_badge_bg = "rgba(251, 191, 36, 0.18)" if error_rate < 10 else "rgba(248, 113, 113, 0.2)"
    error_color = accent_amber if error_rate < 10 else accent_rose
    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 3px solid {error_color};">
            <div class="metric-header">
                <span class="metric-title">Error Rate (HTTP 4xx/5xx %)</span>
                <span class="metric-badge" style="background: {error_badge_bg}; color: {error_color};">
                    {total_errors:,} Errors
                </span>
            </div>
            <div class="metric-value">{error_rate:.2f}<span style="font-size: 1.2rem; font-weight: 600;">%</span></div>
            <p class="metric-subtext">
                <span>⚠️</span> HTTP Client & Server Faults
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

with col4:
    st.markdown(
        f"""
        <div class="metric-card" style="border-top: 3px solid {accent_rose};">
            <div class="metric-header">
                <span class="metric-title">Total Anomalous Events detected</span>
                <span class="metric-badge" style="background: rgba(248, 113, 113, 0.2); color: {accent_rose};">
                    {anomaly_rate:.2f}% of traffic
                </span>
            </div>
            <div class="metric-value">{total_anomalies:,}</div>
            <p class="metric-subtext">
                <span>🚨</span> Threat signatures detected
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("<div style='height: 16px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Interactive Telemetry Overview Charts (Directly Below KPI Cards)
# ---------------------------------------------------------
overview_col1, overview_col2 = st.columns(2)

with overview_col1:
    st.markdown(
        f"<div class='section-header'>📈 Hourly Request Volume by Status Category</div>",
        unsafe_allow_html=True,
    )
    # Hourly time-series line chart split by status code category (2xx vs 4xx vs 5xx)
    ts_df = filtered_df[["timestamp", "status_code"]].copy()
    ts_df["status_category"] = pd.cut(
        ts_df["status_code"],
        bins=[199, 299, 499, 599],
        labels=["2xx Success", "4xx Client Error", "5xx Server Error"],
    )
    hourly_vol = (
        ts_df.set_index("timestamp")
        .groupby([pd.Grouper(freq="1h"), "status_category"], observed=True)
        .size()
        .unstack(fill_value=0)
        .reset_index()
    )

    fig_hourly = go.Figure()

    if "2xx Success" in hourly_vol.columns:
        fig_hourly.add_trace(
            go.Scatter(
                x=hourly_vol["timestamp"],
                y=hourly_vol["2xx Success"],
                mode="lines",
                name="2xx Success",
                line=dict(color=accent_emerald, width=2.5),
                fill="tozeroy",
                fillcolor="rgba(52, 211, 153, 0.08)" if is_dark else "rgba(5, 150, 105, 0.08)",
                hovertemplate="<b>2xx Success</b>: %{y:,} reqs<extra></extra>",
            )
        )

    if "4xx Client Error" in hourly_vol.columns:
        fig_hourly.add_trace(
            go.Scatter(
                x=hourly_vol["timestamp"],
                y=hourly_vol["4xx Client Error"],
                mode="lines",
                name="4xx Client Error",
                line=dict(color=accent_amber, width=2.2),
                hovertemplate="<b>4xx Client Error</b>: %{y:,} reqs<extra></extra>",
            )
        )

    if "5xx Server Error" in hourly_vol.columns:
        fig_hourly.add_trace(
            go.Scatter(
                x=hourly_vol["timestamp"],
                y=hourly_vol["5xx Server Error"],
                mode="lines",
                name="5xx Server Error",
                line=dict(color=accent_rose, width=2.2, dash="dash"),
                hovertemplate="<b>5xx Server Error</b>: %{y:,} reqs<extra></extra>",
            )
        )

    fig_hourly.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
        hovermode="x unified",
    )
    apply_plotly_theme(fig_hourly, x_title="Timestamp (Hourly)", y_title="Request Volume", legend_y=-0.32)
    st.plotly_chart(fig_hourly, width="stretch")

with overview_col2:
    st.markdown(
        f"<div class='section-header'>⚡ Latency vs. Timestamp (SLA Anomaly Detection)</div>",
        unsafe_allow_html=True,
    )
    # Scatter plot: timestamp vs latency_ms, color-coded by status_code, highlighting requests > 2000ms in red
    high_latency = filtered_df[filtered_df["latency_ms"] > 2000]
    normal_latency = filtered_df[filtered_df["latency_ms"] <= 2000]

    # Sample normal points for smooth interactive rendering if dataset is large, while keeping 100% of > 2000ms outliers
    max_normal_sample = 5000
    if len(normal_latency) > max_normal_sample:
        normal_sample = normal_latency.sample(n=max_normal_sample, random_state=42)
    else:
        normal_sample = normal_latency

    status_palette = {
        200: "#10b981",
        201: "#34d399",
        204: "#6ee7b7",
        400: "#f59e0b",
        401: "#f97316",
        403: "#ea580c",
        404: "#d97706",
        408: "#b45309",
        500: "#a855f7",
        503: "#8b5cf6",
        504: "#6366f1",
    }

    fig_scatter = go.Figure()

    # Normal latency requests color-coded by status code
    sorted_codes = sorted(normal_sample["status_code"].unique())
    for code in sorted_codes:
        subset = normal_sample[normal_sample["status_code"] == code]
        fig_scatter.add_trace(
            go.Scattergl(
                x=subset["timestamp"],
                y=subset["latency_ms"],
                mode="markers",
                name=f"HTTP {code}",
                marker=dict(
                    size=4.5,
                    opacity=0.6,
                    color=status_palette.get(code, accent_blue),
                ),
                customdata=subset[["service_name", "endpoint", "trace_id"]].values,
                hovertemplate=(
                    f"<b>HTTP {code}</b><br>"
                    "Time: %{x|%Y-%m-%d %H:%M}<br>"
                    "Latency: %{y:,} ms<br>"
                    "Service: %{customdata[0]}<br>"
                    "Endpoint: %{customdata[1]}<extra></extra>"
                ),
            )
        )

    # Highlighting requests that exceeded 2000ms in red
    if not high_latency.empty:
        fig_scatter.add_trace(
            go.Scattergl(
                x=high_latency["timestamp"],
                y=high_latency["latency_ms"],
                mode="markers",
                name=f"🚨 > 2000ms ({len(high_latency):,} Breaches)",
                marker=dict(
                    size=7.5,
                    color="#ef4444",
                    symbol="diamond",
                    opacity=0.9,
                    line=dict(width=1, color="#fee2e2" if is_dark else "#7f1d1d"),
                ),
                customdata=high_latency[["status_code", "service_name", "endpoint"]].values,
                hovertemplate=(
                    "<b style='color:#ef4444;'>⚠️ SLA BREACH (> 2000ms)</b><br>"
                    "HTTP Status: %{customdata[0]}<br>"
                    "Latency: %{y:,} ms<br>"
                    "Time: %{x|%Y-%m-%d %H:%M}<br>"
                    "Service: %{customdata[1]}<br>"
                    "Endpoint: %{customdata[2]}<extra></extra>"
                ),
            )
        )

    # 2000ms SLA Threshold reference line
    fig_scatter.add_hline(
        y=2000,
        line_dash="dash",
        line_color="#ef4444",
        line_width=1.8,
        annotation_text="2,000ms SLA Threshold",
        annotation_position="top left",
        annotation_font_color="#ef4444",
        annotation_font_size=11,
    )

    fig_scatter.update_layout(
        margin=dict(l=10, r=10, t=25, b=10),
    )
    apply_plotly_theme(fig_scatter, x_title="Timestamp", y_title="Latency (ms)", legend_y=-0.32)
    st.plotly_chart(fig_scatter, width="stretch")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# Visual Analytics Tabs
# ---------------------------------------------------------
tab_threats, tab_perf, tab_incidents, tab_explorer = st.tabs(
    [
        "🚨 Threat & Anomaly Intelligence",
        "📈 Telemetry & Service Health",
        "🛡️ Incident & Suspicious Traffic Explorer",
        "🔍 Full Audit Log Explorer",
    ]
)

# ---------------------------------------------------------
# Tab 1: Threat & Anomaly Intelligence
# ---------------------------------------------------------
with tab_threats:
    anomalies_df = filtered_df[anomalous_mask]

    if anomalies_df.empty:
        st.info("No security anomalies detected under the current filter selection.")
    else:
        row1_col1, row1_col2 = st.columns([1, 1])

        with row1_col1:
            st.markdown(f"<div class='section-header'>🛡️ Anomaly Distribution by Attack Category</div>", unsafe_allow_html=True)
            attack_counts = (
                anomalies_df["label"].value_counts().reset_index()
            )
            attack_counts.columns = ["Attack Vector", "Count"]

            fig_attack = px.pie(
                attack_counts,
                names="Attack Vector",
                values="Count",
                hole=0.55,
                color="Attack Vector",
                color_discrete_sequence=px.colors.qualitative.Bold,
                template=plotly_template,
            )
            fig_attack.update_traces(
                textposition="inside",
                textinfo="percent+label",
                marker=dict(line=dict(color=card_bg, width=2)),
            )
            fig_attack.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
            )
            apply_plotly_theme(fig_attack, show_legend=True, legend_y=-0.25)
            st.plotly_chart(fig_attack, width="stretch")

        with row1_col2:
            st.markdown(f"<div class='section-header'>🎯 Threat Incidents by Target Service</div>", unsafe_allow_html=True)
            service_threats = (
                anomalies_df.groupby(["service_name", "label"], observed=True)
                .size()
                .reset_index(name="Incident Count")
            )
            fig_svc_threats = px.bar(
                service_threats,
                x="service_name",
                y="Incident Count",
                color="label",
                barmode="stack",
                color_discrete_sequence=px.colors.qualitative.Safe,
                template=plotly_template,
                labels={"service_name": "Target Microservice", "label": "Attack Vector"},
            )
            fig_svc_threats.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
            )
            apply_plotly_theme(fig_svc_threats, x_title="Target Microservice", y_title="Incident Count", legend_y=-0.35)
            fig_svc_threats.update_xaxes(showgrid=False)
            st.plotly_chart(fig_svc_threats, width="stretch")

        # Region & Method breakdown
        st.markdown(f"<div class='section-header'>🌐 Threat Surface Analysis by Cloud Region</div>", unsafe_allow_html=True)
        col_reg, col_ip = st.columns([1, 1])

        with col_reg:
            reg_threats = (
                anomalies_df.groupby(["region", "label"], observed=True)
                .size()
                .reset_index(name="Incidents")
            )
            fig_reg = px.bar(
                reg_threats,
                x="region",
                y="Incidents",
                color="label",
                barmode="group",
                color_discrete_sequence=px.colors.qualitative.Prism,
                template=plotly_template,
                labels={"region": "Cloud Region", "label": "Attack Vector"},
            )
            fig_reg.update_layout(
                margin=dict(l=10, r=10, t=20, b=10),
            )
            apply_plotly_theme(fig_reg, x_title="Cloud Region", y_title="Incidents", legend_y=-0.35)
            fig_reg.update_xaxes(showgrid=False)
            st.plotly_chart(fig_reg, width="stretch")

        with col_ip:
            st.markdown(f"<p style='color: {text_secondary}; font-weight: 600; margin-bottom: 8px;'>Top Flagged Origin IPs</p>", unsafe_allow_html=True)
            top_ips = (
                anomalies_df.groupby(["client_ip", "label"], observed=True)
                .size()
                .reset_index(name="Events")
                .sort_values("Events", ascending=False)
                .head(8)
            )
            st.dataframe(
                top_ips,
                width="stretch",
                hide_index=True,
                column_config={
                    "client_ip": st.column_config.TextColumn("Origin IP Address"),
                    "label": st.column_config.TextColumn("Predominant Attack"),
                    "Events": st.column_config.ProgressColumn(
                        "Incident Count",
                        format="%d",
                        min_value=0,
                        max_value=int(top_ips["Events"].max()) if not top_ips.empty else 1,
                    ),
                },
            )

# ---------------------------------------------------------
# Tab 2: Telemetry & Service Health
# ---------------------------------------------------------
with tab_perf:
    perf_col1, perf_col2 = st.columns([1, 1])

    with perf_col1:
        st.markdown(f"<div class='section-header'>⚡ Latency Profile by Microservice</div>", unsafe_allow_html=True)
        svc_latency = (
            filtered_df.groupby("service_name", observed=True)["latency_ms"]
            .agg(avg="mean", p95=lambda x: x.quantile(0.95), max="max")
            .reset_index()
        )
        fig_lat = px.bar(
            svc_latency,
            x="service_name",
            y=["avg", "p95"],
            barmode="group",
            template=plotly_template,
            color_discrete_map={"avg": accent_blue, "p95": accent_amber},
            labels={"value": "Latency (ms)", "service_name": "Microservice", "variable": "Metric"},
        )
        fig_lat.update_layout(
            margin=dict(l=10, r=10, t=20, b=10),
        )
        apply_plotly_theme(fig_lat, x_title="Microservice", y_title="Latency (ms)", legend_y=-0.3)
        fig_lat.update_xaxes(showgrid=False)
        st.plotly_chart(fig_lat, width="stretch")

    with perf_col2:
        st.markdown(f"<div class='section-header'>🚦 HTTP Status Code Distribution</div>", unsafe_allow_html=True)
        status_dist = (
            filtered_df["status_code"].value_counts().reset_index()
        )
        status_dist.columns = ["Status Code", "Requests"]
        status_dist["Status Code"] = status_dist["Status Code"].astype(str)

        def status_color(code):
            if code.startswith("2"):
                return accent_emerald
            elif code.startswith("4"):
                return accent_amber
            elif code.startswith("5"):
                return accent_rose
            return accent_blue

        colors = [status_color(c) for c in status_dist["Status Code"]]

        fig_status = go.Figure(
            go.Bar(
                x=status_dist["Status Code"],
                y=status_dist["Requests"],
                marker_color=colors,
                text=status_dist["Requests"],
                textposition="auto",
            )
        )
        fig_status.update_layout(
            margin=dict(l=10, r=10, t=20, b=10),
        )
        apply_plotly_theme(fig_status, x_title="HTTP Status Code", y_title="Request Count", show_legend=False)
        fig_status.update_xaxes(showgrid=False)
        st.plotly_chart(fig_status, width="stretch")

    # Hourly Traffic & Anomaly timeline
    st.markdown(f"<div class='section-header'>⏱️ Telemetry Volume & Error Trend Over Time</div>", unsafe_allow_html=True)
    timeline_df = filtered_df.set_index("timestamp").sort_index()
    resampled = timeline_df.resample("3h").agg(
        total_volume=("trace_id", "count"),
        errors=("status_code", lambda s: (s >= 400).sum()),
        anomalies=("label", lambda l: (l != "BENIGN").sum()),
    ).reset_index()

    fig_time = go.Figure()
    fig_time.add_trace(
        go.Scatter(
            x=resampled["timestamp"],
            y=resampled["total_volume"],
            mode="lines",
            name="Total Requests",
            line=dict(color=accent_blue, width=2.5),
            fill="tozeroy",
            fillcolor="rgba(56, 189, 248, 0.08)",
        )
    )
    fig_time.add_trace(
        go.Scatter(
            x=resampled["timestamp"],
            y=resampled["errors"],
            mode="lines",
            name="HTTP Errors (4xx/5xx)",
            line=dict(color=accent_amber, width=2, dash="dot"),
        )
    )
    fig_time.add_trace(
        go.Scatter(
            x=resampled["timestamp"],
            y=resampled["anomalies"],
            mode="lines",
            name="Security Incidents",
            line=dict(color=accent_rose, width=2),
        )
    )
    fig_time.update_layout(
        margin=dict(l=10, r=10, t=20, b=10),
    )
    apply_plotly_theme(fig_time, x_title="Time (UTC)", y_title="Volume per 3-hour Bucket", legend_y=-0.25)
    st.plotly_chart(fig_time, width="stretch")

# ---------------------------------------------------------
# Tab 3: Incident & Suspicious Traffic Explorer
# ---------------------------------------------------------
with tab_incidents:
    st.markdown(
        f"<div class='section-header'>🛡️ Incident & Suspicious Traffic Explorer</div>",
        unsafe_allow_html=True,
    )

    # Filter rows where status_code >= 400 or label != 'BENIGN'
    incident_mask = (filtered_df["status_code"] >= 400) | (filtered_df["label"] != "BENIGN")
    incidents_base = filtered_df[incident_mask].copy()

    if incidents_base.empty:
        st.info("✅ No incidents or suspicious traffic detected under current filter selection.")
    else:
        # Quick summary metrics for incident subset
        inc_total = len(incidents_base)
        inc_threats = int((incidents_base["label"] != "BENIGN").sum())
        inc_errors = int((incidents_base["status_code"] >= 400).sum())
        inc_high_lat = int((incidents_base["latency_ms"] > 2000).sum())

        st.markdown(
            f"""
            <div style="display: flex; gap: 12px; margin-bottom: 1rem; flex-wrap: wrap;">
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 8px 14px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">⚠️</span>
                    <div>
                        <div style="font-size: 0.72rem; color: {text_secondary}; text-transform: uppercase; font-weight: 600;">Suspicious Events</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: {accent_amber};">{inc_total:,}</div>
                    </div>
                </div>
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 8px 14px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">🚨</span>
                    <div>
                        <div style="font-size: 0.72rem; color: {text_secondary}; text-transform: uppercase; font-weight: 600;">Security Attacks</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: {accent_rose};">{inc_threats:,}</div>
                    </div>
                </div>
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 8px 14px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">💥</span>
                    <div>
                        <div style="font-size: 0.72rem; color: {text_secondary}; text-transform: uppercase; font-weight: 600;">HTTP Faults (4xx/5xx)</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: {accent_blue};">{inc_errors:,}</div>
                    </div>
                </div>
                <div style="background: {card_bg}; border: 1px solid {card_border}; border-radius: 8px; padding: 8px 14px; display: flex; align-items: center; gap: 8px;">
                    <span style="font-size: 1.1rem;">⚡</span>
                    <div>
                        <div style="font-size: 0.72rem; color: {text_secondary}; text-transform: uppercase; font-weight: 600;">Critical Latency (>2s)</div>
                        <div style="font-size: 1.1rem; font-weight: 700; color: {accent_rose};">{inc_high_lat:,}</div>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        # Search & Filter Controls
        s_col1, s_col2, s_col3 = st.columns([2, 1, 1])
        with s_col1:
            inc_search = st.text_input(
                "🔎 Search Suspicious Records",
                placeholder="Search trace_id, client_ip, user_agent, endpoint, payload...",
                key="inc_search_input",
            )
        with s_col2:
            all_threat_types = ["ALL"] + sorted([x for x in incidents_base["label"].unique().tolist() if x != "BENIGN"]) + (["BENIGN (HTTP Faults Only)"] if (incidents_base["label"] == "BENIGN").any() else [])
            selected_threat_filter = st.selectbox(
                "Threat Classification",
                options=all_threat_types,
                key="inc_threat_filter",
            )
        with s_col3:
            all_status_filters = ["ALL", "4xx Client Errors", "5xx Server Errors"] + [str(c) for c in sorted(incidents_base["status_code"].unique())]
            selected_status_filter = st.selectbox(
                "HTTP Status Filter",
                options=all_status_filters,
                key="inc_status_filter",
            )

        # Apply search and filters
        filtered_incidents = incidents_base

        if selected_threat_filter != "ALL":
            if selected_threat_filter == "BENIGN (HTTP Faults Only)":
                filtered_incidents = filtered_incidents[filtered_incidents["label"] == "BENIGN"]
            else:
                filtered_incidents = filtered_incidents[filtered_incidents["label"] == selected_threat_filter]

        if selected_status_filter != "ALL":
            if selected_status_filter == "4xx Client Errors":
                filtered_incidents = filtered_incidents[(filtered_incidents["status_code"] >= 400) & (filtered_incidents["status_code"] < 500)]
            elif selected_status_filter == "5xx Server Errors":
                filtered_incidents = filtered_incidents[filtered_incidents["status_code"] >= 500]
            else:
                filtered_incidents = filtered_incidents[filtered_incidents["status_code"] == int(selected_status_filter)]

        if inc_search:
            q = inc_search.strip().lower()
            inc_match = (
                filtered_incidents["trace_id"].astype(str).str.lower().str.contains(q, na=False)
                | filtered_incidents["client_ip"].astype(str).str.lower().str.contains(q, na=False)
                | filtered_incidents["user_agent"].astype(str).str.lower().str.contains(q, na=False)
                | filtered_incidents["endpoint"].astype(str).str.lower().str.contains(q, na=False)
                | filtered_incidents["payload_snippet"].astype(str).str.lower().str.contains(q, na=False)
                | filtered_incidents["service_name"].astype(str).str.lower().str.contains(q, na=False)
            )
            filtered_incidents = filtered_incidents[inc_match]

        # Pagination Controls
        total_incident_rows = len(filtered_incidents)
        p_col1, p_col2, p_col3 = st.columns([1, 1, 2])
        with p_col1:
            page_size = st.selectbox(
                "Rows per page",
                options=[10, 25, 50, 100],
                index=1,
                key="inc_page_size",
            )
        total_pages = max(1, math.ceil(total_incident_rows / page_size)) if total_incident_rows > 0 else 1
        with p_col2:
            current_page = st.number_input(
                f"Page (of {total_pages})",
                min_value=1,
                max_value=total_pages,
                value=1,
                step=1,
                key="inc_page_num",
            )
        with p_col3:
            start_row = (current_page - 1) * page_size
            end_row = min(start_row + page_size, total_incident_rows)
            st.markdown(
                f"<div style='margin-top: 1.8rem; font-size: 0.85rem; color: {text_secondary};'>"
                f"Displaying records <b>{start_row + 1 if total_incident_rows > 0 else 0} - {end_row}</b> of <b>{total_incident_rows:,}</b>"
                f"</div>",
                unsafe_allow_html=True,
            )

        # Slice current page
        page_incident_df = filtered_incidents.iloc[start_row:end_row].reset_index(drop=True)

        # Table columns to display
        inc_display_cols = [
            "status_code",
            "label",
            "service_name",
            "http_method",
            "endpoint",
            "latency_ms",
            "client_ip",
            "timestamp",
            "trace_id",
        ]

        st.caption("💡 **Click or select any row** in the table below to inspect its detailed request forensic card.")

        # Interactive Data Table with Selection
        selected_event = st.dataframe(
            page_incident_df[inc_display_cols],
            on_select="rerun",
            selection_mode="single-row",
            key="incident_table_grid",
            width="stretch",
            hide_index=True,
            column_config={
                "status_code": st.column_config.NumberColumn("HTTP Status", format="%d", width="small"),
                "label": st.column_config.TextColumn("Classification", width="medium"),
                "service_name": st.column_config.TextColumn("Service", width="small"),
                "http_method": st.column_config.TextColumn("Method", width="small"),
                "endpoint": st.column_config.TextColumn("Endpoint", width="medium"),
                "latency_ms": st.column_config.NumberColumn("Latency", format="%d ms", width="small"),
                "client_ip": st.column_config.TextColumn("Client IP", width="medium"),
                "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
                "trace_id": st.column_config.TextColumn("Trace ID", width="small"),
            },
        )

        # Request Inspector Expander Card
        selected_indices = selected_event.selection.rows if hasattr(selected_event, "selection") and selected_event.selection else []

        if selected_indices and len(selected_indices) > 0 and selected_indices[0] < len(page_incident_df):
            sel_row = page_incident_df.iloc[selected_indices[0]]
            with st.expander(
                f"🔎 Forensic Request Inspector — Trace ID: `{sel_row['trace_id']}` ({sel_row['label']})",
                expanded=True,
            ):
                insp_c1, insp_c2, insp_c3, insp_c4 = st.columns(4)
                with insp_c1:
                    st.markdown(f"**Trace ID:** `{sel_row['trace_id']}`")
                    st.markdown(f"**Timestamp:** `{sel_row['timestamp']}`")
                with insp_c2:
                    st.markdown(f"**Client IP:** `{sel_row['client_ip']}`")
                    st.markdown(f"**Region:** `{sel_row['region']}`")
                with insp_c3:
                    st.markdown(f"**HTTP Status:** `{sel_row['status_code']}` ({sel_row['http_method']})")
                    st.markdown(f"**Latency:** `{sel_row['latency_ms']} ms`")
                with insp_c4:
                    st.markdown(f"**Target Microservice:** `{sel_row['service_name']}`")
                    st.markdown(f"**Classification:** `{sel_row['label']}`")

                st.markdown(f"**Target Endpoint:** `{sel_row['endpoint']}`")

                st.markdown("**User Agent:**")
                st.code(str(sel_row["user_agent"]), language="text")

                st.markdown("**Raw Payload Snippet:**")
                raw_payload = str(sel_row["payload_snippet"])
                lang = "json" if raw_payload.strip().startswith(("{", "[")) else "text"
                st.code(raw_payload, language=lang)
        else:
            with st.expander("🔎 Forensic Request Inspector (Select a row above to inspect details)", expanded=False):
                st.info("👆 Click or select any row in the table above to inspect its Trace ID, Client IP, User Agent, and raw Payload Snippet.")

# ---------------------------------------------------------
# Tab 4: Detailed Audit Log Explorer
# ---------------------------------------------------------
with tab_explorer:
    st.markdown(f"<div class='section-header'>🔬 Detailed Telemetry & Security Audit Logs</div>", unsafe_allow_html=True)

    filter_exp_c1, filter_exp_c2, filter_exp_c3 = st.columns([2, 1, 1])
    with filter_exp_c1:
        search_query = st.text_input(
            "🔎 Search (IP, Endpoint, Trace ID, Payload)",
            placeholder="e.g., /login, 198.51, curl, UNION, root...",
        )
    with filter_exp_c2:
        filter_label = st.selectbox(
            "Filter by Anomaly Type",
            options=["ALL"] + sorted(filtered_df["label"].unique().tolist()),
            index=0,
        )
    with filter_exp_c3:
        max_rows_display = st.select_slider(
            "Display Rows Limit",
            options=[50, 100, 250, 500, 1000],
            value=100,
        )

    # Apply table filters
    log_view = filtered_df
    if filter_label != "ALL":
        log_view = log_view[log_view["label"] == filter_label]

    if search_query:
        query_lower = search_query.lower()
        search_match = (
            log_view["trace_id"].astype(str).str.lower().str.contains(query_lower, na=False)
            | log_view["endpoint"].astype(str).str.lower().str.contains(query_lower, na=False)
            | log_view["client_ip"].astype(str).str.lower().str.contains(query_lower, na=False)
            | log_view["payload_snippet"].astype(str).str.lower().str.contains(query_lower, na=False)
            | log_view["user_agent"].astype(str).str.lower().str.contains(query_lower, na=False)
        )
        log_view = log_view[search_match]

    st.caption(f"Showing up to **{max_rows_display}** of **{len(log_view):,}** matched records")

    display_cols = [
        "trace_id",
        "timestamp",
        "service_name",
        "region",
        "http_method",
        "endpoint",
        "status_code",
        "latency_ms",
        "client_ip",
        "label",
        "payload_snippet",
    ]

    st.dataframe(
        log_view[display_cols].head(max_rows_display),
        width="stretch",
        hide_index=True,
        column_config={
            "trace_id": st.column_config.TextColumn("Trace ID", width="small"),
            "timestamp": st.column_config.DatetimeColumn("Timestamp", format="YYYY-MM-DD HH:mm:ss"),
            "service_name": st.column_config.TextColumn("Service", width="small"),
            "region": st.column_config.TextColumn("Region", width="small"),
            "http_method": st.column_config.TextColumn("Method", width="small"),
            "endpoint": st.column_config.TextColumn("Endpoint"),
            "status_code": st.column_config.NumberColumn("Status", format="%d"),
            "latency_ms": st.column_config.NumberColumn("Latency", format="%d ms"),
            "client_ip": st.column_config.TextColumn("Client IP"),
            "label": st.column_config.TextColumn("Classification"),
            "payload_snippet": st.column_config.TextColumn("Payload / Event Data"),
        },
    )

    # Download CSV button
    csv_data = log_view.head(5000).to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Export Filtered Logs (CSV, up to 5,000 rows)",
        data=csv_data,
        file_name="filtered_security_audit_logs.csv",
        mime="text/csv",
    )

# ---------------------------------------------------------
# Footer
# ---------------------------------------------------------
st.markdown("---")
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: center; font-size: 0.8rem; color: {text_secondary};">
        <span>Autonomous Enterprise Telemetry & Incident System (AETIS) &bull; Production SOC Monitoring</span>
        <span>Telemetry Cache Active &bull; Refresh via Streamlit Menu (R)</span>
    </div>
    """,
    unsafe_allow_html=True,
)
