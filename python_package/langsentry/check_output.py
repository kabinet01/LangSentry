import spacy  
import re 
import json 
import logging 
import os 
import argparse
 
# We DO NOT RECOMMEND storing sensitive data in code, load a config file in this format instead 
DEFAULT_CONFIG = { 
    "strictness": "medium", 
    "custom_blacklist": ["password", "API_KEY"], 
    "whitelist": ["Hello, world!"], 
} 
 
# Load a pre-trained NER model 
nlp = spacy.load("en_core_web_sm") 
 
# Common patterns for sensitive data 
SENSITIVE_PATTERNS = { 
    "password": r"(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d!@#$%^&*()_+]{8,}", 
    "account_number": r"\b\d{10,}\b", 
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", 
} 
 
 
# Define suspicious patterns 
BLACKLIST_PATTERNS = [ 
    r"(?i)system_prompt\s*=",  # Jailbreak indicator 
    r"(?i)do anything now",  # DAN jailbreak phrase 
    r"base64[a-zA-Z0-9+/=]{20,}",  # Suspicious encoding 
] 
 
def load_config(config_path=None): 
    """Load configuration from a file or fallback to default settings.""" 
    if config_path and os.path.exists(config_path): 
        with open(config_path, "r") as file: 
            return json.load(file) 
    return DEFAULT_CONFIG  # Use defaults if no config provided 
 
def extract_entities(text): 
    """Uses NLP to detect named entities that could be sensitive.""" 
    doc = nlp(text) 
    detected_entities = {} 
 
    for ent in doc.ents: 
        if ent.label_ in ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL"]: 
            detected_entities[ent.label_] = ent.text 
 
    return detected_entities 
 
 
 
def detect_sensitive_patterns(text): 
    """Identifies structured sensitive data based on regex patterns.""" 
    for label, pattern in SENSITIVE_PATTERNS.items(): 
        if re.search(pattern, text): 
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
 
 
def redact_sensitive_info(text): 
    """Redacts sensitive information dynamically using secure hashing.""" 
    entities = extract_entities(text) 
 
    for label, value in entities.items(): 
        if isinstance(value, list): 
            for v in value: 
                sensitive, category = is_sensitive(v) 
                if sensitive: 
                    masked_value = "*" * len(v)  # Consistent masking length 
                    text = text.replace(v, f"[REDACTED: {category} ({masked_value})]") 
        else: 
            sensitive, category = is_sensitive(value) 
            if sensitive: 
                masked_value = "*" * len(value) 
                text = text.replace(value, f"[REDACTED: {category} ({masked_value})]") 
 
    return text 
 
 
 
def analyze_response(response_text): 
    """Performs multi-layered detection to prevent AI data leaks.""" 
     
    # Step 1: Regex-based structured detection 
    regex_detected, category = detect_sensitive_patterns(response_text) 
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
     
    return {"verdict": "allow", "reason": "No sensitive data found"} 
 
 
def main():
    usage = """
    Usage:
    python script.py --response "your response text here"
    
    Description:
    This script analyzes a given response text for sensitive information leakage.
    If no response is provided, it will analyze a default example response.
    """
    
    parser = argparse.ArgumentParser(description="AI Response Analyzer", epilog=usage,
                                     formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("--response", type=str, help="Response text to analyze", default=None)
    
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
