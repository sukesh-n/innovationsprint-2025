import os
import csv
import json
from dotenv import load_dotenv

from langsmith import Client
from langchain.smith import run_on_dataset, RunEvalConfig
from langchain_google_genai import ChatGoogleGenerativeAI # <-- ADD THIS IMPORT

# Import the necessary components from your agent code
from agent_with_guardrails import rails, tools

# --- 1. SETUP ---
load_dotenv()
client = Client()
# Using a new version name to ensure a completely fresh start
dataset_name = "Agent Guardrails Eval - CSV-Final" 

# --- 2. CREATE AND POPULATE DATASET ---
try:
    dataset = client.create_dataset(
        dataset_name=dataset_name, 
        description="Evaluation dataset (from CSV) for Agent with Tools and Guardrails."
    )
    print(f"Created new dataset: '{dataset_name}'.")
except Exception:
    dataset = client.read_dataset(dataset_name=dataset_name)
    print(f"Dataset '{dataset_name}' already exists. Clearing old examples to re-populate.")
    for example in client.list_examples(dataset_name=dataset_name):
        client.delete_example(example.id)

print("Reading CSV and uploading examples one by one...")
with open("evaluation_dataset.csv", mode='r', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        expected_tool_calls_str = row.get("expected_tool_calls")
        tool_calls = json.loads(expected_tool_calls_str) if expected_tool_calls_str else None
        client.create_example(
            inputs={"input": row["input"]},
            outputs={"output": row["output"], "expected_tool_calls": tool_calls},
            dataset_id=dataset.id
        )
print("Upload complete. Dataset is ready.")

# --- 3. DEFINE THE AGENT WRAPPER ---
async def agent_predictor(inputs: dict) -> dict:
    """A wrapper for the NeMo Guardrails chain to be used in evaluation."""
    response = await rails.generate_async(prompt=inputs["input"])
    return {"output": response}

# --- 4. CONFIGURE AND RUN EVALUATION ---

# Create an LLM instance specifically for the evaluation
# This tells LangSmith which model to use for judging the results
eval_llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash-latest", temperature=0) # <-- CREATE THE EVALUATOR'S LLM

# Pass the LLM to the evaluation config
evaluation_config = RunEvalConfig(
    evaluators=["trajectory"],
    eval_llm=eval_llm # <-- PASS THE LLM HERE
)

print("--- Starting Evaluation Run on LangSmith ---")

run = run_on_dataset(
    client=client,
    dataset_name=dataset_name,
    llm_or_chain_factory=agent_predictor,
    evaluation=evaluation_config,
    project_name="agent-guardrails-eval-run-csv-final",
    concurrency_level=1,
)

print("--- Evaluation Complete ---")
print(f"View results in LangSmith at: {run.url}")