import subprocess
import time
import os
from typing import List, Literal, TypedDict, Annotated
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, END
import functools
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import SentenceTransformerEmbeddings
from langchain_core.documents import Document
from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# print("--- Setting up Ollama in Colab ---")
# !curl -fsSL https://ollama.com/install.sh | sh
# process = subprocess.Popen(["nohup", "ollama", "serve"], stdout=open("ollama.log", "w"), stderr=open("ollama_error.log", "w"), preexec_fn=os.setpgrp)
# print("Ollama server started in background. Waiting for it to be ready...")
# time.sleep(10)
# print("Pulling Ollama model 'llama2'...")
# !ollama pull llama2
# print("Ollama model 'llama2' pulled successfully.")
# print("--- Ollama Setup Complete ---")

llm = ChatOllama(model="llama2", temperature=0)

it_docs = [
    Document(page_content="""
    **VPN Setup Guide:**
    To set up your VPN for remote access, follow these steps:
    1. Download the Cisco AnyConnect VPN client from the IT portal (portal.company.com/vpn).
    2. Install the client.
    3. Open Cisco AnyConnect and enter the server address: `vpn.company.com`.
    4. Use your corporate username (e.g., `jsmith`) and password.
    5. For multi-factor authentication (MFA), approve the login via your authenticator app.
    If you encounter issues, ensure your internet connection is stable and check firewall settings.
    """, metadata={"source": "internal_it_docs", "topic": "VPN"}),
    Document(page_content="""
    **Approved Software Policy:**
    Our company maintains a strict list of approved software to ensure security and compatibility.
    The full list is available on the internal IT portal under 'Software & Tools' -> 'Approved Applications'.
    To request new software not on the list, you must:
    1. Fill out the 'Software Request Form' (available on the IT portal).
    2. Obtain manager approval.
    3. IT Security will review the request for vulnerabilities and licensing compliance.
    Unauthorized software installations are prohibited.
    """, metadata={"source": "internal_it_docs", "topic": "Software"}),
    Document(page_content="""
    **Laptop Request Procedure:**
    Employees are eligible for a new laptop refresh every 3 years.
    To request a new laptop or a replacement due to damage/loss:
    1. Navigate to the IT portal (portal.company.com/hardware).
    2. Fill out the 'Hardware Request Form', specifying your current device and reason for request.
    3. Your manager will receive an approval request.
    4. Once approved, IT will provision a new laptop and arrange for pickup or shipping.
    For urgent requests, contact the IT Help Desk directly after submitting the form.
    """, metadata={"source": "internal_it_docs", "topic": "Hardware"}),
    Document(page_content="""
    **Printer Troubleshooting Guide:**
    If your office printer is not working, try these common solutions:
    1. Check if the printer is powered on and connected to the network (ethernet cable or Wi-Fi).
    2. Ensure there's paper in the tray and no paper jams.
    3. Restart the printer.
    4. Restart your computer.
    5. Check your computer's print queue for stuck jobs.
    If the problem persists, submit an IT ticket via the IT portal, including the printer's model number, location, and any error messages displayed on the printer's screen.
    """, metadata={"source": "internal_it_docs", "topic": "Printer"}),
    Document(page_content="""
    **Password Reset Policy:**
    To reset your corporate password:
    1. Go to `password.company.com`.
    2. Enter your username and follow the prompts for identity verification (MFA required).
    3. If you are locked out or cannot use the self-service portal, contact the IT Help Desk at extension 1234 or email helpdesk@company.com.
    Passwords expire every 90 days and must meet complexity requirements (e.g., 12+ characters, mixed case, numbers, symbols).
    """, metadata={"source": "internal_it_docs", "topic": "Password"}),
    Document(page_content="""
    **Email Configuration for Mobile Devices:**
    To set up your company email on your mobile device (iOS/Android):
    1. Download the Microsoft Outlook app from your device's app store.
    2. Open Outlook and enter your company email address.
    3. You will be redirected to the company's single sign-on (SSO) page.
    4. Enter your corporate credentials and complete any MFA prompts.
    5. Your email should now sync. For issues, ensure your device OS is updated and contact IT if problems persist.
    """, metadata={"source": "internal_it_docs", "topic": "Email"}),
]

