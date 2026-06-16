import json
import re
import sys
from pathlib import Path

import pandas as pd

I_PRONOUNS = {
    "i", "me", "my", "mine", "myself",
    "i'm", "i'll", "i've", "i'd",
}

WE_PRONOUNS = {
    "we", "us", "our", "ours", "ourselves",
    "we're", "we'll", "we've", "we'd",
}

if len(sys.argv) < 3:
    print("Uso:")
    print("python extract_pronoun_statements.py archivo.json SPEAKER_00")
    sys.exit(1)

json_file = sys.argv[1]
speaker = sys.argv[2]

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)


def normalize_text(text):
    return text.lower().replace("\u2019", "'").replace("\u2018", "'")


def tokenize(text):
    return re.findall(r"[a-z0-9']+", normalize_text(text))


def split_statements(text):
    parts = re.split(r"[.!?]+", text)
    return [part.strip() for part in parts if part.strip()]


rows = []

for i, segment in enumerate(data["segments"]):
    if segment.get("speaker") != speaker:
        continue

    text = segment["text"].strip()
    statements = split_statements(text) or [text]

    for j, statement in enumerate(statements):
        tokens = set(tokenize(statement))
        has_i = bool(tokens & I_PRONOUNS)
        has_we = bool(tokens & WE_PRONOUNS)
        i_count = sum(1 for token in tokenize(statement) if token in I_PRONOUNS)
        we_count = sum(1 for token in tokenize(statement) if token in WE_PRONOUNS)

        rows.append({
            "segment": i,
            "statement_index": j,
            "start": segment["start"],
            "end": segment["end"],
            "statement": statement,
            "is_i_statement": has_i,
            "is_we_statement": has_we,
            "i_pronoun_count": i_count,
            "we_pronoun_count": we_count,
        })

if not rows:
    print(f"No se encontraron segmentos para {speaker}")
    sys.exit(1)

details = pd.DataFrame(rows)

summary = pd.DataFrame([{
    "speaker": speaker,
    "i_statements": int(details["is_i_statement"].sum()),
    "we_statements": int(details["is_we_statement"].sum()),
    "i_pronoun_count": int(details["i_pronoun_count"].sum()),
    "we_pronoun_count": int(details["we_pronoun_count"].sum()),
    "total_statements": len(details),
}])

person = Path(json_file).with_suffix("")
summary_file = f"{person}_pronoun_summary.csv"
details_file = f"{person}_pronoun_statements.csv"

summary.to_csv(summary_file, index=False)
details.to_csv(details_file, index=False)

row = summary.iloc[0]
print(f"Speaker: {speaker}")
print(f"Enunciados con I: {row['i_statements']}")
print(f"Enunciados con WE: {row['we_statements']}")
print(f"Ocurrencias de pronombres I: {row['i_pronoun_count']}")
print(f"Ocurrencias de pronombres WE: {row['we_pronoun_count']}")
print(f"Total de enunciados analizados: {row['total_statements']}")
print(f"Generado: {summary_file}")
print(f"Generado: {details_file}")
