import openai
import os
from services.logging_service import log_error

class ImpactAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY not found in environment")
        openai.api_key = self.api_key

    def generate_impact_report(self, bill_title: str, summary: str):
        """
        Generates a structured impact report using LLM reasoning.
        """
        prompt = f"""
        Execute a Deep-Box Regulatory Analysis for the following US Legislative Bill.
        
        BILL TITLE: {bill_title}
        SUMMARY: {summary}
        
        Analyze the following dimensions:
        1. SPENDING AUTHORIZATIONS: Identify specific funding levels or budget impacts.
        2. REGULATORY MANDATES: List new requirements for private or public entities.
        3. PRIMARY BENEFICIARIES: Who gains the most from this bill?
        4. POTENTIAL RISKS: Identify constitutional, economic, or regulatory overlaps.
        
        Format the output as a structured Markdown report with clear headings and bullet points.
        Use a professional, neutral, yet investigative tone.
        """
        
        try:
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional legislative analyst specialized in regulatory impact assessments."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1000
            )
            return response.choices[0].message.content
        except Exception as e:
            log_error(str(e), context="ImpactAgent/Generation")
            return "Failed to generate AI impact report. Please check systemic connection."
