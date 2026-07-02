"""
ai_helper.py
Handles all communication with the LLM (OpenAI or Google Gemini).
The model is asked to classify the user's question into one of a fixed
set of intents (duplicates / missing / pivot / predict / chart / general)
and extract any parameters (column names) needed to run that function.
"""

import json
import re

SYSTEM_PROMPT = """You are a data-analysis assistant embedded inside an Excel/CSV analysis tool.
The user has uploaded a spreadsheet. You will be given the column names and a few sample rows.
Your job is to read the user's natural-language question and return ONLY a JSON object
(no markdown, no extra text) describing what to do, using this exact schema:

{
  "intent": "duplicates" | "missing" | "pivot" | "predict" | "chart" | "general",
  "columns": {
      "subset_cols": [list of column names, only for duplicates, can be empty],
      "index_col": "column name, only for pivot",
      "columns_col": "column name, only for pivot, can be null",
      "values_col": "column name, only for pivot/predict/chart",
      "aggfunc": "sum|mean|count|max|min, only for pivot",
      "date_col": "column name, only for predict",
      "chart_type": "bar|line|scatter|pie|histogram, only for chart",
      "x_col": "column name, only for chart",
      "y_col": "column name, only for chart"
  },
  "answer": "If intent is 'general', put your direct natural-language answer here. Otherwise empty string."
}

Rules:
- Only use column names that actually exist in the provided column list.
- If the question doesn't map cleanly to duplicates/missing/pivot/predict/chart, use intent "general"
  and answer the question directly using the sample data/columns given, in plain English.
- Return valid JSON only.
"""


def _build_user_prompt(question: str, profile: dict) -> str:
    return f"""Columns: {profile['columns']}
Data types: {profile['dtypes']}
Sample rows: {profile['sample_rows']}
Rows total: {profile['n_rows']}

User question: "{question}"
"""


def _extract_json(text: str) -> dict:
    """LLMs sometimes wrap JSON in ```json fences — strip those before parsing."""
    text = text.strip()
    text = re.sub(r"^```json\s*|^```\s*|```$", "", text, flags=re.MULTILINE).strip()
    return json.loads(text)


def ask_openai(question, profile, api_key, model="gpt-4o-mini"):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": _build_user_prompt(question, profile)},
        ],
        temperature=0,
    )
    return _extract_json(resp.choices[0].message.content)


def ask_gemini(question, profile, api_key, model="gemini-flash-latest"):
    import google.generativeai as genai
    genai.configure(api_key=api_key)
    gmodel = genai.GenerativeModel(model, system_instruction=SYSTEM_PROMPT)
    resp = gmodel.generate_content(_build_user_prompt(question, profile))
    return _extract_json(resp.text)


def route_question(question, profile, provider, api_key):
    """
    provider: "OpenAI" or "Gemini"
    Returns a parsed intent dict. Falls back to a 'general' intent with an
    error message if the LLM call or JSON parsing fails.
    """
    try:
        if provider == "OpenAI":
            return ask_openai(question, profile, api_key)
        else:
            return ask_gemini(question, profile, api_key)
    except Exception as e:
        return {
            "intent": "general",
            "columns": {},
            "answer": f"⚠️ Couldn't process that with the AI model ({e}). "
                      f"Try rephrasing, or use the dedicated tabs above instead."
        }
