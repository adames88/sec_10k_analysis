from crewai import Agent, Task, Crew, Process
from sec_filing_tool import SecFilingTool
from utils.helpers import get_openai_api_key, get_serper_api_key
from crewai_tools import Tool  # Import for tool validation and registration

# Load API keys
openai_api_key = get_openai_api_key()
serper_api_key = get_serper_api_key()

# Initialize the SEC Filing Tool
sec_filing_tool = SecFilingTool()

# Define a wrapper to register the SEC filing tool correctly
fetch_sec_data_tool = Tool(
    name="SEC Filing Tool",
    func=sec_filing_tool.fetch_submissions,  # Correct reference to the tool method
    description="Fetch SEC filings for the company based on CIK.",
)

# Step 1: Define the SEC Search Agent
search_agent = Agent(
    role="SEC Search Agent",
    goal="Fetch the 10-K filings from the SEC API for the given company.",
    memory=True,
    verbose=True,
    backstory="A highly skilled agent specialized in fetching SEC filings for financial analysis.",
    tools=[fetch_sec_data_tool]  # Correctly attach the tool using Tool registration
)

# Step 2: Define the Financial Analyst Agent
analysis_agent = Agent(
    role="Financial Analyst",
    goal="Analyze the content of the SEC filings and provide insights into the company's financials.",
    memory=True,
    verbose=True,
    backstory="An experienced financial analyst who excels at analyzing complex financial reports.",
    tools=[]  # Analysis tools like LLMs or others can be added here later
)

# Task: Fetch 10-K Filings Task
fetch_10k_task = Task(
    description=(
        "Retrieve the 10-K filings for the company from the SEC using the company's CIK. "
        "Use the SEC API to retrieve the 10-K filings, including the filing dates and URLs."
    ),
    expected_output="A list of 10-K filings including URLs to access the documents.",
    agent=search_agent,
    tools=[fetch_sec_data_tool],  # Ensure the tool is correctly passed to the task
    inputs={"CIK": "{cik}"}  # Correct input format
)

# Task: Analyze 10-K Filings Task
analyze_10k_task = Task(
    description=(
        "Analyze the retrieved 10-K filings. Extract key financial data such as revenue, profit, "
        "and cash flow. Provide insights into the company's financial health based on the analysis."
    ),
    expected_output="A summary report of the company's key financial metrics based on the 10-K filings.",
    agent=analysis_agent,
    tools=[]  # Analysis tools can be added here if needed
)

# Define Crew for multi-agent collaboration
sec_analysis_crew = Crew(
    agents=[search_agent, analysis_agent],
    tasks=[fetch_10k_task, analyze_10k_task],
    process=Process.sequential  # Agents will work in sequence to fetch and analyze
)

def analyze_company(company_name: str) -> dict:
    """
    This function retrieves the CIK for the given company name and triggers the CrewAI process 
    to analyze the company's SEC filings and financial data.
    """
    # Step 1: Fetch 10-K filings using the Search Agent
    print(f"Starting search for company {company_name}...")

    company_cik = sec_filing_tool.get_cik(company_name)
    
    if not company_cik:
        return {"Error": f"Unable to retrieve CIK for {company_name}"}

    # Fetch the 10-K filings using the crew process
    sec_analysis_crew.kickoff(inputs={"company_name": company_name, "cik": company_cik})

    # After the crew process, we expect to have both fetched and analyzed the filings
    filings_data = sec_filing_tool.fetch_submissions(company_cik)  # Pass CIK directly
    if "Error" in filings_data:
        return {"Error": filings_data["Error"]}

    ten_k_filings = sec_filing_tool.get_10k_filings(filings_data)
    if not ten_k_filings:
        return {"Error": "No 10-K filings found."}

    # Analyze the filings using the Analysis Agent (optionally extract key data)
    summary_report = f"Company {company_name} has {len(ten_k_filings)} recent 10-K filings."

    # Return the final result
    return {
        "Company Name": company_name,
        "CIK": company_cik,
        "10-K Filings": ten_k_filings,
        "Summary Report": summary_report
    }
