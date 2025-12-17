#!/usr/bin/env python3
"""Quick test script to verify model predictions"""

from detector import _predict_local_label, detect_cyberbullying
from api_client import classify_with_gemini, keyword_fallback_classifier

test_texts = [
    "you are stupid",
    "you idiot", 
    "you are ugly",
    "I hate you",
    "you loser",
    "shut up",
    "you're a moron",
    "dumbass",
    "hello friend",
    "have a nice day"
]

print("=" * 80)
print("LOCAL MODEL TEST")
print("=" * 80)
for text in test_texts:
    label = _predict_local_label(text)
    print(f"Text: '{text}' -> Local Model: {label}")

print("\n" + "=" * 80)
print("KEYWORD FALLBACK TEST")
print("=" * 80)
for text in test_texts:
    category, explanation = keyword_fallback_classifier(text)
    print(f"Text: '{text}' -> Keyword: {category} ({explanation})")

print("\n" + "=" * 80)
print("FULL DETECTION TEST (Local + API)")
print("=" * 80)
for text in test_texts:
    is_bullying, bully_type = detect_cyberbullying(text)
    result = f"BULLYING ({bully_type})" if is_bullying else "SAFE"
    print(f"Text: '{text}' -> {result}")
