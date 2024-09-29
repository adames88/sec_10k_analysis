import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from dotenv import load_dotenv
from crewai_backend import analyze_company
import pandas as pd
import plotly.express as px


# Load environment variables from .env file
load_dotenv()

# Access the OpenAI API Key
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    raise ValueErro

# Streamlit layout
st.title("SEC 10-K Analysis Dashboard")

# User input for the company name
company_name = st.text_input("Enter a company name (e.g., AAPL for Apple):")

# When the user submits, trigger the analysis
if st.button("Analyze"):
    if company_name:
        st.write(f"Analyzing {company_name}...")
        result = analyze_company(company_name)

        # Display Metadata
        st.write("### Metadata")
        if "Metadata" in result:
            metadata = result["Metadata"]
            st.json(metadata)

        # Display Financial Data
        st.write("### Financial Data")
        if "Financial Data" in result:
            financial_data = result["Financial Data"]
            
            # Create a DataFrame for better presentation
            df = pd.DataFrame({
                "Metric": ["Revenue", "Net Income", "Assets", "Liabilities"],
                "Value": [financial_data.get("Revenue"), financial_data.get("Net Income"), financial_data.get("Assets"), financial_data.get("Liabilities")]
            })
            st.dataframe(df)

            # Plot financial data
            fig = px.bar(df, x="Metric", y="Value", title=f"Financial Metrics for {company_name}")
            st.plotly_chart(fig)
        else:
            st.error("Financial data not available.")
    else:
        st.warning("Please enter a company name.")
