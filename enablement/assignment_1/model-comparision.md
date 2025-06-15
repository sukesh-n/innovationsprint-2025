# AI Model Comparison for DevOps Department

This document compares four AI models — GPT-4o, Claude Sonnet, Gemini Flash, and DeepSeek-R1:7B (via Ollama) — specifically focusing on DevOps use cases. It evaluates Infrastructure Automation, Ease of Use, and Speed/Latency. DeepSeek-R1:7B is noted for local use with an open UI interface.

---

## Comparison Table

| **Model**                | **Infrastructure Automation** | **Ease of Use** | **Speed / Latency** | **Comments** |
|--------------------------|-------------------------------|------------------|----------------------|--------------|
| **GPT-4o**               | Good                          | Excellent        | Good                 | Strong in Bash, Python, YAML, and PowerShell scripts. Sometimes verbose or overly generic. Prompt used: “Write a Bash script to archive logs and restart nginx if down.” |
| **Claude Sonnet**        | Good                          | Excellent        | Good                 | Excels at multi-step workflows and structured IaC. Great with GitHub Actions, Docker Compose. Prompt: “GitHub Actions workflow for Terraform with Slack alerts.” |
| **Gemini Flash**         | Good                          | Excellent        | Excellent            | Fastest response time. Best for CI/CD tasks, short automation snippets, and PR comments. Lacks full-depth reasoning for complex pipelines. |
| **DeepSeek-R1:7B (Ollama)** | Basic or Limited Support     | Good             | Good                 | Used locally with open UI via Ollama — enabling private, interactive script generation and experimentation. Well suited for simple shell commands and quick DevOps snippets but limited in complex workflow memory. Prompt: “Shell script for disk space monitoring with alert if >80%.” |

---

## Summary

| Model                 | Best For                                           | Considerations                                      |
|----------------------|----------------------------------------------------|-----------------------------------------------------|
| **GPT-4o**            | General-purpose scripting and YAML automation     | Sometimes verbose or generic                        |
| **Claude Sonnet**     | Orchestrated workflows and structured IaC         | Precise and modular; may over-explain               |
| **Gemini Flash**      | CI/CD pipelines and automation doc generation     | Super fast; less context-aware in long tasks        |
| **DeepSeek-R1:7B**    | Local/offline CLI and shell command generation with open UI | Limited reasoning; ideal for privacy-conscious users and rapid local testing |

---

## Evaluation Notes

- **Environment**: Bash, YAML, Terraform, CI/CD (GitHub Actions), SQL-based logs
- **Tools Used**: OpenAI (GPT-4o), Anthropic (Claude), Gemini in Google Workspace, DeepSeek on Ollama (local CPU, open UI)
- **Key Prompts Tested**:
  - “Write a Kubernetes YAML for nginx with 2 replicas”
  - “Generate a shell script to clean Docker images and restart a service”
  - “Create SQL for counting login events by day in the past week”
  - “Define secure S3 bucket in Terraform with logging and encryption”

---

