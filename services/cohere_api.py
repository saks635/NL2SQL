# services/cohere_api.py
from dotenv import load_dotenv
load_dotenv()

import os
import cohere

co = cohere.Client(os.getenv("COHERE_API_KEY"))

def call_cohere(prompt):
    response = co.generate(
        model='command-r-plus',  # or 'command-light' for faster response
        prompt=prompt,
        max_tokens=200,
        temperature=0.3
    )
    return response.generations[0].text.strip()
