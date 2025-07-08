# Internal Research Agent – Presidio

This guide walks you through setting up your internal research assistant in **Google Colab**, powered by **LangChain**, **FAISS**, and **Ollama** (using local LLMs like LLaMA 2 or Mistral).

Your main logic lives in the `InternalResearchTool.py` script.

---

## Step-by-Step Setup Instructions

### Step 1: Open Google Colab

1.  Go to [colab](https://colab.research.google.com)
2.  Create **"New Notebook"**

---

### Step 2: Install Required Python Packages

Run the following in a Colab code cell:

```bash
!pip install langchain langchain-community pypdf faiss-cpu sentence-transformers
```

These packages include:

*   `langchain`: Core LangChain features
*   `langchain-community`: Integrations (like local LLMs, document loaders, etc.)
*   `pypdf`: PDF reading
*   `faiss-cpu`: Vector similarity search
*   `sentence-transformers`: Embedding models (via HuggingFace)

---

### Step 3: Install and Start Ollama (Local LLM)

**a. Install Ollama**

```bash
!curl -fsSL https://ollama.com/install.sh | sh
```

**b. Start the Ollama Server in the Background**

```python
import subprocess
import time

# Start Ollama server as a background process
process = subprocess.Popen(["ollama", "serve"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
print("Ollama server started in the background.")
time.sleep(5)  # Give the server a moment to initialize
```

**c. Pull an LLM Model (e.g., LLaMA 2 or Mistral)**

```bash
!ollama run mistral
```

Wait for the model to finish downloading. Once the interactive chat begins, type the following command to exit and return to your Colab notebook:

```text
/bye
```

---

### Step 4: Upload Your Documents

**a. Upload HR Policy PDF**

1.  In the Colab sidebar on the left, click the **Files** icon.
4.  Select and upload your `/contents/hr_policy.pdf` file.

You can now reference the file directly by its name in your Python script (e.g., `"hr_policy.pdf"`).

**b. (Optional) Upload a Text File**

You can also upload a `sample_google_doc.txt` to simulate a plain text document.

---

### Step 5: Run the Agent Script

Assuming your agent's logic is saved in a file named `InternalResearchTool.py` (which you can create or upload to Colab), run it with the following command:

```bash
!python InternalResearchTool.py
```

This script should perform the following actions:
1.  Load and process your uploaded documents.
2.  Create vector embeddings and store them in a FAISS index.
3.  Query the vector store with your questions.
4.  Use the local model via Ollama to generate answers based on the retrieved context.

---

### File Structure

Your final Colab session storage should look like this:

```graphql
Your Colab Session
├── InternalResearchTool.py         
├── hr_policy.pdf    
└── sample_google_doc.txt     
```
```