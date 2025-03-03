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



import re

def extract_entities(text):
    """Uses NLP to detect named entities that could be sensitive."""
    doc = nlp(text)
    detected_entities = {}

    for ent in doc.ents:
        if ent.label_ in ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL"]:
            detected_entities.setdefault(ent.label_, []).append(ent.text)

    return detected_entities


def detect_sensitive_patterns(text):
    """Identifies structured sensitive data based on regex patterns."""
    detected_patterns = {}

    for label, pattern in SENSITIVE_PATTERNS.items():
        if re.search(pattern, text):
            detected_patterns.setdefault("Structured Data", []).append(label)

    return detected_patterns


def detect_anomalies(text):
    """Dummy function to simulate anomaly detection."""
    anomalies = []
    if "suspicious_string" in text:
        anomalies.append("Suspicious keyword detected")

    return anomalies if anomalies else None


def analyze_response(response_text):
    """Performs multi-layered detection to prevent AI data leaks."""
    
    issues = {}

    # Step 1: Regex-based structured detection
    regex_issues = detect_sensitive_patterns(response_text)
    if regex_issues:
        issues.update(regex_issues)

    # Step 2: NLP entity recognition
    entity_issues = extract_entities(response_text)
    if entity_issues:
        issues.setdefault("Sensitive Entities", []).append(entity_issues)

    # Step 3: Anomaly detection
    anomaly_issues = detect_anomalies(response_text)
    if anomaly_issues:
        issues.setdefault("Anomalies", []).extend(anomaly_issues)

    # Step 4: Decide verdict
    if issues:
        return {"verdict": "flag" if "Anomalies" in issues else "block", "reasons": issues}

    return {"verdict": "allow", "reason": "No sensitive data found"}