finance_docs = [
    Document(page_content="""
    **Employee Reimbursement Policy and Procedure:**
    Employees can seek reimbursement for approved business expenses.
    Procedure:
    1. Access the 'Reimbursement Request Form' on the Finance Portal (finance.company.com/forms).
    2. Fill out all required fields, including expense type, date, amount, and business purpose.
    3. Attach original receipts or clear scanned copies.
    4. Submit the form within 30 calendar days of the expense date.
    5. Reimbursements are processed via direct deposit weekly, typically on Fridays.
    Expenses over $50 require manager approval before submission.
    """, metadata={"source": "internal_finance_docs", "topic": "Reimbursement"}),
    Document(page_content="""
    **Monthly Budget Report Access:**
    All departmental budget reports are stored on the shared network drive.
    To access last month's budget report (e.g., for July 2025):
    1. Navigate to `\\company.local\shared\FinanceReports\2025\Monthly_Budgets`.
    2. Locate the file named `[Department Name]_July_2025_Budget.xlsx`.
    Access is restricted to department heads and finance personnel. Contact the Finance department if you require access or a specific report not found.
    """, metadata={"source": "internal_finance_docs", "topic": "Budget"}),
    Document(page_content="""
    **Payroll Processing Schedule:**
    Payroll is processed bi-monthly.
    - **Mid-Month Payroll:** Processed on the 15th of each month. Funds are typically deposited by the 17th.
    - **End-of-Month Payroll:** Processed on the 30th of each month. Funds are typically deposited by the 2nd of the following month.
    If a processing date falls on a weekend or public holiday, payroll will be processed on the preceding business day.
    For questions regarding your payslip or deductions, contact HR & Payroll at payroll@company.com.
    """, metadata={"source": "internal_finance_docs", "topic": "Payroll"}),
    Document(page_content="""
    **Travel Expense Policy:**
    All business travel expenses must adhere to the company's Travel Policy.
    Key points:
    - All travel must be pre-approved by your manager and department head.
    - Use the Concur system for booking flights and hotels.
    - Per diems are provided for meals; itemized receipts are required for all other expenses over $25.
    - Submit expense reports within 7 days of returning from travel.
    Refer to the full 'Travel Policy' document on the Finance Portal for detailed guidelines.
    """, metadata={"source": "internal_finance_docs", "topic": "Travel Expenses"}),
    Document(page_content="""
    **Invoice Payment Process:**
    To process an invoice for payment:
    1. Ensure the invoice is addressed to the company and includes a valid Purchase Order (PO) number.
    2. Forward the invoice to accounts.payable@company.com.
    3. The Accounts Payable team will verify the PO and process the payment within 30 days of receipt.
    For urgent payments, mark the email as 'URGENT' and provide a justification.
    """, metadata={"source": "internal_finance_docs", "topic": "Invoicing"}),
    Document(page_content="""
    **Annual Financial Audit Information:**
    Our company undergoes an annual financial audit typically in Q1 (January-March).
    The audit covers all financial transactions, statements, and internal controls for the previous fiscal year.
    Departments may be contacted by the audit team for specific documentation or clarifications.
    All financial records must be maintained in accordance with retention policies.
    """, metadata={"source": "internal_finance_docs", "topic": "Audit"}),
]

embeddings = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
it_vectorstore = FAISS.from_documents(it_docs, embeddings)
finance_vectorstore = FAISS.from_documents(finance_docs, embeddings)

@tool
def read_file(query: str, domain: Literal["IT", "Finance"]) -> str:
    print(f"\n--- Tool Used: ReadFile ---")
    print(f"Searching internal docs for: '{query}' in {domain} domain.")
    if domain == "IT":
        retriever = it_vectorstore.as_retriever(search_kwargs={"k": 1})
    elif domain == "Finance":
        retriever = finance_vectorstore.as_retriever(search_kwargs={"k": 1})
    else:
        return "Invalid domain specified for ReadFile tool."
    relevant_docs = retriever.invoke(query)
    if relevant_docs:
        return f"Internal Doc (from {relevant_docs[0].metadata.get('source', 'unknown')}): {relevant_docs[0].page_content}"
    else:
        return f"No relevant internal document found for '{query}' in {domain} domain."

@tool
def web_search(query: str) -> str:
    print(f"\n--- Tool Used: WebSearch ---")
    print(f"Searching the web for: '{query}'")
    if "vpn setup" in query.lower():
        return "External Web Result: Generic VPN setup guides often involve network settings and server addresses."
    elif "software approval process" in query.lower():
        return "External Web Result: General software approval processes in companies involve IT review and licensing."
    elif "reimbursement process" in query.lower():
        return "External Web Result: Standard reimbursement processes require submitting expenses with proof of purchase."
    elif "payroll processing dates" in query.lower():
        return "External Web Result: Payroll dates vary by company, often bi-weekly or monthly."
    else:
        return f"No relevant web search results found for '{query}'."

tools = [read_file, web_search]

class AgentState(TypedDict):
    user_query: str
    next_agent: Literal["IT", "Finance", "Supervisor"]
    response: str
    messages: Annotated[List[BaseMessage], lambda x, y: x + y]

