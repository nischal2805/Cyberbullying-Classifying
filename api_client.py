import os
import requests
import json
import time
import urllib3
from typing import Optional, Tuple
from dotenv import load_dotenv

# Disable SSL warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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

# Simple keyword-based fallback classifier
BULLYING_KEYWORDS = {
    "Ethnicity/Race": [
        "nigger", "negro", "chink", "gook", "spic", "wetback", "beaner",
        "cracker", "honky", "kike", "raghead", "towelhead", "paki", "curry", 
        "go back to your country", "illegal alien", "foreigner scum", "dirty immigrant"
    ],
    "Gender/Sexual": [
        "fag", "faggot", "dyke", "homo", "tranny",
        "sissy", "queer", "slut", "whore", "bitch", "cunt", "pussy",
        "man up", "like a girl", "women belong", "hoe", "thot"
    ],
    "Religion": [
        "terrorist", "jihad", "infidel", "heathen", "godless", "cult",
        "your religion", "your god", "religious freak"
    ],
    "Other": [
        "stupid", "idiot", "dumb", "moron", "retard", "retarded", "loser", "ugly", "fat", "fatso",
        "kill yourself", "kys", "die", "hate you", "nobody likes you", "worthless",
        "pathetic", "disgusting", "trash", "garbage", "waste of space", "freak",
        "weirdo", "creep", "shut up", "go away", "nobody cares", "useless",
        "dumbass", "dumba$$", "asshole", "a$$hole", "bastard", "fool", "clown",
        "piece of shit", "pos", "scum", "filth", "disgusting person", "gross",
        "annoying", "irritating", "hate", "despise", "can't stand you"
    ]
}


def keyword_fallback_classifier(text: str) -> Tuple[Optional[str], Optional[str]]:
    """
    Simple keyword-based classifier as fallback when API/model fails.
    """
    text_lower = text.lower().strip()
    
    # Remove common obfuscation characters
    text_cleaned = text_lower.replace('*', '').replace('$', 's').replace('@', 'a').replace('0', 'o')
    
    for category, keywords in BULLYING_KEYWORDS.items():
        for keyword in keywords:
            keyword_lower = keyword.lower()
            if keyword_lower in text_lower or keyword_lower in text_cleaned:
                return category, f"Contains potentially harmful content: '{keyword}'"
    
    return "Not Cyberbullying", "No harmful content detected"


def classify_with_groq(text: str, timeout: int = 30) -> Tuple[Optional[str], Optional[str]]:
    """
    Classify text using Groq API with Llama model.
    
    Returns:
        Tuple of (category, explanation) or (None, None) if API fails
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("GROQ_API_KEY not set, using fallback classifier")
        return keyword_fallback_classifier(text)
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    
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
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {
                "role": "system",
                "content": "You are a cyberbullying detection expert. Respond only with valid JSON."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2,
        "max_tokens": 256
    }
    
    try:
        # Disable SSL verification to fix certificate errors
        response = requests.post(url, headers=headers, json=payload, timeout=timeout, verify=False)
        response.raise_for_status()
        
        result = response.json()
        
        # Extract the response from Groq
        if "choices" in result and len(result["choices"]) > 0:
            message = result["choices"][0].get("message", {})
            response_text = message.get("content", "").strip()
            
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
                print(f"Failed to parse Groq response: {response_text}")
                # Try to extract category from plain text
                for cat in VALID_CATEGORIES:
                    if cat.lower() in response_text.lower():
                        return cat, response_text
                return keyword_fallback_classifier(text)
        
        return keyword_fallback_classifier(text)
        
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429:
            print("Groq API rate limited, using fallback classifier")
            return keyword_fallback_classifier(text)
        print(f"Error calling Groq API: {e}")
        return keyword_fallback_classifier(text)
    except requests.RequestException as e:
        print(f"Error calling Groq API: {e}")
        return keyword_fallback_classifier(text)
    except Exception as e:
        print(f"Unexpected error in Groq classification: {e}")
        return keyword_fallback_classifier(text)


def classify_with_api(text: str, timeout: int = 10) -> Optional[str]:
    """
    Classify text by calling an external classification API.
    Uses Groq API for classification.
    
    Returns:
        Category string or None if all APIs fail
    """
    # Try Groq
    category, explanation = classify_with_groq(text, timeout=timeout)
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
        - api_label: Label from Groq API
        - api_explanation: Explanation from Groq
        - final_label: The authoritative final label
        - is_bullying: Boolean indicating if content is problematic
    """
    local_label = None
    keyword_label = None
    keyword_explanation = None
    
    # Try to get local prediction
    try:
        from detector import _predict_local_label
        local_label = _predict_local_label(text)
    except Exception as e:
        print(f"Local prediction failed: {e}")
        local_label = None
    
    # ALWAYS get keyword fallback prediction (it's fast and reliable)
    keyword_label, keyword_explanation = keyword_fallback_classifier(text)
    
    # Get Groq prediction (will also fallback to keywords if API fails)
    api_label, api_explanation = classify_with_groq(text)
    
    # Decision logic for final label:
    # 1. If Groq succeeds and doesn't return keyword fallback result, use it (most accurate)
    # 2. If keyword classifier detected something, use it (reliable for obvious cases)  
    # 3. If local model detected something, use it
    # 4. Otherwise, use "Not Cyberbullying"
    
    # Check if Groq actually responded (not just fallback)
    groq_actually_responded = (api_label != keyword_label or 
                                api_explanation != keyword_explanation)
    
    if api_label and api_label != "Not Cyberbullying" and groq_actually_responded:
        # Groq detected bullying
        final_label = api_label
        final_explanation = api_explanation
    elif keyword_label and keyword_label != "Not Cyberbullying":
        # Keyword classifier detected bullying
        final_label = keyword_label
        final_explanation = keyword_explanation
    elif local_label and local_label != "Not Cyberbullying":
        # Local model detected bullying
        final_label = local_label
        final_explanation = api_explanation or "Detected by local model"
    else:
        # Nothing detected
        final_label = "Not Cyberbullying"
        final_explanation = api_explanation or "No harmful content detected"
    
    is_bullying = final_label != "Not Cyberbullying"
    
    print(f"[CLASSIFICATION] Text: '{text[:50]}...'")
    print(f"[CLASSIFICATION] Local: {local_label}, Keyword: {keyword_label}, Groq: {api_label}, Final: {final_label}")
    
    return {
        "local_label": local_label,
        "api_label": api_label,
        "api_explanation": api_explanation or final_explanation,
        "final_label": final_label,
        "is_bullying": is_bullying,
        "bullying_type": final_label.lower() if is_bullying else None
    }
