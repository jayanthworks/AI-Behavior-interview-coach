import json
import re
from typing import Dict, Any

from huggingface_hub import InferenceClient


def _extract_json(text: str) -> Dict[str, Any]:
    """Best-effort extraction of the first JSON object in text."""
    try:
        return json.loads(text)
    except Exception:
        pass
    # Fallback: find first {...} block
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    # Last fallback: build minimal structure
    return {
        "score": None,
        "summary": text.strip()[:500],
        "strengths": [],
        "improvements": []
    }


class ResponseRater:
    def __init__(self, token: str, model: str = "deepseek-ai/DeepSeek-V3-0324") -> None:
        self.client = InferenceClient(token=token)
        self.model = model

    def rate_response(self, question: str, transcript: str) -> Dict[str, Any]:
        """Return a dict: {score (0-10), summary, strengths[], improvements[]}"""
        system_instructions = (
            "You are a behavioral interview evaluator. Rate responses on overall thought process, clarity, "
            "structure (STAR), relevance, self-awareness, and impact. Do NOT penalize minor grammar or "
            "ASR transcription artifacts. Be concise and professional."
        )
        rubric = (
            "Scoring rubric (0-10):\n"
            "- 9-10: Exceptional structure (STAR), clear reasoning, strong impact, self-awareness.\n"
            "- 7-8: Good structure and reasoning; mostly relevant with actionable examples.\n"
            "- 5-6: Some structure; generic or partially relevant; limited depth.\n"
            "- 3-4: Vague, little structure; weak linkage to the question.\n"
            "- 0-2: Off-topic or incoherent.\n"
            "Output strictly in compact JSON with keys: score (integer 0-10), summary (string),"
            " strengths (array of strings), improvements (array of strings)."
        )
        prompt = (
            f"Behavioral interview question:\n{question}\n\n"
            f"Candidate transcript (ASR, may include minor errors):\n{transcript}\n\n"
            f"{rubric}"
        )

        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_instructions},
                {"role": "user", "content": prompt},
            ],
        )

        content = completion.choices[0].message.content
        result = _extract_json(content)

        # Normalize and clamp
        score = result.get("score")
        if isinstance(score, (int, float)):
            try:
                score = int(round(float(score)))
            except Exception:
                score = None
        if isinstance(score, int):
            score = max(0, min(10, score))
        result["score"] = score

        # Ensure lists
        for k in ("strengths", "improvements"):
            v = result.get(k)
            if isinstance(v, list):
                result[k] = [str(x) for x in v][:6]
            elif isinstance(v, str) and v.strip():
                result[k] = [v.strip()]
            else:
                result[k] = []

        # Summary fallback
        if not isinstance(result.get("summary"), str):
            result["summary"] = ""

        return result
