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

                # Fetch detailed analysis for each 10-K filing
                st.write("### 10-K Report Analysis")
                for filing in result["10-K Filings"]:
                    filing_url = filing["Filing URL"]
                    submission_text = Sec_filing_tool.extract_submission_text_url(filing_url)
                    st.write(f"#### Analysis for {filing['Accession Number']}")
                    st.text(submission_text)
    else:
        st.warning("Please enter a valid company name.")
