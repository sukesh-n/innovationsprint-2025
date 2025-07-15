# Multi-Agent Support System with LangGraph and Ollama (Colab)

This project implements a multi-agent support system using LangGraph, designed to classify user queries and route them to specialized IT or Finance agents. Each agent is equipped with tools to retrieve information from internal documents (simulated with vectorized data) or perform web searches (simulated). The system integrates with Ollama, allowing you to run powerful language models directly within your Google Colab environment.

## Project Structure

The system consists of three main agents:

### Supervisor Agent:
*   **Purpose**: Classifies incoming user queries as either "IT" or "Finance".
*   **Action**: Routes the query to the appropriate specialist agent based on its classification.
*   **LLM Integration**: Uses an Ollama model for query classification.

### IT Agent:
*   **Purpose**: Handles all IT-related queries.
*   **Tools**:
    *   `ReadFile`: Simulates reading internal IT documentation. It performs a similarity search against a vectorized knowledge base of IT documents.
    *   `WebSearch`: Simulates searching external sources for general IT information.
*   **LLM Integration**: Uses an Ollama model to decide which tool to use and to formulate a response based on tool output or direct answer.

### Finance Agent:
*   **Purpose**: Handles all Finance-related queries.
*   **Tools**:
    *   `ReadFile`: Simulates reading internal finance documentation. It performs a similarity search against a vectorized knowledge base of finance documents.
    *   `WebSearch`: Simulates searching public finance data or general finance information.
*   **LLM Integration**: Uses an Ollama model to decide which tool to use and to formulate a response based on tool output or direct answer.

## Features
*   **Query Classification**: Automatically directs queries to the correct domain expert.
*   **Contextual Information Retrieval**: Utilizes vectorized sample documents for relevant internal information.
*   **External Search Simulation**: Can simulate fetching information from the web.
*   **Ollama Integration**: Runs language models locally within the Colab environment for privacy and control.
*   **Interactive Interface**: Allows users to ask questions directly in the console.

## Setup and Installation (Google Colab)

To run this system in Google Colab, follow these steps:

1.  Open a new Google Colab notebook.
2.  Copy and paste the entire code from the provided Python script into a code cell.
3.  Run the code cell. The script will automatically handle the following:
    *   Install necessary Python libraries (`langchain-community`, `langchain-core`, `langgraph`, `sentence-transformers`, `faiss-cpu`, `ollama`).
    *   Download and install the Ollama server within the Colab environment.
    *   Start the Ollama server in the background.
    *   Pull the `llama2` model (default) from Ollama. You can modify `llm = ChatOllama(model="llama2", temperature=0)` to use a different model if desired, but ensure it's pulled first.

> **Note**: The Ollama setup and model pulling can take a few minutes, depending on the Colab instance's resources and network speed.

## How to Use

Once the setup is complete and the code cell has finished executing, you will see the following prompt in your Colab output:

```
--- Multi-Agent Support System with Ollama (Interactive) ---
Type your query. Type 'exit' or 'quit' to end the session.

Your Query:
```

You can now type your questions at the `Your Query:` prompt.

### Example Queries:

*   **IT Queries**:
    *   How do I set up VPN for remote access?
    *   Is Microsoft Teams approved software for use?
    *   I need a new laptop, what's the procedure?
    *   My printer is not working, what should I do?
    *   How do I reset my password?
    *   Configure email on my phone.

*   **Finance Queries**:
    *   What is the process for filing a reimbursement?
    *   Where can I find the budget report for last month?
    *   When is payroll processed this month?
    *   How do I submit my travel expenses?
    *   What is the invoice payment process?
    *   Tell me about the annual financial audit.

*   **General Queries (will likely use WebSearch fallback)**:
    *   What is the capital of France?
    *   Tell me about the latest AI trends.

To end the interactive session, type `exit` or `quit` and press Enter.

## Troubleshooting

*   **`'str' object has no attribute 'parent_run_id'` or similar errors**: This typically means a string is being treated as a LangChain message object where it shouldn't be. The provided code has attempted to address this by explicitly wrapping tool outputs in `HumanMessage`. If it persists, ensure your `langchain-core` and `langchain-community` libraries are up to date.
*   **Ollama server issues**: If the Ollama server stops or fails to start, you might see connection errors. Try restarting the Colab runtime and running the cell again. Check the `ollama.log` and `ollama_error.log` files (which are created in the Colab environment) for more details on Ollama's status.
*   **Model not found**: Ensure `!ollama pull llama2` successfully completed. If you change the model name, make sure you've pulled that specific model.

## Customization

*   **Add more documents**: Expand `it_docs` and `finance_docs` with more detailed and diverse content to improve the `ReadFile` tool's effectiveness.
*   **Integrate real tools**: Replace the dummy `read_file` and `web_search` functions with actual API calls to internal document management systems (e.g., Google Drive, SharePoint, Confluence API) and external search engines (e.g., Tavily API, Google Search API).
*   **Refine LLM prompts**: Adjust the `ChatPromptTemplate` instances for the supervisor and specialist agents to fine-tune their behavior and decision-making.
*   **Change Ollama model**: Experiment with different Ollama models (e.g., `mistral`, `gemma`) by changing the model parameter in `ChatOllama`.
*   **Add more agents**: Extend the workflow to include more specialized agents for other domains (e.g., HR, Legal).