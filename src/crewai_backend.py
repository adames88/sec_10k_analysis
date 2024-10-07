import os
import requests
from crewai import Agent, Task, Crew, Process
from sec_filing_tool import SecFilingTool
from crewai_tools import FileReadTool
from utils.helpers import get_openai_api_key, get_serper_api_key
from sec_filing_tool_crewai import SecFilingToolWithUserAgent

# Load API keys
openai_api_key = get_openai_api_key()
serper_api_key = get_serper_api_key()

# Initialize the SEC Filing Tool with User-Agent
sec_filing_tool = SecFilingTool()
sec_filing_userAgent = SecFilingToolWithUserAgent()

# Step 1: Extract and save the complete submission text file

def extract_and_save_10k_submission(company_name: str) -> str:
    """
    Extract the complete submission text file for the 10-K filing and save it locally with a proper user-agent.
    """
    # Get CIK for the company
    company_cik = sec_filing_tool.get_cik(company_name)
    if not company_cik:
        return {"Error": f"Unable to retrieve CIK for {company_name}"}
    
    # Fetch the list of submissions using the CIK
    filings_data = sec_filing_tool.fetch_submissions(company_cik)
    if "Error" in filings_data:
        return {"Error": filings_data["Error"]}
    
    # Extract the URL of the complete submission text file
    ten_k_filings = sec_filing_tool.get_10k_filings(filings_data)
    if not ten_k_filings:
        return {"Error": "No 10-K filings found."}
    
    # Get the submission text URL
    submission_text_url = sec_filing_tool.extract_submission_text_url(ten_k_filings[0]["Filing URL"])
    if "Error" in submission_text_url:
        return submission_text_url
    
    # Custom headers with User-Agent
    headers = {
        "User-Agent": "Your Company Name AdminContact@yourcompany.com",
    }
    
    # Download the complete submission text file with custom headers
    try:
        response = requests.get(submission_text_url, headers=headers)
        response.raise_for_status()  # Raise an error for bad responses
        raw_text = response.text
    except requests.RequestException as e:
        return {"Error": f"Failed to download the submission text: {str(e)}"}

    # Define the file path in the current working directory (absolute path)
    file_path = os.path.abspath(os.path.join(os.getcwd(), "10K_submission.txt"))

    # Save the file
    try:
        with open(file_path, "w") as file:
            file.write(raw_text)
        print(f"File saved successfully: {file_path}")  # Debugging: print the full file path
    except IOError as e:
        return {"Error": f"Failed to save the file: {str(e)}"}

    return file_path


# Step 2: Define Agent 1 for processing the 10-K submission file

def create_processing_agent(file_path: str):
    # Initialize FileReadTool with the specific file path
    file_read_tool = FileReadTool(file_path=file_path)
    
    return Agent(
        role="10-K Document Processor",
        goal="Process the submission text file of the 10-K and extract relevant financial sections as text.",
        memory=True,
        verbose=True,
        backstory="A highly skilled agent in reading and structuring SEC filings for analysis.",
        tools=[file_read_tool],  # Use FileReadTool initialized with the specific file path
        model="gpt-3.5-turbo"  # Using GPT-3.5 for document processing
    )


# Task 1: Process 10-K text file and extract relevant sections
def create_process_10k_task(file_path: str):
    processing_agent = create_processing_agent(file_path)
    return Task(
        description=(
            "Process the 10-K submission text file and convert it into structured text. Extract "
            "relevant sections such as the income statement, balance sheet, and cash flow statement."
        ),
        expected_output="A structured text format of relevant financial data extracted from the 10-K submission.",
        agent=processing_agent,
        inputs={"file_path": file_path},  # Pass the absolute file path directly
        async_execution=False
    )


# Step 3: Define Agent 2 for deep financial analysis
analysis_agent = Agent(
    role="Financial Analyst",
    goal="Perform a deep financial analysis on the extracted text data.",
    memory=True,
    verbose=True,
    backstory="An experienced financial analyst specializing in summarizing complex financial reports.",
    tools=[],  # No additional tools needed for the analysis
    model="gpt-4"  # Use GPT-4 for deeper analysis
)

# Task 2: Analyze the extracted sections from the 10-K
def create_analyze_10k_task():
    return Task(
        description=(
            "Analyze the relevant sections of the 10-K filing extracted by the previous task. Perform a financial analysis, "
            "including key metrics like revenue, profit, cash flow, and provide insights into the company's financial health."
        ),
        expected_output="A financial analysis report summarizing the company's financial status.",
        agent=analysis_agent,
        inputs={"extracted_sections": "{process_10k_task_output}"},  # Pass the extracted sections from Task 1
        async_execution=False
    )


# Define the Crew for multi-agent collaboration
def create_sec_analysis_crew(file_path: str):
    return Crew(
        agents=[create_processing_agent(file_path), analysis_agent],
        tasks=[create_process_10k_task(file_path), create_analyze_10k_task()],
        process=Process.sequential  # Ensure the agents work sequentially
    )


# Step 4: Full flow to analyze company
def analyze_company(company_name: str) -> dict:
    """
    Full flow to extract the 10-K submission file, process it, and then analyze the extracted financial sections.
    """
    print(f"Starting analysis for company {company_name}...")
    
    # Extract and save the 10-K submission file
    file_path = extract_and_save_10k_submission(company_name)
    
    # Check if the returned result is an error or the actual file path
    if isinstance(file_path, dict) and "Error" in file_path:
        return {"Error": file_path["Error"]}
    
    print(f"10-K submission file saved at: {file_path}")  # Debugging: confirm the file path before passing
    
    # Create the crew with the correct file path
    sec_analysis_crew = create_sec_analysis_crew(file_path)
    
    # Start the CrewAI process for agents
    try:
        crew_result = sec_analysis_crew.kickoff(inputs={"file_path": file_path})
    except Exception as e:
        return {"Error": f"An error occurred during the crew execution: {str(e)}"}

    # Handle crew result based on its type (string or dict)
    if isinstance(crew_result, str):
        # If the result is a string, treat it as a single output
        summary_report = crew_result
    elif isinstance(crew_result, dict):
        # If the result is a dictionary, extract the output of both tasks
        processing_result = crew_result.get('process_10k_task_output', 'Processing task did not return output.')
        analysis_result = crew_result.get('analyze_10k_task_output', 'Analysis task did not return output.')
        
        # Build the summary report
        summary_report = f"Company {company_name} has a processed 10-K submission.\n\n"
        summary_report += "Processed 10-K Sections:\n"
        summary_report += processing_result
        summary_report += "\n\nFinancial Analysis Result:\n"
        summary_report += analysis_result
    else:
        return {"Error": "Unexpected format for crew_result."}
    
    # Clean up: Delete the local file after processing (optional)
    # os.remove(file_path)
    
    # Return the final result
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
