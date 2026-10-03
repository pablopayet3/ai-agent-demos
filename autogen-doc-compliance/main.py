import os
import json
from typing import Dict, List
from datetime import datetime

from dotenv import load_dotenv
import autogen

# ============================
# 1. Config (key read from .env)
# ============================
load_dotenv()
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("Please set ANTHROPIC_API_KEY in your .env file (see .env.example).")

config_list = [
    {
        "model": "claude-sonnet-4-6",
        "api_key": os.environ.get("ANTHROPIC_API_KEY"),
        "base_url": "https://api.anthropic.com",
        "api_type": "anthropic",
        "api_version": "2023-06-01",
        "max_completion_tokens": 3000,
    }
]

llm_config = {"config_list": config_list}

# ============================
# 2. Sample Documents
# ============================
SAMPLE_DOCUMENTS = [
    {
        "id": "DOC001",
        "title": "Employee Remote Work Policy",
        "type": "HR Policy",
        "content": """
Remote Work Policy
Effective Date: January 2023

1. Eligibility: All full-time employees
2. Equipment: Company will provide laptop
3. Work Hours: Standard 9-5 EST

Note: This policy supersedes the 2021 remote work guidelines.
""",
        "last_updated": "2023-01-15"
    },
    {
        "id": "DOC002",
        "title": "Data Security Manual",
        "type": "Technical Manual",
        "content": """
Data Security Manual
Version: 2.1

1. Password Requirements: Minimum 8 characters
2. Encryption: Use AES-256 for sensitive data

Missing sections:
- Incident Response Procedures
- Data Retention Policy
""",
        "last_updated": "2024-03-20"
    },
    {
        "id": "DOC003",
        "title": "Customer Service Guidelines",
        "type": "Operational Guidelines",
        "content": """
Customer Service Guidelines

1. Response Time: Within 24 hours
2. Escalation: After 48 hours to supervisor
3. Communication: Use template responses from 2019 handbook

Approved by: [Missing Signature]
Review Date: [Not Specified]
""",
        "last_updated": "2024-11-10"
    }
]

# ============================
# 3. Multi-Agent System
# ============================
class DocumentComplianceSystem:

    def __init__(self):

        # Document Scanner Agent
        self.document_scanner = autogen.AssistantAgent(
            name="DocumentScanner",
            llm_config=llm_config,
            system_message="""You are a Document Scanner agent responsible for:
1. Monitoring documents
2. Extracting metadata
3. Categorizing documents
Format your findings clearly."""
        )

        # Compliance Checker Agent
        self.compliance_checker = autogen.AssistantAgent(
            name="ComplianceChecker",
            llm_config=llm_config,
            system_message="""You are a Compliance Checker agent responsible for:
1. Identifying missing sections
2. Detecting outdated content
3. Assigning severity levels
4. Providing remediation recommendations
Format: Issue Type | Severity | Details | Recommendation"""
        )

        # Review Coordinator Agent
        self.review_coordinator = autogen.AssistantAgent(
            name="ReviewCoordinator",
            llm_config=llm_config,
            system_message="""You are a Review Coordinator agent responsible for:
1. Routing documents based on severity
2. Creating action items
3. Assigning deadlines
Format: Document | Issues | Routing Decision | Action Items | Due Date"""
        )

        # User Proxy Agent
        self.user_proxy = autogen.UserProxyAgent(
            name="UserProxy",
            human_input_mode="TERMINATE",
            max_consecutive_auto_reply=2,
            code_execution_config=False,
        )

        # Group Chat
        self.group_chat = autogen.GroupChat(
            agents=[
                self.document_scanner,
                self.compliance_checker,
                self.review_coordinator,
                self.user_proxy
            ],
            messages=[],
            max_round=20
        )

        self.manager = autogen.GroupChatManager(
            groupchat=self.group_chat,
            llm_config=llm_config
        )

    # ============================
    # Process Documents
    # ============================
    def process_document_batch(self, documents: List[Dict]):
        print("\nStarting AutoGen Document Compliance Workflow\n")
        print("=" * 60)

        doc_summary = "\n\n".join([
            f"Document ID: {doc['id']}\n"
            f"Title: {doc['title']}\n"
            f"Type: {doc['type']}\n"
            f"Last Updated: {doc['last_updated']}\n"
            f"Content Preview:\n{doc['content'][:200]} ..."
            for doc in documents
        ])

        initial_message = f"""
New documents detected. Begin compliance workflow:

{doc_summary}

Steps:
1. DocumentScanner -> Categorize
2. ComplianceChecker -> Analyze
3. ReviewCoordinator -> Route & Assign

Begin analysis.
"""

        self.user_proxy.initiate_chat(
            self.manager,
            message=initial_message
        )

        return self.generate_compliance_report()

    # ============================
    # Final Report
    # ============================
    def generate_compliance_report(self):
        print("\n" + "=" * 60)
        print("[ COMPLIANCE WORKFLOW SUMMARY ]")
        print("=" * 60)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Documents Processed: {len(SAMPLE_DOCUMENTS)}")
        print("\nWorkflow Demonstration Complete\n")


# ============================
# 4. Run Demo
# ============================
def run_demo():
    print("\nAutoGen Document Compliance System Demo")
    print("=" * 60)
    print("- Multi-agent collaboration")
    print("- Claude LLM integration")
    print("- Automated workflow execution\n")

    compliance_system = DocumentComplianceSystem()
    compliance_system.process_document_batch(SAMPLE_DOCUMENTS)


# ============================
# 5. Main
# ============================
if __name__ == "__main__":
    try:
        run_demo()
    except Exception as e:
        print(f"\nError: {e}")
