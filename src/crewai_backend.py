from crewai import Agent, Task, Crew, Process
from sec_filing_tool import SecFilingTool
from sec_filing_tool_crewai import SecFilingToolCrewAI
from utils.helpers import get_openai_api_key, get_serper_api_key

# Load API keys
openai_api_key = get_openai_api_key()
serper_api_key = get_serper_api_key()

# Initialize the SEC Filing Tool
sec_filing_tool = SecFilingTool()

# Step 1: Define the File Downloader and Extractor Agent (using GPT-3.5)
download_agent = Agent(
    role="File Downloader and Extractor",
    goal="Download the 10-K filings and extract relevant sections of the document for financial analysis.",
    memory=True,
    verbose=True,
    backstory="An agent specialized in downloading and extracting relevant sections of SEC filings.",
    tools=[SecFilingToolCrewAI()],  # Custom tool to fetch and download the file
    model="gpt-3.5-turbo"  # Use GPT-3.5 model to handle this task
)

# Step 2: Define the Financial Analyst Agent (using GPT-4)
analysis_agent = Agent(
    role="Financial Analyst",
    goal="Analyze the extracted content from the 10-K filings and provide insights into the company's financial health.",
    memory=True,
    verbose=True,
    backstory="An experienced financial analyst using cutting-edge technology to analyze complex financial reports.",
    tools=[],  # This agent does the analysis without additional tools
    model="gpt-4"  # Use GPT-4 model for deeper analysis
)

# Task: Download and Extract Task
download_task = Task(
    description="Download the 10-K filings for the company and extract the relevant sections for analysis.",
    expected_output="Extracted content from the 10-K filings.",
    agent=download_agent,
    inputs={"filing_url": "{filing_url}"},  # Input URL of the filing
    async_execution=False  # Ensure the task completes before proceeding to analysis
)

# Task: Analyze 10-K Filings Task
analyze_10k_task = Task(
    description=(
        "Analyze the extracted sections of the 10-K filings. Extract key financial data such as revenue, profit, "
        "and cash flow. Provide insights into the company's financial health."
    ),
    expected_output="A financial analysis report summarizing the company's key financial metrics.",
    agent=analysis_agent,
    tools=[],  # This task can be expanded with external analysis tools
    inputs={"extracted_text": "{download_task_output}"},  # Pass the output of the first task (downloaded and extracted text)
    async_execution=False  # Ensure synchronous execution
)

# Define Crew for multi-agent collaboration
sec_analysis_crew = Crew(
    agents=[download_agent, analysis_agent],
    tasks=[download_task, analyze_10k_task],
    process=Process.sequential  # Agents will work in sequence: download and extract first, then analyze
)

def analyze_company(company_name: str) -> dict:
    """
    This function retrieves the CIK for the given company name, triggers the CrewAI process 
    to download and analyze the company's 10-K filings, and returns a detailed report.
    """
    # Step 1: Fetch CIK and 10-K filings using the SecFilingTool
    print(f"Starting search for company {company_name}...")
    
    company_cik = sec_filing_tool.get_cik(company_name)
    print(f"Company CIK: {company_cik}")
    if not company_cik:
        return {"Error": f"Unable to retrieve CIK for {company_name}"}
    
    # Fetch submissions (10-K filings) for the company using the CIK
    filings_data = sec_filing_tool.fetch_submissions(company_cik)
    if "Error" in filings_data:
        return {"Error": filings_data["Error"]}
    
    ten_k_filings = sec_filing_tool.get_10k_filings(filings_data)
    if not ten_k_filings:
        return {"Error": "No 10-K filings found."}
    
    # Step 2: Use the first available 10-K filing URL for demonstration purposes
    filing_url = ten_k_filings[0]["Filing URL"]
    
    # Step 3: Kick off the CrewAI process with the necessary inputs (filing URL and company name)
    print("Kicking off CrewAI process for downloading and analyzing the 10-K filing...")
    
    try:
        crew_result = sec_analysis_crew.kickoff(inputs={"company_name": company_name, "filing_url": filing_url})
    except Exception as e:
        return {"Error": f"An error occurred while executing the crew: {str(e)}"}
    
    # Step 4: The crew_result contains the final analysis from both agents
    download_result = crew_result.get('download_task_output', 'Download task did not return output.')
    analysis_result = crew_result.get('analyze_10k_task_output', 'Analysis task did not return output.')
    
    summary_report = f"Company {company_name} has {len(ten_k_filings)} recent 10-K filings.\n\n"
    summary_report += "\n\nFinancial Analysis Result:\n"
    summary_report += analysis_result
    
    # Return the final result with the list of filings and the detailed summary report
    return {
        "Company Name": company_name,
        "CIK": company_cik,
        "10-K Filings": ten_k_filings,
        "Summary Report": summary_report,
        "Financial Analysis": analysis_result  # Add the final analysis to the response
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
