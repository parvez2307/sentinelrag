import json
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

from rag.retrieve import (
    retrieve,
    build_context,
    researcher_agent,
    critic_agent,
    auditor_agent,
    client,
    COLLECTION
)

app = FastAPI(title="SentinelRAG API", version="1.0")

@app.on_event("startup")
def startup_event():
    from rag.ingest_all import ingest_all
    ingest_all()


@app.get("/")
def root():
    return {"message": "SentinelRAG API running", "docs": "/docs"}


# -------- REQUEST SCHEMA --------

class AuditRequest(BaseModel):
    query: str
    policy_id: str | None = None


# -------- HELPERS --------

def get_policy_by_id(policy_id):
    results = client.scroll(collection_name=COLLECTION, limit=200)

    for point in results[0]:
        if point.payload["id"] == policy_id:
            return point.payload
    return None


def clean_json(text):
    return text.strip().replace("```json", "").replace("```", "")


def extract_ids(items):
    ids = set()
    for item in items:
        text = ""
        if isinstance(item, str):
            text = item
        elif isinstance(item, dict):
            text = item.get("regulation_id", "") + " " + item.get("issue", "") + " " + item.get("description", "")

        matches = re.findall(r"(GDPR-ART-\d+|EUAI-[A-Z\-]+)", text)
        for m in matches:
            ids.add(m.strip())
    return list(ids)


# -------- CORE PIPELINE --------

def run_pipeline(query, policy_id=None):
    docs = retrieve(query)

    if policy_id:
        policy = get_policy_by_id(policy_id)
        if not policy:
            raise ValueError(f"Policy {policy_id} not found")

        regulations = [d for d in docs if d["type"] == "regulation"]
        docs = [policy] + regulations

    policy_context, regulation_context = build_context(docs)

    researcher = researcher_agent(policy_context, regulation_context, query)
    critic = critic_agent(policy_context, regulation_context, researcher)
    final = auditor_agent(policy_context, regulation_context, critic)

    return {
        "retrieved_docs": docs,
        "researcher": researcher,
        "critic": critic,
        "final_raw": final
    }


# -------- ENDPOINT --------

@app.post("/audit")
def audit(request: AuditRequest):
    try:
        result = run_pipeline(request.query, request.policy_id)

        # parse final JSON
        try:
            parsed = json.loads(clean_json(result["final_raw"]))
        except:
            parsed = {"raw_output": result["final_raw"]}

        # normalize output
        parsed["confirmed_violations_normalized"] = extract_ids(parsed.get("confirmed_violations", []))
        parsed["potential_risks_normalized"] = extract_ids(parsed.get("potential_risks", []))

        return {
            "status": "success",
            "input": request.dict(),
            "output": parsed,
            "trace": {
                "researcher": result["researcher"],
                "critic": result["critic"]
            }
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# -------- HEALTH CHECK --------

@app.get("/health")
def health():
    return {"status": "ok"}