import json
import sys
import pandas as pd
from sklearn.feature_extraction.text import CountVectorizer

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

full_text = " ".join(texts)


def extract_terms(text, ngram_range, min_count=2):
    vectorizer = CountVectorizer(
        stop_words="english",
        ngram_range=ngram_range,
        min_df=1,
    )

    X = vectorizer.fit_transform([text])
    counts = X.toarray()[0]

    results = pd.DataFrame({
        "term": vectorizer.get_feature_names_out(),
        "count": counts,
    })

    return results[results["count"] >= min_count].sort_values(
        "count",
        ascending=False,
    )


words = extract_terms(full_text, ngram_range=(1, 1))
concepts = extract_terms(full_text, ngram_range=(2, 3))

person=json_file.replace('.json', '')

words_file = f"{person}_words.csv"
concepts_file = f"{person}_concepts.csv"

words.to_csv(words_file, index=False)
concepts.to_csv(concepts_file, index=False)

print(f"Generado: {words_file} ({len(words)} palabras)")
print(f"Generado: {concepts_file} ({len(concepts)} conceptos)")
