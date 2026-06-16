import sys
from pathlib import Path

import pandas as pd

# --- Configuración ---

CANDIDATES = [
    "bachelet",
    "espinosa",
    "grossi",
    "grynspan",
    "sall",
]

DEBATES = [
    {
        "debate": "gwl",
        "words": {
            "bachelet": "gwl/bachelet_words.csv",
            "espinosa": "gwl/espinosa_words.csv",
            "sall": "gwl/sall_words.csv",
            "grynspan": "gwl/grynspan_words.csv",
        },
        "concepts": {
            "bachelet": "gwl/bachelet_concepts.csv",
            "espinosa": "gwl/espinosa_concepts.csv",
            "sall": "gwl/sall_concepts.csv",
            "grynspan": "gwl/grynspan_concepts.csv",
        },
    },
    # Agregar más debates aquí, por ejemplo:
    # {
    #     "debate": "gwl",
    #     "words": {
    #         "bachelet": "debates/gwl/bachelet_words.csv",
    #         ...
    #     },
    #     "concepts": { ... },
    # },
]

TERM_TYPES = ("words", "concepts")


def load_counts(filepath):
    df = pd.read_csv(filepath)
    return dict(zip(df["term"], df["count"]))


def merge_term_type(debate_config, term_type, base_dir):
    files = debate_config.get(term_type, {})
    counts_by_candidate = {}

    for candidate in CANDIDATES:
        filepath = files.get(candidate)
        if filepath is None:
            counts_by_candidate[candidate] = {}
            continue
        counts_by_candidate[candidate] = load_counts(base_dir / filepath)

    all_terms = set()
    for counts in counts_by_candidate.values():
        all_terms.update(counts.keys())

    rows = []
    for term in all_terms:
        row = {
            "word": term,
            "debate": debate_config["debate"],
        }
        total = 0
        for candidate in CANDIDATES:
            count = counts_by_candidate[candidate].get(term, 0)
            row[f"count_{candidate}"] = count
            total += count
        row["_total"] = total
        rows.append(row)

    df = pd.DataFrame(rows)
    df = df.sort_values("_total", ascending=False).drop(columns="_total")
    df.insert(0, "id", range(1, len(df) + 1))

    return df


def main():
    base_dir = Path(__file__).parent

    for debate_config in DEBATES:
        debate_name = debate_config["debate"]

        for term_type in TERM_TYPES:
            if term_type not in debate_config:
                continue

            df = merge_term_type(debate_config, term_type, base_dir)
            output_file = base_dir / f"{debate_name}_{term_type}.csv"
            df.to_csv(output_file, index=False)
            print(f"Generado: {output_file} ({len(df)} filas)")


if __name__ == "__main__":
    main()
