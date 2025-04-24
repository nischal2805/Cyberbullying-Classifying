import pickle
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import nltk
import ssl
import os
import torch
from transformers import AutoModelForSequenceClassification, AutoTokenizer

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

# Load model and tokenizer
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
    # Convert to lowercase
    text = text.lower()
    # Remove special characters and numbers
    text = re.sub(r'[^a-zA-Z\s]', '', text)
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    # Remove stopwords
    text = ' '.join([word for word in text.split() if word not in STOPWORDS])
    return text

def detect_cyberbullying(text):
    """
    Detect if text contains cyberbullying content using the trained transformer model.
    Returns a tuple: (is_bullying, bullying_type)
    """
    if model is None or tokenizer is None:
        # If model isn't loaded, return safe default
        print("Model not loaded, returning default")
        return False, None
    
    try:
        # Tokenize the input text
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True).to(device)
        
        # Make prediction
        with torch.no_grad():
            outputs = model(**inputs)
            predictions = torch.nn.functional.softmax(outputs.logits, dim=-1)
            predicted_class_id = torch.argmax(predictions, dim=-1).item()
        
        # Get the predicted label
        predicted_label = CLASS_LABELS[predicted_class_id]
        
        # Determine if it's bullying (anything not "Not Cyberbullying")
        is_bullying = predicted_label != "Not Cyberbullying"
        bullying_type = predicted_label.lower() if is_bullying else None
        
        print(f"Text: '{text}'")
        print(f"Prediction: {predicted_label} (is_bullying={is_bullying}, type={bullying_type})")
        
        return is_bullying, bullying_type
        
    except Exception as e:
        print(f"Error during prediction: {e}")
        return False, None

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
