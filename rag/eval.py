import json
import re
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


# -------- GET POLICY DIRECTLY --------

def get_policy_by_id(policy_id):

    points, _ = client.scroll(
        collection_name=COLLECTION,
        limit=500
    )

    for point in points:

        payload = point.payload

        if payload.get("id") == policy_id:
            return payload

    return None


# -------- PIPELINE --------

def run_pipeline(query, policy_id=None):

    docs = retrieve(query)

    if policy_id:

        policy = get_policy_by_id(policy_id)

        if policy:

            regulations = [
                d for d in docs
                if d["type"] == "regulation"
            ]

            docs = [policy] + regulations

    policy_context, regulation_context = build_context(docs)

    researcher = researcher_agent(
        policy_context,
        regulation_context,
        query
    )

    critic = critic_agent(
        policy_context,
        regulation_context,
        researcher
    )

    final = auditor_agent(
        policy_context,
        regulation_context,
        critic
    )

    return final


# -------- JSON CLEANER --------

def clean_json(text):

    text = text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")

    start = text.find("{")
    end = text.rfind("}")

    if start != -1 and end != -1:
        text = text[start:end + 1]

    return text


# -------- EXTRACT IDS --------

def extract_ids(items):

    ids = set()

    pattern = r"(GDPR-ART-\d+|EUAI-[A-Z\-]+)"

    for item in items:

        if isinstance(item, str):

            matches = re.findall(pattern, item)

            for m in matches:
                ids.add(m.strip())

        elif isinstance(item, dict):

            combined = json.dumps(item)

            matches = re.findall(pattern, combined)

            for m in matches:
                ids.add(m.strip())

    return ids


# -------- EVALUATION --------

def evaluate():

    with open("./data/eval/test_cases.json", "r", encoding="utf-8") as f:
        test_cases = json.load(f)

    total = len(test_cases)

    overall_recall = 0.0
    overall_precision = 0.0

    for case in test_cases:

        query = case["query"]

        policy_id = case.get("policy_id")

        expected = case["expected"]

        print(
            f"\n=== Testing: {query} "
            f"(Policy: {policy_id}) ==="
        )

        try:

            output = run_pipeline(query, policy_id)

            print("Output:", output)

        except Exception as e:

            print("✘ Pipeline Error:", e)

            continue

        # -------- PARSE JSON --------

        try:

            cleaned = clean_json(output)

            data = json.loads(cleaned)

        except Exception as e:

            print("✘ JSON Parse Error:", e)

            continue

        # -------- PREDICTIONS --------

        pred_confirmed = extract_ids(
            data.get("confirmed_violations", [])
        )

        pred_potential = extract_ids(
            data.get("potential_risks", [])
        )

        # -------- EXPECTED --------

        exp_confirmed = set(
            expected.get("confirmed_violations", [])
        )

        exp_potential = set(
            expected.get("potential_risks", [])
        )

        # -------- RECALL --------

        if exp_confirmed:

            recall = (
                len(pred_confirmed & exp_confirmed)
                / len(exp_confirmed)
            )

        else:

            recall = (
                1.0 if not pred_confirmed else 0.0
            )

        # -------- PRECISION --------

        if pred_confirmed:

            precision = (
                len(pred_confirmed & exp_confirmed)
                / len(pred_confirmed)
            )

        else:

            precision = (
                1.0 if not exp_confirmed else 0.0
            )

        # -------- POTENTIAL MATCH --------

        if exp_potential:

            potential_hit = (
                len(pred_potential & exp_potential) > 0
            )

        else:

            potential_hit = (
                len(pred_potential) == 0
            )

        print(f"Confirmed Recall   : {recall:.2f}")

        print(f"Confirmed Precision: {precision:.2f}")

        print(f"Potential Match    : {potential_hit}")

        overall_recall += recall
        overall_precision += precision

    # -------- FINAL METRICS --------

    avg_recall = overall_recall / total

    avg_precision = overall_precision / total

    print("\n=== Final Metrics ===")

    print(f"Avg Recall   : {avg_recall:.2f}")

    print(f"Avg Precision: {avg_precision:.2f}")


# -------- RUN --------

if __name__ == "__main__":

    evaluate()

    try:
        client.close()
    except:
        pass