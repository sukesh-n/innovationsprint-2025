import os
from langchain_community.llms import Ollama
from langchain_community.chat_models import ChatOllama
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain.tools import Tool
from langchain.agents import AgentExecutor, create_react_agent
from langchain import hub
from langchain_core.prompts import PromptTemplate

# --- Configuration ---
# Path to your HR policy PDF document
HR_POLICY_PDF_PATH = "hr_policy.pdf"
# Path to your simulated Google Doc content
SAMPLE_GOOGLE_DOC_PATH = "sample_google_doc.txt"
# Ollama model name (ensure you have pulled this model using 'ollama run <model_name>')
OLLAMA_MODEL = "mistral" # Or "mistral", "phi3", etc.

# --- 1. Initialize Local LLM (Ollama) ---
# We'll use ChatOllama for conversational capabilities.
# Ensure Ollama is running and the specified model is pulled.
try:
    llm = ChatOllama(model=OLLAMA_MODEL)
    print(f"Successfully connected to Ollama with model: {OLLAMA_MODEL}")
except Exception as e:
    print(f"Error connecting to Ollama: {e}")
    print("Please ensure Ollama is installed and running, and the model "
          f"'{OLLAMA_MODEL}' is pulled (e.g., 'ollama run {OLLAMA_MODEL}' in your terminal).")
    exit()

# --- 2. Initialize Local Embedding Model ---
# This model will run locally to convert text into numerical vectors.
# 'sentence-transformers/all-MiniLM-L6-v2' is a good general-purpose model.
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
print("HuggingFaceEmbeddings initialized.")

# --- 3. RAG Tool: HR Policy Documents ---

# Function to load and vectorize HR policy documents
def setup_hr_rag_tool():
    """
    Loads the HR policy PDF, splits it into chunks, creates embeddings,
    and sets up a FAISS vector store for retrieval.
    """
    if not os.path.exists(HR_POLICY_PDF_PATH):
        print(f"Error: HR Policy PDF not found at {HR_POLICY_PDF_PATH}.")
        print("Please ensure 'hr_policy.pdf' is in the same directory as this script.")
        return None

    print(f"Loading HR Policy document from {HR_POLICY_PDF_PATH}...")
    loader = PyPDFLoader(HR_POLICY_PDF_PATH)
    documents = loader.load()
    print(f"Loaded {len(documents)} pages from HR Policy PDF.")

    # Split documents into smaller, manageable chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
        is_separator_regex=False,
    )
    texts = text_splitter.split_documents(documents)
    print(f"Split HR Policy into {len(texts)} text chunks.")

    # Create a FAISS vector store from the document chunks and embeddings
    print("Creating FAISS vector store for HR Policy documents...")
    vectorstore = FAISS.from_documents(texts, embeddings)
    print("FAISS vector store created.")
    return vectorstore

hr_vectorstore = setup_hr_rag_tool()

# Define the RAG tool function
def hr_policy_rag_tool(query: str) -> str:
    """
    Searches the HR policy documents for relevant information based on the query.
    """
    if hr_vectorstore is None:
        return "HR policy documents are not available. Please check the PDF path and setup."

    print(f"Searching HR Policy documents for: '{query}'")
    # Perform a similarity search in the vector store
    docs = hr_vectorstore.similarity_search(query, k=3) # Retrieve top 3 relevant documents
    if not docs:
        return "No relevant HR policy information found for your query."

    # Concatenate the content of the retrieved documents
    context = "\n\n".join([doc.page_content for doc in docs])

    # Use the LLM to generate a coherent answer based on the retrieved context
    prompt_template = PromptTemplate.from_template(
        """You are an HR policy assistant. Use the following context to answer the question.
        If the answer is not in the context, state that you don't have enough information.

        Context:
        {context}

        Question: {question}

        Answer:"""
    )
    chain = prompt_template | llm
    response = chain.invoke({"context": context, "question": query})
    return response.content

# --- 4. MCP Tool: Simulated Google Docs for Insurance Queries ---

