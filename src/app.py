import streamlit as st
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from crewai_backend import analyze_company
import pandas as pd
from utils.helpers import get_openai_api_key, get_serper_api_key
from sec_filing_tool import SecFilingTool
# Set OpenAI model key and serper key:
openai_api_key = get_openai_api_key()
serper_api_key = get_serper_api_key()

st.title("SEC 10-K Analysis Dashboard")

Sec_filing_tool = SecFilingTool()


# Input for the company name
company_name = st.text_input("Enter a company name (e.g., Apple, Tesla):")

# Trigger the analysis
if st.button("Analyze"):
    if company_name:
        st.write(f"Analyzing {company_name}...")
        result = analyze_company(company_name)

        # Display the result
        if "Error" in result:
            st.error(result["Error"])
        else:
            st.write("### Summary Report")
            st.text(result["Summary Report"])

            if "10-K Filings" in result:
                st.write("### 10-K Filings")
                filings_df = pd.DataFrame(result["10-K Filings"])
                st.dataframe(filings_df)

            # Display the Financial Analyst's final analysis
            if "Financial Analysis" in result:
                st.write("### Financial Analysis")
                st.text(result["Financial Analysis"])
    else:
        st.warning("Please enter a valid company name.")
