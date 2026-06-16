import json
import re
import sys
from collections import Counter

import pandas as pd
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

if len(sys.argv) < 3:
    print("Uso:")
    print("python extract_concepts.py archivo.json SPEAKER_00")
    sys.exit(1)

json_file = sys.argv[1]
speaker = sys.argv[2]

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

texts = []

for segment in data["segments"]:
    if segment.get("speaker") == speaker:
        texts.append(segment["text"])

def normalize_text(text):
    return text.lower().replace("\u2019", "'").replace("\u2018", "'")


def tokenize(text):
    return re.findall(r"[a-z0-9']+", normalize_text(text))


def extract_words(texts, min_count=2):
    counts = Counter()

    for text in texts:
        for word in tokenize(text):
            if word in ENGLISH_STOP_WORDS:
                continue
            counts[word] += 1

    results = pd.DataFrame(
        {"term": list(counts.keys()), "count": list(counts.values())}
    )

    return results[results["count"] >= min_count].sort_values(
        "count",
        ascending=False,
    )


def extract_literal_phrases(texts, min_words=2, max_words=3, min_count=2):
    counts = Counter()

    for text in texts:
        words = tokenize(text)
        for n in range(min_words, max_words + 1):
            for i in range(len(words) - n + 1):
                window = words[i : i + n]
                if any(word in ENGLISH_STOP_WORDS for word in window):
                    continue
                counts[" ".join(window)] += 1

    results = pd.DataFrame(
        {"term": list(counts.keys()), "count": list(counts.values())}
    )

    return results[results["count"] >= min_count].sort_values(
        "count",
        ascending=False,
    )


words = extract_words(texts)
concepts = extract_literal_phrases(texts)

person=json_file.replace('.json', '')

words_file = f"{person}_words.csv"
concepts_file = f"{person}_concepts.csv"

words.to_csv(words_file, index=False)
concepts.to_csv(concepts_file, index=False)

print(f"Generado: {words_file} ({len(words)} palabras)")
print(f"Generado: {concepts_file} ({len(concepts)} conceptos)")
