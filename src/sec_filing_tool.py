import requests
import logging

class SecFilingTool:
    def __init__(self):
        # New endpoint based on correct structure
        self.edgar_company_search_url = "https://efts.sec.gov/LATEST/search-index"
        self.headers = {"User-Agent": "YourAppName"}

    def get_cik(self, company_name: str) -> str:
        """
        Fetch the CIK (Central Index Key) for the given company name using SEC's EDGAR API.
        This function will attempt to match the exact company based on the 'display_names' field.
        """
        url = self.edgar_company_search_url
        params = {
            "q": company_name,  # Query company name
            "entity": "company",  # Ensure entity type is specified
        }

        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code != 200:
                logging.error(f"Failed to fetch CIK for {company_name}. Status code: {response.status_code}")
                return None

            data = response.json()

            # Print full response for debugging purposes
            print(f"Full response data for {company_name}: {data}")

            # Ensure hits exist and check for exact match on 'display_names'
            hits = data.get('hits', {}).get('hits', [])
            if not hits:
                logging.error(f"No results found for {company_name}. Response data: {data}")
                return None

            # Loop through hits and look for exact match on 'display_names'
            for hit in hits:
                display_name = hit['_source'].get('display_names', [''])[0]
                if company_name.lower() in display_name.lower():
                    cik = hit['_source'].get('ciks', [None])[0]
                    if cik:
                        print(f"CIK for {company_name}: {cik}")
                        return cik

            logging.error(f"CIK not found for {company_name}. Response data: {data}")
            return None

        except requests.exceptions.RequestException as e:
            logging.error(f"Request exception occurred: {e}")
            return None

        except Exception as e:
            logging.error(f"Error parsing CIK for {company_name}: {e}")
            return None



    def fetch_submissions(self, company_cik: str) -> dict:
        """
        Fetch the SEC filings for a given company CIK.
        """
        submissions_url = f"https://data.sec.gov/submissions/CIK{company_cik}.json"
        response = requests.get(submissions_url, headers=self.headers)
        if response.status_code == 200:
            return response.json()
        else:
            return {"Error": f"Failed to fetch data. Status code: {response.status_code}"}

    def get_10k_filings(self, company_data: dict) -> list:
        """
        Extract 10-K filings and construct the URLs.
        """
        filings = company_data.get("filings", {}).get("recent", {})
        form_type = filings.get("form", [])
        accession_numbers = filings.get("accessionNumber", [])
        filing_dates = filings.get("filingDate", [])
        
        ten_k_filings = []

        # Loop through filings to find 10-K forms
        for i, form in enumerate(form_type):
            if form == "10-K":
                ten_k_filings.append({
                    "Accession Number": accession_numbers[i],
                    "Filing Date": filing_dates[i],
                    "Filing URL": f"https://www.sec.gov/Archives/edgar/data/{company_data['cik']}/{accession_numbers[i].replace('-', '')}/{accession_numbers[i]}-index.html"
                })
        
        return ten_k_filings

    def extract_submission_text_url(self, filing_url: str) -> str:
        """
        Scrape the filing URL page to find the "Complete submission text files" link.
        """
        response = requests.get(filing_url, headers=self.headers)
        if response.status_code != 200:
            return {"Error": f"Failed to load the filing page. Status code: {response.status_code}"}

        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for the "Complete submission text files" link
        link = soup.find('a', text='Complete submission text files')
        if link and link.get('href'):
            return f"https://www.sec.gov{link.get('href')}"
        else:
            return {"Error": "Complete submission text file not found"}

    def download_submission_text(self, submission_text_url: str) -> str:
        """
        Download the content from the "Complete submission text files" link.
        """
        response = requests.get(submission_text_url, headers=self.headers)
        if response.status_code == 200:
            return response.text
        else:
            return {"Error": f"Failed to download submission text. Status code: {response.status_code}"}