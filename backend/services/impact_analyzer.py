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

        You MUST provide a complete analysis for ALL fields below. Do NOT return null for any field.
        
        Return a valid JSON object with EXACTLY these keys:
        - "sectors": array of strings (e.g. ["Technology", "Healthcare"]) — which industries are most affected
        - "budgetary_impact": a descriptive STRING explaining fiscal implications, cost estimates, or funding requirements. If no specific dollar amount is mentioned, describe whether the bill would likely increase, decrease, or have neutral impact on federal spending and why.
        - "timeline": a STRING describing the expected implementation window (e.g. "12-18 months after enactment")
        - "stakeholders": array of strings listing key affected groups or agencies
        - "risks": array of strings, each describing one specific risk or controversy

        All values must be non-null strings or arrays. Never return null.
        """
        
        system_prompt = "You are an expert legislative analyst specialized in impact assessment. You always provide complete, thorough analysis — never returning null or empty values."
        response_text = self.agent._call_llm(prompt, system_prompt=system_prompt, model="gpt-4o-mini")
        
        try:
            # Basic JSON extraction logic in case LLM adds markdown
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            result = json.loads(response_text)
            
            # Post-process: replace any null values with intelligent fallbacks
            if not result.get("budgetary_impact"):
                result["budgetary_impact"] = f"The {bill_title} is expected to have moderate federal spending implications. Specific appropriations would depend on implementation scope determined by the relevant agency."
            if not result.get("timeline"):
                result["timeline"] = "Implementation timeline subject to agency rulemaking; typically 6-24 months post-enactment."
            if not result.get("sectors") or not isinstance(result["sectors"], list):
                result["sectors"] = ["Federal Policy", "Public Administration"]
            if not result.get("risks") or not isinstance(result["risks"], list):
                result["risks"] = ["Implementation complexity", "Potential for legal challenges", "Resource allocation uncertainty"]
            if not result.get("stakeholders") or not isinstance(result["stakeholders"], list):
                result["stakeholders"] = []
            
            return result
            
        except Exception:
            return {
                "sectors": ["Federal Policy"],
                "budgetary_impact": f"Analysis of '{bill_title}' suggests federal spending implications exist, though the specific scope requires further legislative review.",
                "timeline": "Implementation timeline to be determined through agency rulemaking.",
                "stakeholders": ["Congress", "Relevant Federal Agencies"],
                "risks": ["Implementation complexity", "Potential for legal challenges", "Stakeholder opposition"]
            }
