from crewai import Agent, Task, Crew, Process
from sec_filing_tool import SecFilingTool

# Initialize SEC Filing Tool
sec_tool = SecFilingTool

# Agent: Financial Analyst
financial_analyst = Agent(
    role='Financial Analyst',
    goal='Analyze financial metrics from the SEC 10-K filings for {company}',
    verbose=True,
    memory=True,
    backstory="You have deep expertise in financial statements and can identify trends.",
    tools=[sec_tool]
)

# Task: Retrieve Financial Data
retrieve_financial_data_task = Task(
    description="Retrieve financial metrics such as revenue, net income, assets, and liabilities from the 10-K filings.",
    expected_output="Structured financial data in a table format.",
    tools=[sec_tool],
    agent=financial_analyst
)

# Create the Crew
financial_analysis_crew = Crew(
    agents=[financial_analyst],
    tasks=[retrieve_financial_data_task],
    process=Process.sequential
)

def analyze_company(company_name):
    # Inputs passed to the Crew for dynamic interaction
    result = financial_analysis_crew.kickoff(inputs={'company': company_name})
    return result
