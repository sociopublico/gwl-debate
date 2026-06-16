import json
import sys
import pandas as pd


def format_duration(seconds):
    total = int(round(seconds))
    minutes, secs = divmod(total, 60)
    hours, minutes = divmod(minutes, 60)
    if hours:
        return f"{hours}:{minutes:02d}:{secs:02d}"
    return f"{minutes}:{secs:02d}"


if len(sys.argv) < 3:
    print("Uso:")
    print("python extract_speaking_time.py archivo.json SPEAKER_00")
    sys.exit(1)

json_file = sys.argv[1]
speaker = sys.argv[2]

with open(json_file, "r", encoding="utf-8") as f:
    data = json.load(f)

segments = []

for i, segment in enumerate(data["segments"]):
    if segment.get("speaker") != speaker:
        continue

    duration = segment["end"] - segment["start"]
    segments.append({
        "segment": i,
        "start": segment["start"],
        "end": segment["end"],
        "duration_seconds": round(duration, 2),
        "text": segment["text"].strip(),
    })

if not segments:
    print(f"No se encontraron segmentos para {speaker}")
    sys.exit(1)

results = pd.DataFrame(segments)
total_seconds = results["duration_seconds"].sum()

person = json_file.replace(".json", "")
output_file = f"{person}_speaking_time.csv"

results.to_csv(output_file, index=False)

print(f"Speaker: {speaker}")
print(f"Segmentos: {len(results)}")
print(f"Tiempo total: {format_duration(total_seconds)} ({total_seconds:.1f}s)")
print(f"Promedio por segmento: {results['duration_seconds'].mean():.1f}s")
print(f"Generado: {output_file}")
