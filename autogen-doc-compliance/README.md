# Autonomous Document Compliance (AutoGen)

A team of AI agents that reviews company policy documents and flags what's missing or out of date. A Document Scanner categorizes each document, a Compliance Checker finds gaps and rates severity, and a Review Coordinator routes issues and assigns owners and deadlines. Built with Microsoft AutoGen and Claude.

## Agents
- **DocumentScanner** — monitors documents, extracts metadata, categorizes
- **ComplianceChecker** — finds missing sections and outdated content, assigns severity
- **ReviewCoordinator** — routes by severity, creates action items with deadlines

## Run
1. `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and add your Anthropic key.
3. `python main.py`

Runs on three sample documents included in the script.
