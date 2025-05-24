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



# -------------------------------- Team Lead agent --------------------------------- #
team_lead = Agent(
    model=Gemini(id="gemini-2.0-flash-exp"),
    description="Aggregates stock analysis, company research, and investment strategy.",
    instructions=[
        "Compile stock performance, company analysis, and recommendations.",
        "give me insight if I can invest in that or not",
        "For how long should I invest"
    ],
    markdown=True
)

def get_final_investment_report(symbols):
    market_analysis = get_market_analysis(symbols)
    company_analyses = [get_company_analysis(symbol) for symbol in symbols]
    stock_recommendations = get_stock_recommendations(symbols)

    final_report = team_lead.run(
        f"Market Analysis:\n{market_analysis}\n\n"
        f"Company Analyses:\n{company_analyses}\n\n"
        f"Stock Recommendations:\n{stock_recommendations}\n\n"
        f"Generate a final ranked list in ascending order on which should I buy."
    )
    return final_report.content