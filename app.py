import os
from flask import Flask, render_template, request

UPLOAD_FOLDER = "uploads"
OUTPUT_FOLDER = "output"

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

import csv

def load_data(path):
    with open(path, newline="") as file:
        return list(csv.DictReader(file))

def clean_data(rows):
    clean_rows = []
    removed = 0
    for row in rows:
        try:
            if row["name"] and row["age"] and row["score"]:
                row["age"] = int(row["age"])
                row["score"] = int(row["score"])
                clean_rows.append(row)
            else:
                removed += 1
        except ValueError:
            removed += 1
    return clean_rows, removed

def save_data(rows, path):
    with open(path, "w", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

def calculate_summary(rows):
    scores = [row["score"] for row in rows]
    return {
        "rows": len(rows),
        "average": round(sum(scores) / len(scores), 2),
        "max": max(scores),
        "min": min(scores)
    }

@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        file = request.files["file"]
        file_path = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
        file.save(file_path)

        data = load_data(file_path)
        clean_rows, removed = clean_data(data)
        summary = calculate_summary(clean_rows)

        save_data(clean_rows, os.path.join(OUTPUT_FOLDER, "cleaned_output.csv"))

        return render_template(
            "index.html",
            summary=summary,
            removed=removed
        )

    return render_template("index.html")

if __name__ == "__main__":
    app.run(debug=True)