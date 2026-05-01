import google.generativeai as genai

genai.configure(api_key="AIzaSyCbwSBQ2nhY9-zV1Vx7r6ZXyurrrCOLfpc")

model = genai.GenerativeModel("models/gemini-flash-lite-latest")

response = model.generate_content("Explain GDPR in 2 lines")
print(response.text)