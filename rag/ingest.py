import json
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import VectorParams, Distance, PointStruct

# -------- CONFIG --------
COLLECTION = "policies"

# Init models
embed_model = SentenceTransformer("all-MiniLM-L6-v2")

# Qdrant local (persistent)
client = QdrantClient(path="./qdrant_data")


# -------- HELPERS --------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def embed(text):
    return embed_model.encode(text).tolist()


def extract_text(item):
    # policies
    if "text" in item:
        return item["text"]

    # regulations
    elif "rules" in item:
        return " ".join(item["rules"])

    return str(item)


def get_existing_collections():
    return [c.name for c in client.get_collections().collections]


def create_collection_if_not_exists(vector_size):
    if COLLECTION not in get_existing_collections():
        client.create_collection(
            collection_name=COLLECTION,
            vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE),
        )


# -------- INGEST --------

def ingest(file_path, start_id=0):
    data = load_json(file_path)

    points = []

    for idx, item in enumerate(data):
        text = extract_text(item)
        vector = embed(text)

        point = PointStruct(
            id=start_id + idx,
            vector=vector,
            payload={
                "id": item["id"],
                "text": text,
                "type": "policy" if "text" in item else "regulation"
            }
        )

        points.append(point)

    create_collection_if_not_exists(len(points[0].vector))

    client.upsert(collection_name=COLLECTION, points=points)

    return len(points)


# -------- MAIN --------

if __name__ == "__main__":
    try:
        total = 0

        total += ingest("./data/policies/non_compliant.json", start_id=0)
        total += ingest("./data/policies/compliant.json", start_id=100)
        total += ingest("./data/policies/edge_cases.json", start_id=200)
        total += ingest("./data/policies/expanded_policies.json", start_id=300)

        total += ingest("./data/regulations/gdpr.json", start_id=1000)
        total += ingest("./data/regulations/eu_ai_act.json", start_id=2000)

        print(f"Ingested total {total} documents.")

    finally:
        try:
            client.close()
        except:
            pass