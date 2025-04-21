import openai
import os
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def ask_coach(question: str, athlete_data: dict) -> str:
    prompt = f"""You are a professional triathlon coach AI. Use the following athlete data to give advice:\n\n{athlete_data}\n\nQuestion: {question}\n\nCoach:"""
    try:
        response = openai.Completion.create(
            engine="text-davinci-003",
            prompt=prompt,
            max_tokens=150,
            temperature=0.7
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"Error retrieving coach response: {e}"
