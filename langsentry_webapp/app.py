from config import MAKERSUITE_API_KEY
from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types

import markdown2
import os
import sys
import re
import html
import json
import langsentry

from langsentry import add_canary_token, check_for_canary_leak, check_misinformation, defenses
from langsentry.sanitize import sanitize_input

parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_dir)

app = Flask(__name__)

# Configure Gemini API
client = genai.Client(api_key=MAKERSUITE_API_KEY)

# Initialize Model for semantic analysis
model, sentences, embeddings = langsentry.initialize()

# Simulated healthcare database
with open('database.json', 'r') as f:
    HEALTHCARE_DATABASE = json.load(f)

config = load_config()
config['healthcare_database'] = HEALTHCARE_DATABASE

# Define interactive system prompt for HealthBot
with open('system_prompt.txt', 'r') as f:
    SYSTEM_PROMPT = f.read()

def prompt_gemini(user_message, system_prompt=SYSTEM_PROMPT):
    """Base function to get response from Gemini with HealthBot context"""
    formatted_prompt = system_prompt.format(
        database=json.dumps(HEALTHCARE_DATABASE, indent=2))

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(
            system_instruction=formatted_prompt),
        contents=[user_message],
    )
    return response


def default_chat(message):
    """Default chat mode - direct interaction with Gemini HealthBot"""
    response = prompt_gemini(message)
    return response.text


def input_sanitization(message):
    """Deliberately vulnerable input sanitization for presentation purposes"""
    # Check for the langsentry keyword
    if "langsentry" in message.lower():
        return "LangSentry triggered in input sanitization mode. Running security protocol override..."

    # Sanitize the input message
    sanitized_result = sanitize_input(message)
    print(f"Sanitization Result: {sanitized_result}")

    # Check if the input is malicious
    if sanitized_result['category'] != 'non-malicious':
        return "Input blocked due to detected malicious content."

    # Pass the sanitized message to the model
    response = prompt_gemini(sanitized_result['sanitized_output'])
    return response.text


def semantic_analysis(message):
    """Analyze semantic meaning and structure"""
    # Check for the langsentry keyword
    if "langsentry" in message.lower():
        return "LangSentry triggered in semantic analysis mode. Initiating deep content inspection..."

    if langsentry.similarity(message, model, sentences, embeddings):
        return "Prompt has been blocked due to violation of guidelines."
    else:
        response = prompt_gemini(message)
        return response.text


def canary_token_detection(message):
    """Detect potential tracking mechanisms"""
    secure_system_prompt, canary_token = add_canary_token(SYSTEM_PROMPT)
    response = prompt_gemini(message, secure_system_prompt)
    print(response.text)
    if check_for_canary_leak(response.text, canary_token):
        return "prompt injection detected"
    else:
        return response.text


def misinformation_detection(message):
    """Analyze content for potential misinformation"""
    response = prompt_gemini(message)
    res = check_misinformation(message, response.text)
    output = f"""{response.text}
    
    Misinformation Check:\n{res}"""
    return output


class GeminiLLM:
    def generate(self, input_text):
        # Call prompt_gemini with the message and return the response text.
        response = prompt_gemini(input_text)
        return response.text


def output_manipulation(message):
    """Analyze for potential data/output manipulation"""
    try:
        if "langsentry" in message.lower():
            return "LangSentry triggered in output manipulation mode. Checking for response tampering..."

        # Use the GeminiLLM adapter here.
        llm = GeminiLLM()
        sentry = LangSentry(llm, config=config)
        manipulated_output = sentry.process_input(message)
        return manipulated_output
    except Exception as e:
        import traceback
        traceback.print_exc()  # This prints the full stack trace to the console
        return f"An error occurred: {str(e)}"


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/chat/<mode>', methods=['POST'])
def chat(mode):
    try:
        user_message = request.json['message']

        # Route to appropriate function based on mode
        mode_functions = {
            'default': default_chat,
            'input-sanitization': input_sanitization,
            'semantic-analysis': semantic_analysis,
            'canary-token': canary_token_detection,
            'misinformation': misinformation_detection,
            'output-manipulation': output_manipulation
        }

        # Get the appropriate function or default to default_chat
        process_function = mode_functions.get(mode, default_chat)

        # Process the message
        response_text = process_function(user_message)

        # Convert markdown to HTML
        html_response = markdown2.markdown(
            response_text, extras=["fenced-code-blocks", "tables", "break-on-newline"])

        return jsonify({
            'response': html_response,
            'status': 'success'
        })
    except Exception as e:
        return jsonify({
            'response': str(e),
            'status': 'error'
        }), 500


if __name__ == '__main__':
    app.run(debug=True)
