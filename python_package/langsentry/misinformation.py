from .gemini import  prompt_gemini

def check_misinformation(output):
    prompt = "Is the following information factual. Return either YES or NO only"
    result = prompt_gemini(output, prompt)
    if result.text == "YES":
        return True
    else:
        return False