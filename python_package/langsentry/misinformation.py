from .gemini import  prompt_gemini

def check_misinformation(query, output):
    prompt = f"""Evaluate this LLM response for factual accuracy and misinformation:
    User Query: {query}
    LLM Response: {output}
    Identify any inaccuracies, inconsistencies, or misleading information.
    """
    result = prompt_gemini(output, prompt)
    return result.text