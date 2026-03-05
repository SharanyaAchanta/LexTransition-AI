"""
Universal OCR Summarizer Engine for LexTransition-AI
Provides a single entry point for all OCR-based analysis tasks.
"""
import openai
import os

# Map prompt_type to system prompts
PROMPT_MAP = {
    "risk": "You are a legal risk analyzer. Given the extracted legal text, identify the severity, relevant sections, guidance, and possible punishments. Respond in JSON with keys: severity, sections, guidance, punishment.",
    "bail": "You are a bail eligibility analyzer. Given the legal text, extract bail eligibility, section, description, cognizable, procedure, and punishment. Respond as a list of dicts.",
    "deadline": "You are a legal deadline extractor. Extract all important dates and deadlines from the text. Respond as a list of dicts with keys: date, status.",
    "summary": "You are a legal document summarizer. Provide a plain-language summary, detected sections, authorities, and recommended actions. Respond in JSON with keys: plain_summary, sections, authorities, action_points.",
}

def summarize_with_prompt(text: str, prompt_type: str = "summary"):
    """
    Universal function for OCR-based summarization and analysis.
    Args:
        text: Extracted OCR text
        prompt_type: One of 'risk', 'bail', 'deadline', 'summary'
    Returns:
        Parsed LLM response (dict or list)
    """
    import json
    system_prompt = PROMPT_MAP.get(prompt_type, PROMPT_MAP["summary"])
    user_prompt = f"Text: {text}\nRespond as instructed."
    # Use OpenAI API or fallback to a stub for demo
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        # Demo stub for local/dev
        if prompt_type == "risk":
            return {"severity": "Medium", "sections": ["302"], "guidance": "Consult a lawyer.", "punishment": ["Imprisonment up to 10 years."]}
        if prompt_type == "bail":
            return [{"section": "302", "description": "Murder", "bailable": "Non-bailable", "cognizable": "Yes", "procedure": "Court hearing required.", "punishment": "Life imprisonment"}]
        if prompt_type == "deadline":
            return [{"date": "10/04/2026", "status": "Upcoming"}]
        return {"plain_summary": "This is a legal notice.", "sections": ["302"], "authorities": ["Police"], "action_points": ["Appear in court"]}
    # Real LLM call
    openai.api_key = api_key
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.2,
        max_tokens=512
    )
    content = response["choices"][0]["message"]["content"]
    try:
        return json.loads(content)
    except Exception:
        return {"error": "Failed to parse LLM response", "raw": content}
