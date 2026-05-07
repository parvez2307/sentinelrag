import os

os.environ.pop("GOOGLE_APPLICATION_CREDENTIALS", None)

from dotenv import load_dotenv
load_dotenv()

import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

response = genai.embed_content(
    model="models/gemini-embedding-001",
    content="hello world"
)

print("Embedding size:", len(response["embedding"]))