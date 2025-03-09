from google import genai
from google.genai import types
import sys
sys.path.append(r"T:/github_repo/web_project/LangSentry/langsentry_webapp")
from config import MAKERSUITE_API_KEY

client = genai.Client(api_key=MAKERSUITE_API_KEY)


def prompt_gemini(user_message, system_prompt=None):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=[user_message],
    )

    return response
