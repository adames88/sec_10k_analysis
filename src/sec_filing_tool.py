from crewai_tools import tool
import requests
from bs4 import BeautifulSoup
import pandas as pd

@tool
class SecFilingTool:
    def __init__(self):
        self.base_url = "https://www.sec.gov/cgi-bin/browse-edgar"
        self.headers = {"User-Agent": "Your Company Name"}

    def fetch_10k(self, company_ticker):
        url = f"{self.base_url}?action=getcompany&CIK={company_ticker}&type=10-k&owner=exclude&count=1"
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            return f"Error fetching 10-K data for {company_ticker}"

    def parse_metadata(self, filing_data):
        # Using BeautifulSoup to parse the HTML content from EDGAR
        soup = BeautifulSoup(filing_data, 'html.parser')

        # Example of extracting key metadata based on JSON file details
        metadata = {}

        # Accession Number
        adsh = soup.find('adsh')  # Assuming the HTML/XML contains this field
        if adsh:
            metadata['Accession Number'] = adsh.get_text()

        # CIK (Central Index Key)
        cik = soup.find('cik')
        if cik:
            metadata['CIK'] = cik.get_text()

        # Registrant Name
        registrant = soup.find('name')
        if registrant:
            metadata['Registrant'] = registrant.get_text()

        # SIC Code (Standard Industrial Classification)
        sic = soup.find('sic')
        if sic:
            metadata['SIC'] = sic.get_text()

        # Public Float
        public_float = soup.find('pubfloatusd')
        if public_float:
            metadata['Public Float'] = public_float.get_text()

        # Filing Status
        status = soup.find('afs')
        if status:
            metadata['Accelerated Filer Status'] = status.get_text()

        # Fiscal Year End Date
        fiscal_year_end = soup.find('fye')
        if fiscal_year_end:
            metadata['Fiscal Year End'] = fiscal_year_end.get_text()

        return metadata

    def parse_financial_data(self, filing_data):
        # Parse financial data such as revenue, net income, and assets
        soup = BeautifulSoup(filing_data, 'html.parser')

        financial_data = {}

        # Example of extracting structured financial data based on metadata details
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

    def run(self, company_ticker):
        filing_data = self.fetch_10k(company_ticker)
        if "Error" in filing_data:
            return filing_data
        
        metadata = self.parse_metadata(filing_data)
        financial_data = self.parse_financial_data(filing_data)

        # Combine both metadata and financial data into a single response
        result = {
            "Metadata": metadata,
            "Financial Data": financial_data
        }

        return result

