from crewai import Agent, Task, Crew, Process
from sec_filing_tool import SecFilingTool
from utils.helpers import get_openai_api_key, get_serper_api_key
import logging

# Load API keys
openai_api_key = get_openai_api_key()
serper_api_key = get_serper_api_key()

# Initialize the SEC Filing Tool
sec_filing_tool = SecFilingTool()

# External function to download the 10-K document and extract relevant parts.
def extract_10k_document(company_name: str) -> str:
    """
    This function downloads and parses the 10-K HTML document.
    """
    logging.info(f"Extracting 10-K document for {company_name}...")
    
    # Step 1: Get CIK and Download 10-K Filing
    company_cik = sec_filing_tool.get_cik(company_name)
    if not company_cik:
        return {"Error": f"Unable to retrieve CIK for {company_name}"}

    filings_data = sec_filing_tool.fetch_submissions(company_cik)
    if "Error" in filings_data:
        return {"Error": filings_data["Error"]}

    ten_k_filings = sec_filing_tool.get_10k_filings(filings_data)
    if not ten_k_filings:
        return {"Error": "No 10-K filings found."}

    # Get the first 10-K filing URL and download its content
    first_filing_url = ten_k_filings[0]["Filing URL"]
    submission_text_url = sec_filing_tool.extract_submission_text_url(first_filing_url)
    
    if "Error" in submission_text_url:
        return submission_text_url  # Return the error message directly

    raw_10k_document = sec_filing_tool.download_submission_text(submission_text_url)
    return raw_10k_document

# Step 1: Define the 10-K Document Processor Agent (GPT-3.5)
document_processor_agent = Agent(
    role="10-K Document Processor",
    goal="Organize and extract relevant sections from the 10-K filing.",
    memory=True,
    verbose=True,
    model="gpt-3.5-turbo",  # GPT-3.5 for faster processing
    backstory="An expert at structuring financial documents, specialized in SEC 10-K filings."
)

# Step 2: Define the Financial Analyst Agent (GPT-4)
analysis_agent = Agent(
    role="Financial Analyst",
    goal="Analyze the financial sections extracted from the 10-K filing and provide a summary.",
    memory=True,
    verbose=True,
    model="gpt-4",  # GPT-4 for deeper analysis
    backstory="A seasoned financial analyst focused on interpreting 10-K filings."
)

# Task: Process the 10-K Document
process_10k_task = Task(
    description=(
        "Clean and extract relevant sections from the raw 10-K HTML document. "
        "The focus should be on key financial sections such as the Income Statement, "
        "Balance Sheet, and Cash Flow Statement."
    ),
    expected_output="Processed sections of the 10-K document.",
    agent=document_processor_agent,
    tools=[],  # No external tools, processing the HTML
    inputs={"raw_10k_document": "{raw_10k_document}"}
)

# Task: Analyze the 10-K Document
analyze_10k_task = Task(
    description=(
        "Analyze the financial data from the 10-K document. Extract insights from the financial statements "
        "such as revenue, profit, assets, liabilities, and cash flow. Provide a summary analysis."
    ),
    expected_output="Summary of key financial metrics and insights.",
    agent=analysis_agent,
    tools=[],  # LLM analysis only
    inputs={"processed_10k_sections": "{processed_10k_sections}"}
)

# Define Crew for multi-agent collaboration
sec_analysis_crew = Crew(
    agents=[document_processor_agent, analysis_agent],
    tasks=[process_10k_task, analyze_10k_task],
    process=Process.sequential  # Agents will work in sequence to process and analyze
)

def analyze_company(company_name: str) -> dict:
    """
    Full flow to extract the raw 10-K document, process it, and then analyze the extracted financial sections.
    """
    print(f"Starting analysis for company {company_name}...")
    
    # Step 1: Extract raw 10-K document (outside the agents)
    raw_10k_document = extract_10k_document(company_name)
    
    if isinstance(raw_10k_document, dict) and "Error" in raw_10k_document:
        return {"Error": raw_10k_document["Error"]}
    
    print("10-K document extracted. Kicking off crew for processing and analysis...")
    
    # Step 2: Kick off the CrewAI agents for processing and analysis
    crew_result = sec_analysis_crew.kickoff(inputs={"raw_10k_document": raw_10k_document})
    
    if isinstance(crew_result, str):
        summary_report = crew_result  # Single output string
    elif isinstance(crew_result, dict):
        processing_result = crew_result.get('process_10k_task_output', 'Processing task did not return output.')
        analysis_result = crew_result.get('analyze_10k_task_output', 'Analysis task did not return output.')
        summary_report = f"Processed 10-K Sections:\n{processing_result}\n\nFinancial Analysis Result:\n{analysis_result}"
    else:
        return {"Error": "Unexpected format for crew_result."}
    
    # Step 3: Return the final result to the app
    return {
        "Company Name": company_name,
        "Summary Report": summary_report
    }


# def analyze_company(company_name: str) -> dict:
#     """
#     This function retrieves the CIK for the given company name and fetches the company's SEC filings 
#     directly, bypassing the CrewAI tool issue.
#     """
#     # Step 1: Fetch the CIK manually
#     print(f"Starting search for company {company_name}...")
    
#     company_cik = sec_filing_tool.get_cik(company_name)
#     print(f"Company CIK: {company_cik}")
#     if not company_cik:
#         return {"Error": f"Unable to retrieve CIK for {company_name}"}

#     # Fetch the 10-K filings directly without the CrewAI tool
#     filings_data = sec_filing_tool.fetch_submissions(company_cik)  # Pass CIK directly
#     if "Error" in filings_data:
#         return {"Error": filings_data["Error"]}

#     ten_k_filings = sec_filing_tool.get_10k_filings(filings_data)
#     if not ten_k_filings:
#         return {"Error": "No 10-K filings found."}

#     # Create the summary report based on the fetched filings
#     summary_report = f"Company {company_name} has {len(ten_k_filings)} recent 10-K filings."

#     # Return the result without involving the CrewAI tool
#     return {
#         "Company Name": company_name,
#         "CIK": company_cik,
#         "10-K Filings": ten_k_filings,
#         "Summary Report": summary_report
#     }
