import json
import openai
import data_processing
import os


client = openai.OpenAI(api_key="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")

def analyze_headline_sentiment(ticker: str, headlines: list[dict], custom_rule: str) -> float:
    """
    Evaluates news headlines against a custom user rule.
    Returns a normalized sentiment score between -1.0 (Extreme Negative) and +1.0 (Extreme Positive).
    """
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
    
    response = client.chat.completions.create(
        model="gpt-4o-mini", # Fast & inexpensive for live hackathon loops
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    
    data = json.loads(response.choices[0].message.content)
    return float(data.get("score", 0.0)), data.get("rationale", "")

sentiment = analyze_headline_sentiment('AAPL', data_processing.get_news_headlines('GOOG'), "Shift capital into gold and defensive stocks whenever headline sentiment drops below 0.3")
print(sentiment)
