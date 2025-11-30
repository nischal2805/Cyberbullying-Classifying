import os
import requests
import json
from typing import Optional, Tuple
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Category mapping for consistent output
VALID_CATEGORIES = [
    "Not Cyberbullying",
    "Ethnicity/Race", 
    "Gender/Sexual",
    "Religion",
    "Other"
]


def classify_with_gemini(text: str, timeout: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """
    Classify text using Google Gemini 2.0 Flash model.
    
    Returns:
        Tuple of (category, explanation) or (None, None) if API fails
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY not set, skipping Gemini classification")
        return None, None
    
    # Gemini 2.0 Flash API endpoint
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    prompt = f"""You are a cyberbullying detection expert. Analyze the following text and determine if it contains cyberbullying content.

IMPORTANT: Even mild insults like "stupid", "idiot", "dumb", "loser", "ugly", etc. should be flagged as problematic content.

Text to analyze: "{text}"

Classify this text into EXACTLY ONE of these categories:
1. "Not Cyberbullying" - Neutral, positive, or harmless content
2. "Ethnicity/Race" - Bullying based on race, ethnicity, nationality, or cultural background
3. "Gender/Sexual" - Bullying based on gender, sexual orientation, or gender identity
4. "Religion" - Bullying based on religious beliefs or practices
5. "Other" - General bullying, insults, or harassment that doesn't fit the above categories (includes words like stupid, idiot, ugly, loser, etc.)

Respond with ONLY a JSON object in this exact format (no markdown, no code blocks):
{{"category": "category_name", "explanation": "brief reason"}}"""

    headers = {
        "Content-Type": "application/json"
    }
    
    payload = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }],
        "generationConfig": {
            "temperature": 0.1,
            "topK": 1,
            "topP": 1,
            "maxOutputTokens": 256
        }
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=timeout)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the text response from Gemini
        if "candidates" in result and len(result["candidates"]) > 0:
            content = result["candidates"][0].get("content", {})
            parts = content.get("parts", [])
            if parts:
                response_text = parts[0].get("text", "").strip()
                
                # Clean up response - remove markdown code blocks if present
                response_text = response_text.replace("```json", "").replace("```", "").strip()
                
                # Parse JSON response
                try:
                    data = json.loads(response_text)
                    category = data.get("category", "Not Cyberbullying")
                    explanation = data.get("explanation", "")
                    
                    # Validate category
                    if category not in VALID_CATEGORIES:
                        # Try to map to closest valid category
                        category_lower = category.lower()
                        if "race" in category_lower or "ethnic" in category_lower:
                            category = "Ethnicity/Race"
                        elif "gender" in category_lower or "sexual" in category_lower:
                            category = "Gender/Sexual"
                        elif "religion" in category_lower:
                            category = "Religion"
                        elif "not" in category_lower or "safe" in category_lower:
                            category = "Not Cyberbullying"
                        else:
                            category = "Other"
                    
                    return category, explanation
                    
                except json.JSONDecodeError:
                    print(f"Failed to parse Gemini response: {response_text}")
                    # Try to extract category from plain text
                    for cat in VALID_CATEGORIES:
                        if cat.lower() in response_text.lower():
                            return cat, response_text
                    return None, None
        
        return None, None
        
    except requests.RequestException as e:
        print(f"Error calling Gemini API: {e}")
        return None, None
    except Exception as e:
        print(f"Unexpected error in Gemini classification: {e}")
        return None, None


def classify_with_api(text: str, timeout: int = 10) -> Optional[str]:
    """
    Classify text by calling an external classification API.
    First tries Gemini, then falls back to custom API if configured.
    
    Returns:
        Category string or None if all APIs fail
    """
    # Try Gemini first
    category, explanation = classify_with_gemini(text, timeout=timeout)
    if category:
        return category
    
    # Fallback to custom API if configured
    api_url = os.getenv("CLASSIFIER_API_URL")
    if not api_url:
        return None

    headers = {
        "Content-Type": "application/json"
    }
    api_key = os.getenv("CLASSIFIER_API_KEY")
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    payload = {"text": text}

    try:
        resp = requests.post(api_url, json=payload, headers=headers, timeout=timeout)
        resp.raise_for_status()

        try:
            data = resp.json()
            if isinstance(data, dict) and "category" in data:
                return data["category"]
            for k in ("label", "prediction", "class"):
                if isinstance(data, dict) and k in data:
                    return data[k]
        except ValueError:
            pass

        text_body = resp.text.strip()
        if text_body:
            return text_body

    except requests.RequestException as e:
        print(f"Error calling classifier API: {e}")

    return None


def get_detailed_classification(text: str) -> dict:
    """
    Get detailed classification with both local and API results.
    
    Returns a dict with:
        - local_label: Label from local model (if available)
        - api_label: Label from Gemini API
        - api_explanation: Explanation from Gemini
        - final_label: The authoritative final label
        - is_bullying: Boolean indicating if content is problematic
    """
    from detector import _predict_local_label
    
    # Get local prediction
    try:
        local_label = _predict_local_label(text)
    except Exception as e:
        print(f"Local prediction failed: {e}")
        local_label = None
    
    # Get Gemini prediction
    api_label, api_explanation = classify_with_gemini(text)
    
    # Final label: prefer API, fallback to local
    final_label = api_label or local_label or "Not Cyberbullying"
    is_bullying = final_label != "Not Cyberbullying"
    
    return {
        "local_label": local_label,
        "api_label": api_label,
        "api_explanation": api_explanation,
        "final_label": final_label,
        "is_bullying": is_bullying,
        "bullying_type": final_label.lower() if is_bullying else None
    }
