import json
import os
from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# -------- CONFIG --------

COLLECTION = "policies"

# Use local persistent DB
client = QdrantClient(path="./qdrant_data")


# -------- EMBEDDING --------

def embed_text(text):
    response = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
        task_type="retrieval_document"
    )
    return response["embedding"]


# -------- HELPERS --------

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def extract_text(item):
    if "text" in item:
        return item["text"]

    elif "rules" in item:
        return " ".join(item["rules"])

    return str(item)


def get_existing_collections():
    return [c.name for c in client.get_collections().collections]


def recreate_collection():
    existing = get_existing_collections()

    if COLLECTION in existing:
        client.delete_collection(COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(
            size=3072,
            distance=Distance.COSINE
        ),
    )


# -------- INGEST --------

def ingest(file_path, start_id=0):
    data = load_json(file_path)

    points = []

    for idx, item in enumerate(data):

        text = extract_text(item)

        vector = embed_text(text)

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

    client.upsert(
        collection_name=COLLECTION,
        points=points
    )

    return len(points)


# -------- MAIN --------

if __name__ == "__main__":

    try:

        recreate_collection()

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