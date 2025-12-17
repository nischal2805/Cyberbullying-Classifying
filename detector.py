import re
import os
import ssl
import nltk
from typing import Optional

# Import API client function
try:
    from api_client import classify_with_api
except ImportError:
    # Fallback if api_client is not available
    def classify_with_api(text: str) -> Optional[str]:
        return None

# Simple keyword-based fallback classifier (duplicated to avoid circular imports)
BULLYING_KEYWORDS = {
    "Ethnicity/Race": [
        "nigger", "negro", "chink", "gook", "spic", "wetback", "beaner",
        "cracker", "honky", "kike", "raghead", "towelhead", "paki", "curry", 
        "go back to your country", "illegal alien", "foreigner", "immigrant"
    ],
    "Gender/Sexual": [
        "fag", "faggot", "dyke", "homo", "tranny",
        "sissy", "queer", "slut", "whore", "bitch", "cunt", "pussy",
        "man up", "like a girl", "women belong"
    ],
    "Religion": [
        "terrorist", "jihad", "infidel", "heathen", "godless", "cult"
    ],
    "Other": [
        "stupid", "idiot", "dumb", "moron", "retard", "loser", "ugly", "fat",
        "kill yourself", "kys", "die", "hate you", "nobody likes you", "worthless",
        "pathetic", "disgusting", "trash", "garbage", "waste of space", "freak",
        "weirdo", "creep", "shut up", "go away", "nobody cares", "useless"
    ]
}

def _keyword_fallback_classifier(text):
    """Simple keyword-based classifier as fallback."""
    text_lower = text.lower()
    for category, keywords in BULLYING_KEYWORDS.items():
        for keyword in keywords:
            if keyword.lower() in text_lower:
                return category, f"Contains potentially harmful keyword"
    return "Not Cyberbullying", "No harmful content detected"

# Try to import torch and transformers - they may fail due to version issues
try:
    import torch
    from transformers import AutoModelForSequenceClassification, AutoTokenizer
    TORCH_AVAILABLE = True
except ImportError as e:
    print(f"PyTorch/Transformers not available: {e}")
    TORCH_AVAILABLE = False

# SSL workaround for NLTK downloads
try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    pass
else:
    ssl._create_default_https_context = _create_unverified_https_context

# Download NLTK data
nltk.download('stopwords', quiet=True)
nltk.download('punkt', quiet=True)

# Alternative: Use a try-except block for the NLTK resources
try:
    from nltk.corpus import stopwords
    STOPWORDS = set(stopwords.words('english'))
except:
    # Fallback if stopwords can't be downloaded
    STOPWORDS = set(['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 
                    'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 
                    'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 
                    'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 
                    'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 
                    'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 
                    'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 
                    'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 
                    'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once'])

# Path to your saved model
MODEL_PATH = "boss2805/cyberbully"
TOKENIZER_NAME = "distilbert-base-uncased"  # The base tokenizer for your model

# Define the class labels (from your confusion matrix)
CLASS_LABELS = ['Ethnicity/Race', 'Gender/Sexual', 'Not Cyberbullying', 'Religion']

# Load model and tokenizer only if torch is available
model = None
tokenizer = None
device = None

if TORCH_AVAILABLE:
    try:
        model = AutoModelForSequenceClassification.from_pretrained(MODEL_PATH)
        tokenizer = AutoTokenizer.from_pretrained(TOKENIZER_NAME)
        model.eval()  # Set model to evaluation mode
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model.to(device)
        print("Model loaded successfully")
    except Exception as e:
        print(f"Error loading model: {e}")
        model = None
        tokenizer = None

def preprocess_text(text):
    """Clean and preprocess text for model input."""
    text = text.lower()
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    text = ' '.join([word for word in text.split() if word not in STOPWORDS])
    return text

def _predict_local_label(text: str) -> str:
    """Return the local model's predicted label (string)."""
    if not TORCH_AVAILABLE or model is None or tokenizer is None:
        # Use keyword fallback when model is not available
        label, _ = _keyword_fallback_classifier(text)
        return label

    import torch
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
        predicted_class_id = torch.argmax(predictions, dim=-1).item()

    return CLASS_LABELS[predicted_class_id]


def detect_cyberbullying(text: str):
    """Detect cyberbullying by combining local model and external API.

    Flow:
    - Run the local Hugging Face model to get an initial label.
    - If a remote API is configured (env `CLASSIFIER_API_URL`), call it with the text.
      If the API responds with a category, use that category as the final label.
    - If the API is not configured or fails, fall back to the local model label.

    Returns (is_bullying: bool, bullying_type: Optional[str]) preserving the
    original function signature used by `app.py`.
    """
    try:
        local_label = _predict_local_label(text)
    except Exception as e:
        print(f"Local prediction failed: {e}")
        local_label = "Not Cyberbullying"

    # Try remote API classifier; it should return a category string or None
    api_label = classify_with_api(text)

    final_label = api_label if api_label is not None else local_label

    is_bullying = (final_label != "Not Cyberbullying")
    bullying_type = final_label.lower() if is_bullying else None

    print(f"Text: '{text}'")
    print(f"Local label: {local_label}; API label: {api_label}; Final: {final_label}")

    return is_bullying, bullying_type

# Test the detector directly if run as standalone script
if __name__ == "__main__":
    test_texts = [
        "Hello, how are you today?",
        "I hate people from your country",
        "You're stupid because you're a woman",
        "Your religion is evil and you should be ashamed"
    ]
    
    for text in test_texts:
        is_bullying, bullying_type = detect_cyberbullying(text)
        print(f"Result: {'BULLYING - ' + bullying_type if is_bullying else 'NOT BULLYING'}")
        print("---")
