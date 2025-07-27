import google.generativeai as genai

import os
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def call_gemini(prompt):
    model = genai.GenerativeModel("gemini-pro")
    response = model.generate_content(prompt)
    return response.text.strip()
