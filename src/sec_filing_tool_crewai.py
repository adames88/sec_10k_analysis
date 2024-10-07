from crewai_tools import ScrapeWebsiteTool
import requests

class SecFilingToolWithUserAgent(ScrapeWebsiteTool):
    """
    A ScrapeWebsiteTool subclass that uses custom headers to declare the user agent.
    This helps comply with SEC.gov guidelines for automated requests.
    """
    def __init__(self):
        super().__init__()  # Initialize the ScrapeWebsiteTool class
        self.headers = {
            "User-Agent": "Your Company Name AdminContact@yourcompany.com",
        }

    def run(self, website_url: str) -> str:
        """
        Override the run method to include headers with the custom User-Agent.
        """
        try:
            # Make a request using the custom headers
            response = requests.get(website_url, headers=self.headers)
            if response.status_code == 200:
                # Scrape the website content using the parent class's run method
                return super().run(website_url=website_url)
            else:
                return {"Error": f"Failed to scrape the website. Status code: {response.status_code}"}
        except Exception as e:
            return {"Error": f"Exception occurred: {str(e)}"}
