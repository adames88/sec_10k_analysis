from crewai_tools import tool
import requests
from bs4 import BeautifulSoup
import pandas as pd

class SecFilingTool:
    """
    A tool to fetch and parse SEC 10-K filings from the EDGAR database.
    
    Methods:
    --------
    fetch_10k(company_ticker: str) -> str:
        Fetches the 10-K filings for a given company ticker.

    parse_metadata(filing_data: str) -> dict:
        Parses the metadata from the 10-K filings, such as Accession Number, CIK, etc.

    parse_financial_data(filing_data: str) -> dict:
        Extracts financial data like revenue, net income, and assets from the 10-K filings.

    run(company_ticker: str) -> dict:
        Fetches and parses both metadata and financial data for a given company ticker.
    """

    def __init__(self):
        self.base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.headers = {"User-Agent": "Your Company Name"}

    def fetch_10k(self, company_ticker: str) -> str:
        """Fetches the latest 10-K filing for the given company ticker."""
        url = f"{self.base_url}?action=getcompany&CIK={company_ticker}&type=10-k&owner=exclude&count=1"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching 10-K data for {company_ticker}"

    def parse_metadata(self, filing_data: str) -> dict:
        """Parses the metadata from the filing data, including CIK, Accession Number, SIC code, etc."""
        soup = BeautifulSoup(filing_data, 'html.parser')

        metadata = {}

        # Accession Number
        adsh = soup.find('adsh')
        if adsh:
            metadata['Accession Number'] = adsh.get_text()

        # CIK (Central Index Key)
        cik = soup.find('cik')
        if cik:
            metadata['CIK'] = cik.get_text()

        # SIC Code (Standard Industrial Classification)
        sic = soup.find('sic')
        if sic:
            metadata['SIC'] = sic.get_text()

        # Public Float
        public_float = soup.find('pubfloatusd')
        if public_float:
            metadata['Public Float'] = public_float.get_text()

        return metadata

    def parse_financial_data(self, filing_data: str) -> dict:
        """Parses financial data such as revenue, net income, and assets from the 10-K filings."""
        soup = BeautifulSoup(filing_data, 'html.parser')

        financial_data = {}

        revenue = soup.find('revenue')
        if revenue:
            financial_data['Revenue'] = revenue.get_text()

        net_income = soup.find('net_income')
        if net_income:
            financial_data['Net Income'] = net_income.get_text()

        assets = soup.find('assets')
        if assets:
            financial_data['Assets'] = assets.get_text()

        liabilities = soup.find('liabilities')
        if liabilities:
            financial_data['Liabilities'] = liabilities.get_text()

        return financial_data


@tool
def sec_filing_tool(company_ticker: str) -> dict:
    """
    A tool that uses SecFilingTool class to fetch and parse 10-K data for a given company ticker.

    Parameters:
    ----------
    company_ticker : str
        The ticker symbol of the company to analyze.
    
    Returns:
    --------
    dict
        A dictionary containing the metadata and financial data of the company's 10-K filing.
    """
    tool = SecFilingTool()
    filing_data = tool.fetch_10k(company_ticker)
    if "Error" in filing_data:
        return {"Error": filing_data}
    
    metadata = tool.parse_metadata(filing_data)
    financial_data = tool.parse_financial_data(filing_data)

    return {
        "Metadata": metadata,
        "Financial Data": financial_data
    }
