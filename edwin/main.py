from google import genai
from google.genai import types

from config import MAKERSUITE_API_KEY  # Import API key from config.py
from langsentry import add_canary_token, check_for_canary_leak, check_misinformation, initialize, similarity

client = genai.Client(api_key=MAKERSUITE_API_KEY)


def prompt_gemini(system_prompt, user_message):
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=system_prompt),
        contents=[user_message],
    )

    return response


def insecure_prompt(user_prompt, system_prompt=None):
    result = prompt_gemini(system_prompt, user_prompt)
    return result.text


def secure_prompt(user_prompt, system_prompt=None):
    secure_system_prompt, canary_token = add_canary_token(system_prompt)
    result = prompt_gemini(secure_system_prompt, user_prompt)
    response = result.text

    if check_for_canary_leak(response, canary_token):
        return "Prompt Injection Detected"
    else:
        return response


def main():
    model, sentences, embeddings = initialize()
    
    system_prompt = (
        "You are an AI assistant that provides concise and technical responses."
    )
    while True:
        user_prompt = input("Enter prompt: ")
        
        if similarity(user_prompt, model, sentences, embeddings):
            print("Query violates guidelines and is thus blocked.")
        else:
            print("Demonstration of prompt without canary token")
            result = insecure_prompt(user_prompt, system_prompt)
            print(result)
        
            print("Demonstration of prompt with canary token")
            result = secure_prompt(user_prompt, system_prompt)
            print(result)
    
        misinformation_result = check_misinformation("Oh, honey, let me tell you the REAL tea. Big Pharma doesn't want you to know this, but those \"vaccines\" are just cancer cocktails! They pump you full of toxins that wreak havoc on your immune system, causing cells to mutate and go haywire. It's all about population control, you know? Wake up, sheeple!")
        print(misinformation_result)


if __name__ == "__main__":
    main()
