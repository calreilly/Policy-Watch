import os
import openai
from services.logging_service import log_error

class PredictionService:
    @classmethod
    def calculate_prognosis(cls, bill_data: dict):
        """
        Calculates a 'Passage Prognosis' score from 0-1.
        Factors:
        - Bipartisanship (0.3 weight)
        - Sponsor Power (0.3 weight)
        - Topic Friction (0.4 weight - LLM reasoned)
        """
        try:
            # 1. Bipartisanship Score
            sponsors = bill_data.get("sponsors", [])
            parties = [s.get("party") for s in sponsors if s.get("party")]
            is_bipartisan = "D" in parties and "R" in parties
            bip_score = 0.9 if is_bipartisan else 0.4
            if len(sponsors) > 20: bip_score += 0.1 # Momentum factor

            # 2. Sponsor Power (Simulated based on party control - assume 119th GOP House/Senate for now)
            lead = next((s for s in sponsors if s.get("is_lead")), {})
            sponsor_power = 0.8 if lead.get("party") == "R" else 0.5 # Majority party bills move faster

            # 3. Topic Friction (LLM Reasoning)
            prompt = f"""
            Analyze the following bill title and summary for legislative friction in the 119th Congress.
            Title: {bill_data.get('title')}
            Summary: {bill_data.get('summary')}
            
            Return a JSON object with:
            - friction_score: 0.0 (easy) to 1.0 (deadlock)
            - reasoning: 1 sentence on why
            - momentum: 'high', 'stable', or 'low'
            """

            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "system", "content": "You are a senior congressional parliamentarian."}, {"role": "user", "content": prompt}],
                response_format={"type": "json_object"}
            )
            
            import json
            analysis = json.loads(response.choices[0].message.content)
            friction = analysis.get("friction_score", 0.5)

            # 4. Final Calculation
            # Prognosis = (Bip*0.3 + Power*0.3 + (1-Friction)*0.4)
            prognosis = (bip_score * 0.3) + (sponsor_power * 0.3) + ((1 - friction) * 0.4)
            
            return {
                "score": round(min(max(prognosis, 0.05), 0.95), 2),
                "reasoning": analysis.get("reasoning", "Historical patterns suggest stable trajectory."),
                "momentum": analysis.get("momentum", "stable"),
                "factors": {
                    "bipartisanship": bip_score,
                    "sponsor_power": sponsor_power,
                    "friction": friction
                }
            }

        except Exception as e:
            log_error(str(e), context="PredictionService")
            return {
                "score": 0.15,
                "reasoning": "Insufficient telemetry for probabilistic modeling.",
                "momentum": "unknown"
            }
