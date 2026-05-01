import sys
sys.path.append("./") 
from rag.ingest import ingest

def ingest_all():
    total = 0

    total += ingest("data/policies/non_compliant.json", start_id=0)
    total += ingest("data/policies/compliant.json", start_id=100)
    total += ingest("data/policies/edge_cases.json", start_id=200)
    total += ingest("data/policies/expanded_policies.json", start_id=300)

    total += ingest("data/regulations/gdpr.json", start_id=1000)
    total += ingest("data/regulations/eu_ai_act.json", start_id=2000)

    print(f"[Startup] Ingested {total} documents")