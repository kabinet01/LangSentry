import spacy  
import re 
import json 
import logging 
import os 
import argparse
 
INDUSTRY_PROFILES = {
    "finance": {
        "flag": ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL", "ACCOUNT_NUMBER", "SSN"],
        "ignore": ["USER_HANDLE", "SCREEN_NAME"]
    },
    "healthcare": {
        "flag": ["PERSON", "ORG", "GPE", "DATE", "CARDINAL", "MEDICAL_RECORD", "DISEASE", "HEALTHCARE_PROVIDER"],
        "ignore": ["SCREEN_NAME", "USER_HANDLE"]
    },
    "technology": {
        "flag": ["PERSON", "ORG", "GPE", "MONEY", "DATE", "IP_ADDRESS", "EMAIL", "CODE_SNIPPET"],
        "ignore": ["SCREEN_NAME", "USER_HANDLE"]
    },
    "retail": {
        "flag": ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL", "EMAIL", "PHONE_NUMBER", "CREDIT_CARD"],
        "ignore": ["USER_HANDLE", "SCREEN_NAME"]
    },
    "telecom": {
        "flag": ["PERSON", "ORG", "GPE", "DATE", "CARDINAL", "PHONE_NUMBER", "IP_ADDRESS", "ACCOUNT_NUMBER"],
        "ignore": ["SCREEN_NAME", "USER_HANDLE"]
    },
    "energy": {
        "flag": ["PERSON", "ORG", "GPE", "DATE", "CARDINAL", "ACCOUNT_NUMBER", "LOCATION", "EQUIPMENT_ID"],
        "ignore": ["SCREEN_NAME", "USER_HANDLE"]
    },
    "manufacturing": {
        "flag": ["ORG", "GPE", "PRODUCT", "MATERIAL", "EQUIPMENT_ID", "DATE", "CARDINAL"],
        "ignore": ["USER_HANDLE", "SCREEN_NAME"]
    },
    "government": {
        "flag": ["PERSON", "ORG", "GPE", "DATE", "CARDINAL", "CLASSIFIED_INFO", "GOVERNMENT_ID", "MILITARY_UNIT"],
        "ignore": ["SCREEN_NAME", "USER_HANDLE"]
    },
    "education": {
        "flag": ["PERSON", "ORG", "GPE", "DATE", "CARDINAL", "STUDENT_ID", "RESEARCH_TOPIC", "PUBLICATION"],
        "ignore": ["USER_HANDLE", "SCREEN_NAME"]
    },
    "entertainment": {
        "flag": ["PERSON", "ORG", "GPE", "DATE", "CARDINAL", "CONTENT_ID", "COPYRIGHTED_MATERIAL", "SOCIAL_MEDIA_HANDLE"],
        "ignore": ["SCREEN_NAME"]
    }
}

DEFAULT_CONFIG = {
    "strictness": "medium",
    
    # New: Industry Selection
    "industry": "finance",  # Default industry

    # These will be dynamically filled based on the selected industry
    "entity_labels": {
        "flag": [],
        "ignore": []
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

    "whitelist": [],
    "blacklist_patterns": []
}


# Load a pre-trained NER model 
nlp = spacy.load("en_core_web_sm") 
  
  
def load_config(config_path=None):
    """Load configuration from a file or fallback to default settings with industry-based flagging."""
    if config_path and os.path.exists(config_path):
        with open(config_path, "r") as file:
            config = json.load(file)
    else:
        config = DEFAULT_CONFIG.copy()  # Use defaults if no config provided

    # Apply industry-based flagging if an industry is specified
    industry = config.get("industry", "finance").lower()
    if industry in INDUSTRY_PROFILES:
        config["entity_labels"]["flag"] = INDUSTRY_PROFILES[industry]["flag"]
        config["entity_labels"]["ignore"] = INDUSTRY_PROFILES[industry]["ignore"]
    else:
        logging.warning(f"Industry '{industry}' not recognized. Using default flags.")

    return config
 
def apply_manual_overrides(config, user_overrides):
    """Allow users to override industry defaults with their own flags."""
    if "entity_labels" in user_overrides:
        if "flag" in user_overrides["entity_labels"]:
            config["entity_labels"]["flag"] = user_overrides["entity_labels"]["flag"]
        if "ignore" in user_overrides["entity_labels"]:
            config["entity_labels"]["ignore"] = user_overrides["entity_labels"]["ignore"]
    return config


def extract_entities(text, config):
    """Uses NLP to detect named entities that could be sensitive."""
    doc = nlp(text)
    detected_entities = {}

    for ent in doc.ents:
        if ent.label_ in config.get("entity_labels", {}).get("flag", []):
            detected_entities.setdefault(ent.label_, []).append(ent.text)

    return detected_entities
 
 
def detect_sensitive_patterns(text, config):
    """Identifies structured sensitive data based on regex patterns."""
    detected_patterns = {}

    for label, pattern in config.get("sensitive_patterns", {}).items():
        if re.search(pattern.get("regex", ""), text):
            detected_patterns.setdefault("Structured Data", []).append(label)

    return detected_patterns


def detect_anomalies(response_text):
    """Flags text if it contains unusual patterns that might indicate sensitive leaks."""
    anomalies = []
    
    words = response_text.split()
    for word in words:
        if len(word) > 10 and any(char.isdigit() for char in word):   
            anomalies.append(word)  # Possible password or account number

    return anomalies if anomalies else None


def analyze_response(response_text, config):
    """Performs multi-layered detection to prevent AI data leaks."""
    
    issues = {}

    try:
        # Step 1: Regex-based structured detection
        regex_issues = detect_sensitive_patterns(response_text, config)
        if regex_issues:
            issues.update(regex_issues)

        # Step 2: NLP entity recognition
        entity_issues = extract_entities(response_text, config)
        if entity_issues:
            issues.setdefault("Sensitive Entities", []).append(entity_issues)

        # Step 3: Anomaly detection
        anomaly_issues = detect_anomalies(response_text)
        if anomaly_issues:
            issues.setdefault("Anomalies", []).extend(anomaly_issues)

    except KeyError as e:
        return {"verdict": "error", "reason": f"Missing config key: {str(e)}"}

    # Step 4: Decide verdict
    if issues:
        return {"verdict": "flag" if "Anomalies" in issues else "block", "reasons": issues}

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
