from crewai_tools import BaseTool
from sec_filing_tool import SecFilingTool

class SecFilingToolCrewAI(BaseTool):
    name: str = "Download Submission Text"
    description: str = "Download and organize the complete submission text for analysis."
      

    def _run(self, filing_url: str) -> str:
        """Use the tool to download the submission text based on the provided filing URL."""
        # Instance of the core logic class
        sec_tool = SecFilingTool()
        return sec_tool.download_submission_text(filing_url)
