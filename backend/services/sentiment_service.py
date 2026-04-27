import openai
import os
from ddgs import DDGS
from services.logging_service import log_error

class SentimentService:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")

    def analyze_public_pulse(self, bill_number: str, title: str):
        """
        Scrapes social mentions and parses sentiment using LLM.
        """
        try:
            d = DDGS()
            query = f'"{bill_number}" {title} Reddit discussion opinion'
            results = list(d.text(query, max_results=5))
            
            snippets = "\n".join([f"- {r.get('body', '')}" for r in results])
            
            if not snippets:
                return {
                    "score": 0.5,
                    "label": "Neutral",
                    "summary": "No significant recent public discourse detected in the primary social vectors."
                }

            prompt = f"""
            Analyze the public sentiment for US Bill {bill_number} based on these search snippets:
            {snippets}
            
            Return a JSON object with:
            - score: 0.0 (Extremely Negative/Angry) to 1.0 (Extremely Positive/Supportive)
            - label: One of [Positive, Negative, Mixed, Hotly Contested, Neutral]
            - summary: A 1-sentence summary of public opinion.
            """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a social sentiment analyst."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            import json
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            log_error(str(e), context="SentimentService")
            return {"score": 0.5, "label": "Neutral", "summary": "Intelligence pulse currently recalibrating."}
