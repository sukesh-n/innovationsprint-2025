import json
import csv

with open("evaluation_dataset.jsonl", "r") as jsonl_file, open("evaluation_dataset.csv", "w", newline="") as csv_file:
    writer = None
    for line in jsonl_file:
        record = json.loads(line)
        if writer is None:
            writer = csv.DictWriter(csv_file, fieldnames=record.keys())
            writer.writeheader()
        writer.writerow(record)

print("Converted evaluation_dataset.jsonl to evaluation_dataset.csv")
