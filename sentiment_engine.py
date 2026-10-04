import json
import os
from dotenv import load_dotenv
from pathlib import Path
from functools import lru_cache

import openai


@lru_cache(maxsize=1)
def _get_client(api_key: str) -> openai.OpenAI:
    return openai.OpenAI(api_key=api_key)


def analyze_headline_sentiment(
    ticker: str,
    headlines: list[dict],
    custom_rule: str,
) -> tuple[float, str]:
    """
    Evaluates news headlines against a custom user rule.
    Returns a normalized sentiment score between -1.0 (Extreme Negative) and +1.0 (Extreme Positive).
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured.")

    prompt = f"""
    You are a quantitative news analyst evaluating {ticker}.
    User Strategy Rule: "{custom_rule}"
    
    Headlines:
    {json.dumps(headlines)}
    
    Analyze the sentiment of these headlines strictly according to the User Strategy Rule.
    Output MUST be valid JSON with the following format:
    {{
        "score": <float between -1.0 and 1.0>,
        "rationale": "<one-sentence summary of overall market sentiment>"
    }}
    """
    
    response = _get_client(api_key).chat.completions.create(
        model="gpt-4o-mini", # Fast & inexpensive for live hackathon loops
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    content = response.choices[0].message.content
    if not content:
        raise RuntimeError("The sentiment service returned an empty response.")

    data = json.loads(content)
    score = float(data.get("score", 0.0))
    if not -1.0 <= score <= 1.0:
        raise ValueError("The sentiment service returned a score outside [-1, 1].")
    return score, str(data.get("rationale", ""))

#sentiment = analyze_headline_sentiment('AAPL', data_processing.get_news_headlines('GOOG'), "Shift capital into gold and defensive stocks whenever headline sentiment drops below 0.3")
#print(sentiment)
