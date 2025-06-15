
# RAG Chatbot (Chroma + Hugging Face + Azure OpenAI)

  

A simple Retrieval-Augmented Generation (RAG) chatbot that:

  

- Generates embeddings locally using Hugging Face

- Stores and queries those embeddings using Chroma (local vector DB)

- Uses Azure OpenAI (e.g. GPT-4o) to generate answers using retrieved context

  

No LangChain. No external databases. Fully customizable.

  

---

  

## 📁 Project Structure

rag-chatbot/

├── data/

│ └── docs.txt # Text knowledge base

├── ingest.py # Embeds and stores in Chroma

├── chatbot.py # Chat with GPT + context

├── .env # Azure OpenAI credentials

├── chroma_db/ # Auto-generated vector store

└── README.md

  
  

## How to Run the Project

  

###  Step 1: Install Python Dependencies

    pip install -r requirements.txt

  
  

### Step 2: Add data.txt

Populate `docs.txt` with the text information you want your chatbot to learn from

### Step 3: Run the embedding script

    python ingest.py

  

### Step 4: Run the chatbot script

    python chatbot.py

