# -------------------- Libraries and Modules -------------
from langchain import PromptTemplate, LLMChain
from langchain_community.chat_models.perplexity import ChatPerplexity
from langchain.chains import SequentialChain

# -------------------- Initialization --------------------
# API key and model initialization
PPLX_API_KEY = "API KEY GOES HERE"
llm = ChatPerplexity(model="sonar-reasoning", 
                     temperature=0.5, 
                     pplx_api_key=PPLX_API_KEY)

# -------------------- Chain Definitions --------------------
# 1. Market Data Analyst: Retrieve financial dataclear

market_data_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["ticker"],
        template=(
            "📈 For {ticker}, provide detailed and up-to-date financial data. Include current stock price, "
            "volume, key financial ratios (e.g., P/E, P/B, dividend yield), recent price trends, and relevant market indicators."
        )
    ),
    output_key="market_data"
)

# 2. Sentiment Analyst: Analyze news and social media sentiment
sentiment_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["ticker"],
        template=(
            "📰 For {ticker}, analyze recent news articles, social media posts, and expert commentary. "
            "Summarize the prevailing sentiment, highlight any key events, and note emerging trends that may impact the stock."
        )
    ),
    output_key="sentiment_analysis"
)

# 3. Macro-Economic Analyst: Evaluate macro-economic conditions
macro_analysis_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["ticker"],
        template=(
            "🌐 For {ticker}, analyze the current macro-economic environment. "
            "Include key indicators such as GDP growth, inflation rates, interest rates, unemployment trends, "
            "and central bank policies. Summarize how these factors could impact the overall market and the asset."
        )
    ),
    output_key="macro_analysis"
)

# 4. Quantitative Strategist: Develop a trading strategy
strategy_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["market_data", "sentiment_analysis", "macro_analysis"],
        template=(
            "📊 Using the detailed market data:\n{market_data}\n"
            "the sentiment analysis:\n{sentiment_analysis}\n"
            "and the macro-economic analysis:\n{macro_analysis}\n"
            "develop a sophisticated trading strategy. Outline a clear asset allocation, specify entry and exit points, "
            "detail risk management measures, and provide estimated expected returns. If applicable, incorporate algorithmic signals."
        )
    ),
    output_key="strategy"
)

# 5. Risk Manager: Assess the strategy's risk
risk_chain = LLMChain(
    llm=llm,
    prompt=PromptTemplate(
        input_variables=["strategy"],
        template=(
            "⚠️ Evaluate the following trading strategy:\n{strategy}\n"
            "Identify potential risks such as market volatility, liquidity issues, or unexpected market events. "
            "Summarize your risk assessment in 4 concise bullet points, and state in the final bullet point whether the strategy meets an acceptable risk tolerance."
        )
    ),
    output_key="risk_assessment"
)

# -------------------- Sequential Orchestration --------------------
sequential_agent = SequentialChain(
    chains=[market_data_chain, sentiment_chain, macro_analysis_chain, strategy_chain, risk_chain],
    input_variables=["ticker"],
    output_variables=["market_data", "sentiment_analysis", "macro_analysis", "strategy", "risk_assessment"],
    verbose=True
)

# -------------------- Run the Analysis --------------------
def run_ai_hedge_fund(ticker: str) -> None:
    result = sequential_agent({"ticker": ticker})
    
    print("\n======== AI Hedge Fund Analysis Results ========\n")
    
    print("📈 Market Data Retrieved:")
    print("--------------------------------------------------")
    print(result["market_data"], "\n")
    
    print("📰 Market Sentiment Analysis:")
    print("--------------------------------------------------")
    print(result["sentiment_analysis"], "\n")
    
    print("🌐 Macro-Economic Analysis:")
    print("--------------------------------------------------")
    print(result["macro_analysis"], "\n")
    
    print("📊 Developed Trading Strategy:")
    print("--------------------------------------------------")
    print(result["strategy"], "\n")
    
    print("⚠️ Risk Assessment:")
    print("--------------------------------------------------")
    print(result["risk_assessment"], "\n")
    
    print("==============================================\n")

# Run the analysis for a given ticker (e.g., "MSFT")
run_ai_hedge_fund("MSFT")