# Function to read content from the simulated Google Doc file
def read_simulated_google_doc(file_path: str) -> str:
    """Reads content from a local text file simulating a Google Doc."""
    if not os.path.exists(file_path):
        print(f"Error: Simulated Google Doc file not found at {file_path}.")
        print(f"Please create '{file_path}' with sample insurance content.")
        return "Simulated Google Doc content not available."
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return content
    except Exception as e:
        return f"Error reading simulated Google Doc: {e}"

# Define the MCP tool function
def mcp_tool(query: str) -> str:
    """
    Simulates connecting to Google Docs to answer insurance-related queries.
    Reads from a local text file containing sample insurance policy information.
    """
    print(f"Simulating MCP Tool access for insurance query: '{query}'")
    insurance_content = read_simulated_google_doc(SAMPLE_GOOGLE_DOC_PATH)

    # Use the LLM to extract relevant information from the simulated doc content
    # or summarize based on the query.
    prompt_template = PromptTemplate.from_template(
        """You are an insurance policy expert. Use the following insurance policy details
        to answer the user's question. If the answer is not directly available,
        explain why or state that the information is not present in the provided policy.

        Insurance Policy Details:
        {policy_details}

        Question: {question}

        Answer:"""
    )
    chain = prompt_template | llm
    response = chain.invoke({"policy_details": insurance_content, "question": query})
    return response.content

# --- 5. Web Search Tool: Placeholder ---

# Define the placeholder Web Search tool function
def web_search_tool(query: str) -> str:
    """
    Placeholder for a web search tool. In a real scenario, this would
    integrate with a search engine API (e.g., Google Search, SerpAPI).
    """
    print(f"Executing placeholder Web Search for: '{query}'")
    return (f"This is a placeholder for a web search result for '{query}'.\n"
            "To get real-time industry benchmarks, trends, or regulatory updates, "
            "you would need to integrate with a web search API (e.g., Google Search API, SerpAPI, DuckDuckGo Search API).")

# --- 6. Define Tools for the Agent ---
tools = [
    Tool(
        name="HR_Policy_RAG_Tool",
        func=hr_policy_rag_tool,
        description="Useful for answering questions about internal HR policies, employee benefits, company guidelines, and any human resources related queries. Input should be a clear question about HR policies."
    ),
    Tool(
        name="MCP_Insurance_Tool",
        func=mcp_tool,
        description="Useful for answering questions about Presidio's insurance policies, coverage details, deductibles, claim procedures, and related insurance information. Input should be a clear question about insurance."
    ),
    Tool(
        name="Web_Search_Placeholder_Tool",
        func=web_search_tool,
        description="Useful for finding general information, industry benchmarks, market trends, or regulatory updates that are not available in internal documents. This is currently a placeholder and does not perform live searches."
    )
]

# --- 7. Create the Agent ---
# Get the prompt for the ReAct agent
prompt = hub.pull("hwchase17/react")

# Create the agent
agent = create_react_agent(llm, tools, prompt)
print("LangChain ReAct Agent created.")

# --- 8. Create Agent Executor ---
agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True, handle_parsing_errors=True)
print("Agent Executor ready. You can now start querying the agent.")

# --- 9. Interaction Loop ---
if __name__ == "__main__":
    print("\n--- Presidio Internal Research Agent ---")
    print("Type 'exit' or 'quit' to end the session.")
    print("Try queries like:")
    print("- 'What is the policy on sick leave?' (HR Policy)")
    print("- 'Summarize the deductible for insurance claims.' (Insurance Policy)")
    print("- 'What are the current trends in AI data handling regulations?' (Web Search Placeholder)")
    print("-----------------------------------\n")

    while True:
        query = input("Your query or to end chat enter 'exit' or 'quit': ")
        if query.lower() in ["exit", "quit"]:
            print("Exiting agent. Goodbye!")
            break
        
        try:
            # Invoke the agent with the user's query
            response = agent_executor.invoke({"input": query})
            print("\nAgent Response:")
            print(response["output"])
            print("\n" + "="*50 + "\n")
        except Exception as e:
            print(f"\nAn error occurred during agent execution: {e}")
            print("Please check the console for detailed error messages and ensure all setup steps are complete.")
            print("\n" + "="*50 + "\n")