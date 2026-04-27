import json
from services.agent_service import AgentService
from services.congress_service import CongressService
from services.rag_service import RAGService

class ImpactAnalyzer:
    def __init__(self, agent_service: AgentService):
        self.agent = agent_service

    def analyze_impact(self, bill_id: str, bill_title: str, bill_summary: str) -> dict:
        """
        Perform a deep LLM analysis of a bill's projected impact across sectors.
        """
        prompt = f"""
        Analyze the legislative impact of the following bill:
        Bill ID: {bill_id}
        Title: {bill_title}
        Summary: {bill_summary}

        Please extract:
        1. Primary sectors impacted (e.g., Technology, Healthcare).
        2. Projected budgetary implications (if mentioned).
        3. Implementation timeline.
        4. Key stakeholders.
        5. Potential risks or controversies.

        Return the output as a valid JSON object with these keys: 
        'sectors', 'budgetary_impact', 'timeline', 'stakeholders', 'risks'.
        """
        
        system_prompt = "You are an expert legislative analyst specialized in impact assessment."
        response_text = self.agent._call_llm(prompt, system_prompt=system_prompt, model="gpt-4o-mini")
        
        try:
            # Basic JSON extraction logic in case LLM adds markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            return json.loads(response_text)
        except Exception:
            return {
                "sectors": ["Unknown"],
                "budgetary_impact": "Data unavailable",
                "timeline": "Unspecified",
                "stakeholders": [],
                "risks": "Failed to parse impact report"
            }
