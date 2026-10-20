from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import json
import os

app = Flask(__name__)
CORS(app)

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# ---------------- LOAD DATA ----------------
ipc_df = pd.read_csv(os.path.join(DATA_DIR, "ipc_crime.csv")).fillna(0)
women_df = pd.read_csv(os.path.join(DATA_DIR, "women_crime.csv")).fillna(0)

ipc_df.columns = ipc_df.columns.str.strip()
women_df.columns = women_df.columns.str.strip()

with open(os.path.join(DATA_DIR, "ipc_sections.json"), encoding="utf-8") as f:
    ipc_sections = json.load(f)

with open(os.path.join(DATA_DIR, "legal_awareness.json"), encoding="utf-8") as f:
    legal_awareness = json.load(f)

with open(os.path.join(DATA_DIR, "legal_faqs.json"), encoding="utf-8") as f:
    legal_faqs = json.load(f)

with open(os.path.join(DATA_DIR, "helplines.json"), encoding="utf-8") as f:
    helplines = json.load(f)

# =======================
# 🔥 ROOT LANDING PAGE
# =======================
@app.route("/")
def landing():
    return jsonify({
        "project": "AI Lawyer – Legal Analytics & Assistance Platform",
        "status": "Backend is running successfully",
        "available_endpoints": [
            "/api/health",
            "/api/crime/summary",
            "/api/ipc/records",
            "/api/ipc/assistant/search",
            "/api/ipc/assistant/explain",
            "/api/women/dashboard",
            "/api/legal-awareness",
            "/api/legal-faqs",
            "/api/helplines",
            "/api/case/predict"
        ],
        "note": "This backend is running locally for project demonstration."
    })

# ---------------- HEALTH ----------------
@app.route("/api/health")
def health():
    return jsonify({
        "status": "Backend running",
        "ipc_rows": len(ipc_df),
        "women_rows": len(women_df),
        "ipc_sections": len(ipc_sections),
        "helplines": len(helplines)
    })

# ---------------- DASHBOARD ----------------
@app.route("/api/crime/summary")
def crime_summary():
    return jsonify(
        ipc_df.groupby("YEAR")["TOTAL IPC CRIMES"]
        .sum()
        .reset_index()
        .to_dict(orient="records")
    )

# ---------------- IPC RECORDS ----------------
@app.route("/api/ipc/records")
def ipc_records():
    return jsonify({
        "available_years": sorted(ipc_df["YEAR"].unique().tolist()),
        "available_states": sorted(ipc_df["STATE/UT"].unique().tolist())
    })

# ---------------- IPC SEARCH ----------------
@app.route("/api/ipc/assistant/search")
def ipc_assistant_search():
    query = request.args.get("q", "").lower()
    if not query:
        return jsonify([])

    results = [
        sec for sec in ipc_sections
        if query in sec["section"].lower()
        or query in sec["title"].lower()
        or query in sec["law_text"].lower()
    ][:5]

    return jsonify(results)

# ---------------- IPC EXPLAIN ----------------
@app.route("/api/ipc/assistant/explain", methods=["POST"])
def ipc_assistant_explain():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    section_no = payload.get("section")
    if not isinstance(section_no, str) or not section_no.strip():
        return jsonify({"error": "'section' must be a non-empty string."}), 400

    section = next((s for s in ipc_sections if s["section"] == section_no.strip()), None)
    if not section:
        return jsonify({"error": "Section not found"}), 404

    return jsonify({
        "section": section["section"],
        "title": section["title"],
        "law_text": section["law_text"],
        "explanation": (
            "This educational summary describes the supplied section data only. "
            "It is not legal advice and may not reflect the latest amendments."
        ),
        "disclaimer": "Check current official legislation and consult a qualified lawyer for advice.",
    })

# ---------------- WOMEN DASHBOARD ----------------
@app.route("/api/women/dashboard")
def women_dashboard():
    crime_cols = [
        "No. of Rape cases",
        "Kidnap And Assault",
        "Dowry Deaths",
        "Assault against women",
        "Assault against modesty of women",
        "Domestic violence",
        "Women Trafficking"
    ]

    df = women_df.copy()
    df[crime_cols] = df[crime_cols].apply(pd.to_numeric, errors="coerce").fillna(0)
    df["TOTAL"] = df[crime_cols].sum(axis=1)

    return jsonify({
        "state_wise": (
            df.groupby("State")["TOTAL"]
            .sum()
            .reset_index()
            .sort_values(by="TOTAL", ascending=False)
            .head(10)
            .to_dict(orient="records")
        )
    })

# ---------------- LEGAL AWARENESS ----------------
@app.route("/api/legal-awareness")
def get_legal_awareness():
    return jsonify(legal_awareness)

@app.route("/api/legal-faqs")
def get_legal_faqs():
    return jsonify(legal_faqs)

@app.route("/api/helplines")
def get_helplines():
    return jsonify(helplines)

# ---------------- CASE FACTORS (NON-PREDICTIVE) ----------------
@app.route("/api/case/predict", methods=["POST"])
def predict_case():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "A JSON object is required."}), 400

    evidence = payload.get("evidence_strength", "Moderate")
    past = payload.get("past_record", "None")
    valid_evidence = {"Limited", "Moderate", "Strong"}
    valid_past_records = {"None", "Minor", "Serious"}
    if evidence not in valid_evidence or past not in valid_past_records:
        return jsonify({
            "error": "evidence_strength must be Limited, Moderate, or Strong; past_record must be None, Minor, or Serious."
        }), 400

    return jsonify({
        "assessment_status": "educational_checklist_only",
        "possible_outcome": {
            "probability": "Not calculated",
            "result": "Not predicted",
            "basis": (
                "This prototype does not contain a validated legal-outcome model "
                "or a case dataset suitable for estimating conviction probabilities."
            )
        },
        "inputs": {
            "evidence_strength": evidence,
            "past_record": past,
        },
        "key_factors": [
            "Strength and admissibility of the available evidence",
            "Applicable law and the specific facts of the case",
            "Relevant and current judicial precedents",
            "Procedural requirements and jurisdiction"
        ],
        "next_steps": [
            "Organize relevant documents and evidence",
            "Check current official legislation and applicable precedents",
            "Consult a qualified lawyer about the specific circumstances"
        ],
        "disclaimer": (
            "Educational information only. This endpoint does not predict a case outcome, "
            "estimate a real probability, or provide legal advice."
        )
    })

# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(debug=True)

