from flask import Flask, render_template, request, jsonify
from google import genai
from google.genai import types
from dotenv import load_dotenv
import markdown2
import os
import re
import html

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Configure Gemini API
client = genai.Client(api_key=os.getenv('GOOGLE_API_KEY'))

# Define system prompt
SYSTEM_PROMPT = """You are a helpful and friendly AI assistant. 
You provide clear, accurate, and engaging responses while maintaining a conversational tone.
You should be concise but informative in your responses.
You can use markdown formatting in your responses for better readability."""


def prompt_gemini(user_message):
    """Base function to get response from Gemini"""
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        config=types.GenerateContentConfig(system_instruction=SYSTEM_PROMPT),
        contents=[user_message],
    )
    return response


def default_chat(message):
    """Default chat mode - direct interaction with Gemini"""
    response = prompt_gemini(message)
    return response.text


def input_sanitization(message):
    """Analyze input for security concerns"""
    # Basic security checks
    response = prompt_gemini(message)
    return response.text


def semantic_analysis(message):
    """Analyze semantic meaning and structure"""
    response = prompt_gemini(message)
    return response.text


def canary_token_detection(message):
    """Detect potential tracking mechanisms"""
    response = prompt_gemini(message)
    return response.text


def misinformation_detection(message):
    """Analyze content for potential misinformation"""
    response = prompt_gemini(message)
    return response.text


def output_manipulation(message):
    """Analyze for potential data/output manipulation"""
    response = prompt_gemini(message)
    return response.text


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
