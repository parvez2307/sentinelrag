from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from qdrant_client.models import Filter, FieldCondition, MatchValue
import google.generativeai as genai
import time

# -------- CONFIG --------
COLLECTION = "policies"

genai.configure(api_key="AIzaSyCbwSBQ2nhY9-zV1Vx7r6ZXyurrrCOLfpc")
llm_model = genai.GenerativeModel("models/gemini-flash-lite-latest")

embed_model = SentenceTransformer("all-MiniLM-L6-v2")
client = QdrantClient(":memory:")


# -------- SAFE LLM CALL --------

def safe_generate(prompt, retries=3):
    for i in range(retries):
        try:
            response = llm_model.generate_content(prompt)
            return response.text
        except Exception as e:
            print(f"Retry {i+1}: {e}")
            time.sleep(2 * (i + 1))
    return "LLM failed after retries"


# -------- EMBEDDING --------

def embed(text):
    return embed_model.encode(text).tolist()


# -------- RETRIEVAL --------
def retrieve(query):
    vector = embed(query)

    policy_filter = Filter(
        must=[FieldCondition(key="type", match=MatchValue(value="policy"))]
    )

    regulation_filter = Filter(
        must=[FieldCondition(key="type", match=MatchValue(value="regulation"))]
    )

    policy_results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=3,
        query_filter=policy_filter
    )

    regulation_results = client.search(
        collection_name=COLLECTION,
        query_vector=vector,
        limit=5,
        query_filter=regulation_filter
    )

    policies = [r.payload for r in policy_results][:1]
    regulations = [r.payload for r in regulation_results][:2]

    return policies + regulations


# -------- CONTEXT BUILDER --------

def build_context(docs):
    policy_context = ""
    regulation_context = ""

    for doc in docs:
        if doc["type"] == "policy":
            policy_context += f"""
Policy ID: {doc['id']}
Content: {doc['text']}
"""
        else:
            regulation_context += f"""
Regulation ID: {doc['id']}
Content: {doc['text']}
"""

    return policy_context, regulation_context


# -------- AGENTS --------

def researcher_agent(policy_context, regulation_context, query):
    prompt = f"""
You are a compliance analyst.

Rules:
- Only use provided context
- Compare policy vs regulations

Policies:
{policy_context}

Regulations:
{regulation_context}

Question:
{query}

Output:
- Violations:
- Explanation:
- Risk:
"""
    return safe_generate(prompt)


def critic_agent(policy_context, regulation_context, initial_answer):
    prompt = f"""
You are a strict compliance critic.

Rules:
- Only use context
- Do NOT assume facts not present
- Identify overreach or unsupported claims

Policies:
{policy_context}

Regulations:
{regulation_context}

Initial Analysis:
{initial_answer}

Tasks:
1. Is analysis valid? (Yes/No)
2. List issues
3. Provide corrected reasoning

Output:
- Valid:
- Issues:
- Corrections:
"""
    return safe_generate(prompt)


def auditor_agent(policy_context, regulation_context, critic_output):
    prompt = f"""
You are a compliance auditor.

Rules:
- Use critic output as final authority
- Do NOT include speculative violations
- Separate confirmed vs potential risks

Policies:
{policy_context}

Regulations:
{regulation_context}

Critic Output:
{critic_output}

Tasks:
1. Confirmed violations (strong evidence)
2. Potential risks (uncertain)
3. Explanation
4. Risk level

Output JSON:
{{
  "confirmed_violations": [],
  "potential_risks": [],
  "explanation": "",
  "risk": ""
}}
"""
    return safe_generate(prompt)


# -------- MAIN --------

if __name__ == "__main__":
    query = "automated loan approval without explanation policy compliance GDPR EU AI Act"

    docs = retrieve(query)

    print("\n--- Retrieved Documents ---")
    for d in docs:
        print(d)

    policy_context, regulation_context = build_context(docs)

    print("\n--- Researcher Output ---")
    researcher_out = researcher_agent(policy_context, regulation_context, query)
    print(researcher_out)

    print("\n--- Critic Output ---")
    critic_out = critic_agent(policy_context, regulation_context, researcher_out)
    print(critic_out)

    print("\n--- Auditor Output ---")
    final_out = auditor_agent(policy_context, regulation_context, critic_out)
    print(final_out)

    client.close()