"""
Securities Analyzer Worker Module

This module provides a Streamlit web application for analyzing securities
using multi-agent AI analysis. It integrates various analysis components
to generate comprehensive investment reports.
"""

import os
import yfinance as yf
import streamlit as st
from agno.agent import Agent
from agno.models.google import Gemini
import plotly.graph_objects as go
from compare_securities_1 import compare_stocks
from market_analyst_2 import get_market_analysis
from company_researcher_3 import get_company_analysis
from securities_strategist_4 import get_stock_recommendations
from team_lead_5 import get_final_investment_report

# Set environment variable for Google API
os.environ["GOOGLE_API_KEY"] = "AIzaSyCYeGTKVMp1PTIXgx0bvgKb1gPSj9hYEVo"


def configure_page():
    """Configure Streamlit page settings and styling."""
    st.set_page_config(
        page_title="Securities Analyzer",
        page_icon="📈",
        layout="wide"
    )


def inject_custom_css():
    """Inject custom CSS styling for the application."""
    st.markdown(
        """
        <style>
            /* ---- Google fonts ---- */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600&family=JetBrains+Mono:wght@400;600&display=swap');

            /* ------  Global background  ------ */
            html, body, [class*="css"]  {
                font-family: 'Inter', sans-serif;
                color: #22272e;
                background: linear-gradient(135deg,#FFD8BC 0%,#FF968B 35%,#8BC6FF 100%) fixed;
            }

            /* Header card with warm gradient */
            .header-card {
                background: linear-gradient(120deg,#FF7E5F,#FFB199);
                border-radius: 16px;
                padding: 26px 34px;
                margin-bottom: 1.8rem;
                box-shadow: 0 8px 18px rgba(0,0,0,0.15);
                color: #ffffff;
            }

            /* Sidebar card with fresh greens */
            .sidebar-card {
                background: linear-gradient(135deg,#ABE9CE 0%, #3EADCF 100%);
                border-radius: 14px;
                padding: 20px;
                color:#08343c;
                box-shadow: 0 6px 14px rgba(0,0,0,0.12);
            }

            /* Input & button tweaks */
            input, textarea {
                background: rgba(255,255,255,0.85) !important;
                color:#22272e !important;
                border: 1px solid rgba(0,0,0,0.1) !important;
                border-radius: 6px !important;
            }

            /* Fancy primary button */
            button[kind="primary"] {
                background: linear-gradient(90deg,#845EF7 0%,#B388FF 100%) !important;
                border-radius: 10px !important;
                color:#ffffff !important;
                font-weight:600;
                transition: transform .15s ease-in-out;
            }
            button[kind="primary"]:hover {
                transform: scale(1.04);
            }

            /* Scrollbar in coral tone */
            ::-webkit-scrollbar {
                width: 8px;
            }
            ::-webkit-scrollbar-thumb {
                background: #ff7e5f;
                border-radius: 8px;
            }
        </style>
        """,
        unsafe_allow_html=True
    )


def render_header():
    """Render the application header."""
    st.markdown(
        """
        <div class="header-card">
            <h1 style="text-align:center; margin:0;">📈 Securities Analyzer</h1>
            <h4 style="text-align:center; font-weight:300; margin:6px 0 0;">
                Personalised reports powered by multi-agent AI
            </h4>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar():
    """
    Render the sidebar with configuration options.
    
    Returns:
        tuple: A tuple containing (input_symbols, api_key, run_button_clicked)
    """
    with st.sidebar:
        st.markdown(
            """
            <div class="sidebar-card">
                <h3 style="margin-top:0;">⚙️ Configuration</h3>
                <p style="font-size:0.9rem;">
                    Enter one or more tickers US<br>
                    Analyze for 6-month performance, fundamentals & news.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        input_symbols = st.text_input(
            "Stock Symbols (comma-separated)", "AAPL, TSLA, GOOG"
        )
        api_key = st.text_input("Google API Key", type="password")
        run = st.button("🚀 Generate Report", use_container_width=True)

    return input_symbols, api_key, run


def parse_symbols(input_symbols):
    """
    Parse and validate stock symbols from input string.
    
    Args:
        input_symbols (str): Comma-separated string of stock symbols
        
    Returns:
        list: List of cleaned and uppercase stock symbols
    """
    return [s.strip().upper() for s in input_symbols.split(",") if s.strip()]


def create_price_chart(symbols, price_df):
    """
    Create a Plotly chart for stock price history.
    
    Args:
        symbols (list): List of stock symbols
        price_df (pd.DataFrame): DataFrame containing price data
        
    Returns:
        plotly.graph_objects.Figure: Configured Plotly figure
    """
    fig = go.Figure()
    for sym in symbols:
        fig.add_trace(
            go.Scatter(
                x=price_df.index,
                y=price_df[sym],
                mode="lines",
                name=sym,
                hovertemplate=f"{sym}: %{{y:.2f}}<extra></extra>",
            )
        )
    fig.update_layout(
        height=480,
        margin=dict(l=0, r=0, t=30, b=0),
        xaxis_title="Date",
        yaxis_title="Price (USD)",
        template="plotly_white",
        colorway=["#FF7E5F", "#57C1EB", "#845EF7", "#FFC75F", "#F85F73"]
    )
    return fig


def main():
    """Main application function."""
    # Configure page and styling
    configure_page()
    inject_custom_css()
    
    # Render UI components
    render_header()
    input_symbols, api_key, run = render_sidebar()
    
    # Parse symbols
    symbols = parse_symbols(input_symbols)
    
    # Main action
    if run:
        if not symbols:
            st.error("Please enter at least one valid ticker.")
            st.stop()
        if not api_key:
            st.error("Please provide your Google API key.")
            st.stop()

        os.environ["GOOGLE_API_KEY"] = api_key  # use the user's key

        with st.spinner("Crunching data and drafting your report…"):
            report_md = get_final_investment_report(symbols)
            price_df = yf.download(symbols, period="6mo")["Close"]

        # Layout: two columns
        col_report, col_chart = st.columns((1.25, 1), gap="large")

        with col_report:
            st.subheader("📑 Investment Report")
            st.markdown(report_md, unsafe_allow_html=True)
            st.info(
                "This report blends historical performance, fundamentals & news. "
                "Use it as a starting point, not financial advice."
            )

        with col_chart:
            st.subheader("📊 Price History (6 mo.)")
            fig = create_price_chart(symbols, price_df)
            st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    main()
