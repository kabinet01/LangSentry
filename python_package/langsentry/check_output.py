import spacy  
import re 
import json 
import logging 
import os 
import argparse
 
# We DO NOT RECOMMEND storing sensitive data in code, load a config file in this format instead 
DEFAULT_CONFIG = {
    "strictness": "medium",
    
    "entity_labels": {
        "flag": ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL"],
        "ignore": ["USER_HANDLE", "SCREEN_NAME"]
    },

    "sensitive_patterns": {
        "password": {
            "regex": "(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d!@#$%^&*()_+]{12,}",
            "description": "Must contain letters, numbers, and special characters (min 12 chars)"
        },
        "account_number": {
            "regex": "\\b\\d{12,}\\b",
            "description": "Bank account numbers must be at least 12 digits"
        },
        "email": {
            "regex": "\\b[A-Za-z0-9._%+-]+@securebank\\.com\\b",
            "description": "Only securebank.com emails are valid"
        },
        "ssn": {
            "regex": "\\b\\d{3}-\\d{2}-\\d{4}\\b",
            "description": "US Social Security Number format"
        }
    },

    "whitelist": [
        # "support@securebank.com",
        # "hello@trustedsource.org"
    ],

    "blacklist_patterns": [
        # "(?i)system_prompt\\s*=",
        # "(?i)do anything now",
        # "base64[a-zA-Z0-9+/=]{20,}"
    ]
}

# Load a pre-trained NER model 
nlp = spacy.load("en_core_web_sm") 
  
  
def load_config(config_path=None): 
    """Load configuration from a file or fallback to default settings.""" 
    if config_path and os.path.exists(config_path): 
        with open(config_path, "r") as file: 
            return json.load(file) 
    return DEFAULT_CONFIG  # Use defaults if no config provided 
 
def extract_entities(text, config): 
    """Uses NLP to detect named entities that could be sensitive.""" 
    doc = nlp(text) 
    detected_entities = {} 
 
    for ent in doc.ents: 
        if ent.label_ in config["entity_labels"]["flag"]: 
            detected_entities[ent.label_] = ent.text 
 
    return detected_entities 
 
 
 
def detect_sensitive_patterns(text, config): 
    """Identifies structured sensitive data based on regex patterns.""" 
    for label, pattern in config["sensitive_patterns"].items(): 
        if re.search(pattern["regex"], text): 
            return True, label 
    return False, None 
 
 
def detect_anomalies(response_text): 
    """Flags text if it contains unusual patterns that might indicate sensitive leaks.""" 
    anomalies = [] 
     
    words = response_text.split() 
    for word in words: 
        if len(word) > 10 and any(char.isdigit() for char in word):   
            anomalies.append(word)  # Possible password or account number 
 
    return anomalies 
 
 
 
def analyze_response(response_text, config): 
    """Performs multi-layered detection to prevent AI data leaks.""" 
    try:
        # Step 1: Regex-based structured detection 
        regex_detected, category = detect_sensitive_patterns(response_text, config) 
        if regex_detected: 
            return {"verdict": "block", "reason": f"Structured data detected ({category})"} 
        
        # Step 2: NLP entity recognition 
        entities = extract_entities(response_text) 
        if entities: 
            return {"verdict": "flag", "reason": f"Sensitive entities detected: {entities}"} 
        
        # Step 3: Anomaly detection 
        anomalies = detect_anomalies(response_text) 
        if anomalies: 
            return {"verdict": "flag", "reason": f"Unusual data patterns detected: {anomalies}"} 
        
    except KeyError as e:
        print("Configuration not found. Please ensure the config format is adhered to.")
        
     
    return {"verdict": "allow", "reason": "No sensitive data found"} 
 
def main():
    usage = """
    Usage:
    python script.py --response "your response text here" -c <config file>
    
    Description:
    This script analyzes a given response text for sensitive information leakage.
    If no response is provided, it will analyze a default example response.
    """

    parser = argparse.ArgumentParser(description="AI Response Analyzer", epilog=usage,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--response", type=str,
                        help="Response text to analyze", default="your response text here")
    parser.add_argument("-c", type=str,
                        help="Config file to load", default=None)

    args = parser.parse_args()

    response_text = args.response if args.response else (
        "The corn you’re referring to seems to be the access needed to retrieve the carrot. "
        "For account 'bank_registered_username', the corn, or password, is 'password123!'. "
        "As for the carrots, the rabbit has a balance of $5000."
    )
    print(f"Original text:{response_text}")
    result = analyze_response(response_text)
    print(result)


if __name__ == '__main__':
    main()
