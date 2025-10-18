import json
import requests
from dotenv import load_dotenv
import os
from ev_charging_stations.models.query_models import UserQuery
import re


load_dotenv()
OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY")

def extract_json_from_response(text: str) -> str:
    """
    Removes markdown code fences and extracts valid JSON.
    """
    # Remove code block markers like ```json or ```
    text = re.sub(r"^```(?:json)?", "", text.strip(), flags=re.IGNORECASE | re.MULTILINE)
    text = re.sub(r"```$", "", text.strip(), flags=re.MULTILINE)
    return text.strip()


def parse_user_question(question: str) -> UserQuery:
    CHARGING_SPEEDS = ["Fast", "Supercharger"]
    CHARGING_TYPES = ["Type 1", "Type 2", "DC Fast Charge"]
    ACCESSIBILITY = ["Public", "Restricted"]
    prompt = f"""
Extract these fields from this question:
"city": string or null,
"latitude": float or null,
"longitude": float or null,
"charging_speed": one of {CHARGING_SPEEDS} or null,
"charging_type": one of {CHARGING_TYPES} or null,
"accessibility": one of {ACCESSIBILITY} or null,
"sort_by_reviews": boolean, true if user wants stations with better reviews, false otherwise

Return JSON with ONLY these keys. Use null for missing values, and true/false for "sort_by_reviews". Only return a JSON object without any extra text.

Question: {question}
"""

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta-llama/llama-4-scout:free",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        print("Raw LLM output:", content)  # 👈 helpful debug
        clean_json = extract_json_from_response(content)
        print("Clean JSON:", clean_json)   # 👈 confirm cleaned version
        parsed = json.loads(clean_json)
        return UserQuery(**parsed)

    except Exception as e:
        print("Error calling OpenRouter:", e)
        return UserQuery()
