#!/usr/bin/env python3
"""Test the API classification endpoint"""

from api_client import get_detailed_classification

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
print("API ENDPOINT CLASSIFICATION TEST (get_detailed_classification)")
print("=" * 80)

for text in test_texts:
    result = get_detailed_classification(text)
    status = "🚨 BULLYING" if result['is_bullying'] else "✅ SAFE"
    print(f"\n{status}: '{text}'")
    print(f"  Final: {result['final_label']}")
    print(f"  Type: {result['bullying_type']}")
