# Smart Gmail Agent — n8n Workflow Guide

This guide provides a comprehensive walkthrough for setting up and running the **Smart Gmail Agent** workflow in **n8n**. It assumes you’ve already cloned the project repository and have access to the `Smart_Gmail_Agent.json` workflow file.

---

## Workflow Overview

The **Smart Gmail Agent** workflow automates the initial triage of incoming support and administrative queries. It simulates:

- Classifying requests.
- Identifying the correct internal team.
- Dispatching tailored email notifications.

This demonstrates how **n8n** can function as an intelligent routing system for business communications.

### Workflow Sequence

1. Fetch a list of internal users and their roles from a sample API.
2. Simulate two distinct queries:
   - A customer billing question.
   - An urgent technical issue.
3. Classify each query using keyword analysis.
4. Route each query based on its assigned role.
5. Filter the user list to match relevant roles.
6. Send personalized email notifications to matching users.

---

## Prerequisites

Before starting, ensure you have:

- A running **n8n** instance (n8n.cloud or self-hosted).
- The `Smart_Gmail_Agent.json` workflow file.
- **SMTP credentials** for sending emails (e.g., Gmail, Outlook, SendGrid).

> **Important for Gmail Users**  
> Use an [App Password](https://support.google.com/accounts/answer/185833) with n8n instead of your standard Google password.

---

## Setup Instructions

### Step 1: Import the Workflow

1. Open your n8n dashboard.
2. Click **New** to create a blank workflow.
3. Click **Import from File** (top-right).
4. Select the `Smart_Gmail_Agent.json` file. The workflow will appear on the canvas.

---

### Step 2: Configure SMTP Credentials

1. In the left-hand sidebar, go to **Credentials**.
2. Click **Add Credential** → Select **SMTP**.
3. Enter your SMTP server details:
   - Host  
   - Port  
   - User  
   - Password  
4. Click **Save** and give it a name (e.g., `My Company SMTP`).

5. Back in the canvas:
   - Click on both **Send email** nodes (`Send email`, `Send email1`).
   - Assign the SMTP credential you just created.

---

### Step 3: Configure Email Recipients & Run the Workflow

> **Test Run Safety Note**  
> The email nodes use static email addresses to avoid accidentally spamming real people. For testing, update the **To Email** field to your own address.

- In each **Send email** node, replace the static address with **your own email**.
- In production, use dynamic expressions like `={{ $json.email }}`.

Then:

1. Click **Save**.
2. Click **Execute Workflow**.

---

## Expected Result

After running the workflow:

- The workflow nodes will light up green.
- You should receive two emails in your inbox:

### 1. Customer Query Email

- **Subject:** `New customer Query`  
- **Body:** A confirmation about a billing issue.

### 2. Admin Query Email

- **Subject:** `New admin Query`  
- **Body:** An alert about a technical API issue.

---

## Workflow Logic (Node-by-Node)

### 1. Get Users (`HTTP Request`)

- **Purpose:** Fetch a directory of internal users.
- **How:** Pulls sample users (name, email, role) from a public API.

---

### 2. Set Query (`Set`)

- **Purpose:** Simulate incoming support requests.
- **How:** Provides two static queries (one customer, one admin).  
  > In production, this would be replaced by an email or ticket trigger.

---

### 3. Classify Query (`Code`)

- **Purpose:** Assign a role to each query.
- **How:** Uses keyword lists (`customerKeywords`, `adminKeywords`) to analyze the text and classify the query as either `customer` or `admin`.

---

### 4. Loop Over Items (`Split In Batches`)

- **Purpose:** Process each query individually.
- **How:** Sends each classified query through the workflow in sequence.

---

### 5. If-customer / If-admin (`IF`)

- **Purpose:** Route based on classification.
- **How:** 
  - If-customer: Checks if role is `customer`.
  - If-admin: Checks if role is `admin`.

---

### 6. Filter Users by Role / Filter Users by Role1 (`Code`)

- **Purpose:** Identify the team members for notification.
- **How:** Filters users from "Get Users" node to match the query role.

---

### 7. Send email / Send email1 (`Send Email`)

- **Purpose:** Send the final email notifications.
- **How:** 
  - Loops through filtered users.
  - Sends a customized email using expressions like `{{ $json.name }}`.

---

## In Actual Use

To ensure how the workflow works:

- Replace static email addresses with dynamic ones:
  ```n8n
  {{ $json.email }}
