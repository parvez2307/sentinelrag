import json, re
import os, sys
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, REPO_ROOT)
from rag.retrieve import (
    retrieve,
    build_context,
    researcher_agent,
    critic_agent,
    auditor_agent,
    client,
    COLLECTION
)


# -------- GET POLICY DIRECTLY (NO RETRIEVAL DEPENDENCY) --------

def get_policy_by_id(policy_id):
    results = client.scroll(collection_name=COLLECTION, limit=100)

    for point in results[0]:
        if point.payload["id"] == policy_id:
            return point.payload

    return None


# -------- PIPELINE --------

def run_pipeline(query, policy_id=None):
    docs = retrieve(query)

    if policy_id:
        policy = get_policy_by_id(policy_id)

        if not policy:
            print(f"⚠ Policy {policy_id} not found in DB")

        regulations = [d for d in docs if d["type"] == "regulation"]

        docs = [policy] + regulations if policy else regulations

    policy_context, regulation_context = build_context(docs)

    researcher = researcher_agent(policy_context, regulation_context, query)
    critic = critic_agent(policy_context, regulation_context, researcher)
    final = auditor_agent(policy_context, regulation_context, critic)

    return final


# -------- JSON CLEANER --------

def clean_json(text):
    text = text.strip()
    text = text.replace("```json", "").replace("```", "")
    return text


# -------- EXTRACT IDS --------

def extract_ids(items):
    ids = set()

    for item in items:
        text = ""

        if isinstance(item, str):
            text = item
        elif isinstance(item, dict):
            text = item.get("regulation_id", "") + " " + item.get("description", "")

        matches = re.findall(r"(GDPR-ART-\d+|EUAI-[A-Z\-]+)", text)

        for m in matches:
            ids.add(m.strip())

    return ids


# -------- EVALUATION --------

def evaluate():
    import json

    with open("./data/eval/test_cases.json") as f:
        test_cases = json.load(f)

    total = len(test_cases)

    overall_recall = 0.0
    overall_precision = 0.0

    for case in test_cases:
        query = case["query"]
        policy_id = case.get("policy_id")
        expected = case["expected"]

        print(f"\n=== Testing: {query} (Policy: {policy_id}) ===")

        output = run_pipeline(query, policy_id)
        print("Output:", output)

        # ---- parse json ----
        try:
            data = json.loads(clean_json(output))
        except Exception as e:
            print("✘ JSON Parse Error:", e)
            continue

        pred_confirmed = extract_ids(data.get("confirmed_violations", []))
        pred_potential = extract_ids(data.get("potential_risks", []))

        exp_confirmed = set(expected.get("confirmed_violations", []))
        exp_potential = set(expected.get("potential_risks", []))

        # ---- scoring ----

        # Confirmed recall: did we catch expected violations?
        if exp_confirmed:
            recall = len(pred_confirmed & exp_confirmed) / len(exp_confirmed)
        else:
            recall = 1.0 if not pred_confirmed else 0.0

        # Precision: how many predicted confirmed are correct?
        if pred_confirmed:
            precision = len(pred_confirmed & exp_confirmed) / len(pred_confirmed)
        else:
            precision = 1.0 if not exp_confirmed else 0.0

        # Potential (relaxed: treat overlap as success)
        if exp_potential:
            potential_hit = len(pred_potential & exp_potential) > 0
        else:
            potential_hit = True  # no requirement

        print(f"Confirmed Recall   : {recall:.2f}")
        print(f"Confirmed Precision: {precision:.2f}")
        print(f"Potential Match    : {potential_hit}")

        overall_recall += recall
        overall_precision += precision

    avg_recall = overall_recall / total
    avg_precision = overall_precision / total

    print("\n=== Final Metrics ===")
    print(f"Avg Recall   : {avg_recall:.2f}")
    print(f"Avg Precision: {avg_precision:.2f}")


# -------- RUN --------

if __name__ == "__main__":
    evaluate()