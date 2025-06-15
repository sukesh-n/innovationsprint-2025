from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import openai
from openai import AzureOpenAI
from openai import APIStatusError, APIConnectionError, AuthenticationError 
import os
from dotenv import load_dotenv


load_dotenv()
AZURE_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_API_VERSION = os.getenv("AZURE_OPENAI_API_VERSION")
CHAT_DEPLOYMENT = os.getenv("AZURE_OPENAI_DEPLOYMENT_CHAT")

# Check env
if not all([AZURE_API_KEY, AZURE_ENDPOINT, CHAT_DEPLOYMENT]):
    print("Error: Please set AZURE_OPENAI_API_KEY, AZURE_OPENAI_ENDPOINT, and AZURE_OPENAI_DEPLOYMENT_CHAT environment variables.")
    exit()

# AzureOpenAI Init
try:
    client = AzureOpenAI(
        api_key=AZURE_API_KEY,
        azure_endpoint=AZURE_ENDPOINT,
        api_version=AZURE_API_VERSION
    )
    print("Azure OpenAI client initialized.")
except Exception as e:
    print(f"Error initializing Azure OpenAI client: {e}")
    exit()


# Load Embedding Model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Load Chroma
PERSIST_DIRECTORY = "./chroma_db"
try:
    chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)
    collection = chroma_client.get_collection(name="docs")
    print(f"✅ Successfully connected to ChromaDB collection 'docs' at {PERSIST_DIRECTORY}.")
except Exception as e:
    print(f"Error connecting to ChromaDB: {e}")
    print("Please ensure your ingestion script has been run and 'docs' collection exists.")
    exit()

# Embedding Function
def get_embedding(text: str):
    """
    Generates an embedding for the given text using the loaded SentenceTransformer model.
    """
    return model.encode(text).tolist()

# Context Retrieval Function
def get_context(query: str, top_k=3) -> str:
    """
    Retrieves relevant document snippets from ChromaDB based on the query.
    """
    query_embedding = get_embedding(query)
    try:
        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        if results and 'documents' in results and results['documents'] and results['documents'][0]:
            return "\n".join(results['documents'][0])
        else:
            print("Warning: No relevant documents found in ChromaDB for the query.")
            return "No relevant context found."
    except Exception as e:
        print(f"Error during ChromaDB context retrieval: {e}")
        return "Error retrieving context."

# Answer Generation Function using Azure OpenAI
def generate_answer(query: str, context: str) -> str:
    """
    Generates an answer to the query using the provided context and Azure OpenAI.
    """
    if not context or context == "No relevant context found." or context == "Error retrieving context.":
        prompt_content = f"""You are a helpful assistant.
Question: {query}
Answer: (Note: No specific context was available. Please answer based on general knowledge if possible, or state if you cannot answer without more information.)
"""
    else:
        prompt_content = f"""You are a helpful assistant. Please use the following context to answer the question. If the answer is not available in the context, clearly state that you cannot answer based on the provided information.

Context:
{context}

Question: {query}
Answer:"""

    try:
        response = client.chat.completions.create(
            model=CHAT_DEPLOYMENT,
            messages=[{"role": "user", "content": prompt_content}],
            temperature=0.2,
            max_tokens=300
        )
        return response.choices[0].message.content.strip() 
    except APIStatusError as e:
        print(f"Azure OpenAI API Status Error (Code: {e.status_code}): {e.response}")
        return "Sorry, I'm having trouble generating an answer right now due to an API error."
    except APIConnectionError as e: 
        print(f"Azure OpenAI API Connection Error: {e}")
        return "Sorry, I'm having trouble connecting to the OpenAI service."
    except AuthenticationError as e:
        print(f"Azure OpenAI Authentication Error: {e}")
        return "Sorry, there's an authentication issue with the OpenAI service. Please check your API key."
    except Exception as e:
        print(f"An unexpected error occurred during answer generation: {e}")
        return "An internal error occurred while generating the answer."

# Main Chatbot Loop
if __name__ == "__main__":
    print("Welcome to the RAG Chatbot!")
    print("Type 'exit' or 'quit' to end the session.")

    while True:
        question = input("\nAsk a question: ")
        if question.lower() in ['exit', 'quit']:
            print("Goodbye!")
            break

        print("Searching for context...")
        context = get_context(question)

        print("Generating answer...")
        answer = generate_answer(question, context)
        print("\n🧠 Answer:", answer)