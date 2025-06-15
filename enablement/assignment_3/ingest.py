from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import os



# Load model for embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define the persistence directory
PERSIST_DIRECTORY = "./chroma_db"

# Ensure the persistence directory exists
if not os.path.exists(PERSIST_DIRECTORY):
    os.makedirs(PERSIST_DIRECTORY)
    print(f"Created persistence directory: {PERSIST_DIRECTORY}")

# Initialize ChromaDB client
chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

# Get or create the collection
collection = chroma_client.get_or_create_collection(name="docs")

def get_embedding(text: str):
    """
    Generates an embedding for the given text.
    """
    return model.encode(text).tolist()

# Define the path to your data file
DATA_FILE_PATH = "data/docs.txt"

# Ensure the data directory and file exist (optional, but good practice)
if not os.path.exists("data"):
    print("Error: 'data' directory not found. Please create it and place 'docs.txt' inside.")
    exit()

if not os.path.exists(DATA_FILE_PATH):
    print(f"Error: '{DATA_FILE_PATH}' not found. Please create this file with your documents.")
    exit()

# Read documents from the file and process them
try:
    with open(DATA_FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    # Prepare lists for batch addition
    documents_to_add = []
    embeddings_to_add = []
    ids_to_add = []

    for i, text in enumerate(lines):
        stripped_text = text.strip()
        if stripped_text:  # Process only non-empty lines
            embedding = get_embedding(stripped_text)
            documents_to_add.append(stripped_text)
            embeddings_to_add.append(embedding)
            ids_to_add.append(f"doc-{i}")

    # Add documents in a batch for better performance
    if documents_to_add:
        collection.add(
            documents=documents_to_add,
            embeddings=embeddings_to_add,
            ids=ids_to_add
        )
        print(f"Added {len(documents_to_add)} documents to Chroma.")
    else:
        print("No documents found in 'docs.txt' to embed.")

    print("Documents embedded and stored in Chroma.")

except FileNotFoundError:
    print(f"Error: The file '{DATA_FILE_PATH}' was not found.")
except Exception as e:
    print(f"An unexpected error occurred: {e}")