def supervisor_agent(state: AgentState) -> AgentState:
    user_query = state["user_query"]
    print(f"\n--- Supervisor Agent: Classifying Query with Ollama ---")
    print(f"Query: '{user_query}'")
    classification_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. Classify the following user query as either 'IT' or 'Finance'. Respond with only 'IT' or 'Finance'."),
        ("user", "{query}")
    ])
    classification_chain = classification_prompt | llm | StrOutputParser()
    raw_classification = classification_chain.invoke({"query": user_query})
    next_agent = raw_classification.strip().upper()
    if next_agent not in ["IT", "FINANCE"]:
        print(f"Warning: Ollama returned unrecognised classification '{next_agent}'. Defaulting to IT.")
        next_agent = "IT"
    print(f"Classified as: {next_agent} Query.")
    return {"next_agent": next_agent, "messages": [HumanMessage(content=f"Supervisor classified query as {next_agent}.")]}

def run_tool_calling_agent(state: AgentState, domain_tools: List[tool], domain_name: str) -> AgentState:
    user_query = state["user_query"]
    print(f"\n--- {domain_name} Agent: Processing Query with Ollama and Tools ---")
    print(f"Query: '{user_query}'")
    tool_decision_prompt = ChatPromptTemplate.from_messages([
        ("system", f"You are a helpful {domain_name} support agent. Based on the user's query, decide whether to use 'read_file' (for internal documents) or 'web_search' (for external information). If neither is suitable, just answer directly. Respond with 'USE_READ_FILE', 'USE_WEB_SEARCH', or your direct answer."),
        ("user", "{query}")
    ])
    tool_decision_chain = tool_decision_prompt | llm | StrOutputParser()
    decision = tool_decision_chain.invoke({"query": user_query}).strip().upper()
    response_content = ""
    tool_output = None
    if "USE_READ_FILE" in decision:
        print(f"LLM decided to use read_file.")
        tool_output = read_file(user_query, domain_name)
    elif "USE_WEB_SEARCH" in decision:
        print(f"LLM decided to use web_search.")
        tool_output = web_search(user_query)
    else:
        response_content = decision
    if tool_output:
        final_response_prompt = ChatPromptTemplate.from_messages([
            ("system", f"You are a helpful {domain_name} support agent. Based on the following tool output, formulate a concise and helpful answer to the user's original query: '{user_query}'"),
            HumanMessage(content=f"Tool Output: {tool_output}\nOriginal Query: {user_query}")
        ])
        response_content = (final_response_prompt | llm | StrOutputParser()).invoke({})
    elif not response_content:
        response_content = "I'm sorry, I couldn't process your request with the available tools or information."
    print(f"{domain_name} Agent Response: {response_content}")
    return {"response": response_content, "messages": [HumanMessage(content=f"{domain_name} Agent handled: {response_content}")]}

def it_agent(state: AgentState) -> AgentState:
    return run_tool_calling_agent(state, [functools.partial(read_file, domain="IT"), web_search], "IT")

def finance_agent(state: AgentState) -> AgentState:
    return run_tool_calling_agent(state, [functools.partial(read_file, domain="Finance"), web_search], "Finance")

workflow = StateGraph(AgentState)
workflow.add_node("supervisor", supervisor_agent)
workflow.add_node("it_agent", it_agent)
workflow.add_node("finance_agent", finance_agent)
workflow.set_entry_point("supervisor")

def router(state: AgentState) -> Literal["it_agent", "finance_agent"]:
    if state["next_agent"] == "IT":
        return "it_agent"
    elif state["next_agent"] == "FINANCE":
        return "finance_agent"
    else:
        print(f"Error: Unexpected next_agent value from supervisor: {state['next_agent']}. Defaulting to IT agent.")
        return "it_agent"

workflow.add_conditional_edges(
    "supervisor",
    router,
    {
        "it_agent": "it_agent",
        "finance_agent": "finance_agent",
    },
)

workflow.add_edge("it_agent", END)
workflow.add_edge("finance_agent", END)
app = workflow.compile()

print("--- Multi-Agent Support System with Ollama (Interactive) ---")
print("Type your query. Type 'exit' or 'quit' to end the session.")

while True:
    user_input = input("\nYour Query: ")
    if user_input.lower() in ["exit", "quit"]:
        print("Exiting session. Goodbye!")
        break
    try:
        result = app.invoke({"user_query": user_input, "messages": []})
        print(f"\nFinal Response: {result['response']}")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please try your query again or restart the Colab runtime if the Ollama server has stopped.")
print("-" * 50)
