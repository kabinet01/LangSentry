import random
import uuid
import re
import spacy
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from test import DummyLLM, test_inputs

# Load pre-trained NLP models
nlp = spacy.load("en_core_web_sm")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
classifier = pipeline("text-classification", model="roberta-large-mnli")

# Sensitive data detection patterns.
SENSITIVE_PATTERNS = {
    "password": r"(?i)\b(?:pass(?:word)?|pwd)\b(?:\s+(?:is|:))?\s+(?P<secret>(?=.*[A-Za-z])(?=.*[\W_])\S+)",
    "account_number": r"\b\d{10,}\b",
    "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
    "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
    "api_key": r"(?i)\b(?:api|key|token)\b\s*[:=]?\s*(?P<secret>[\w-]{10,})\b"
}

# Blacklisted phrases (Jailbreak detection)
BLACKLIST_PATTERNS = [
    r"(?i)system_prompt\s*=",
    r"(?i)do anything now",
    r"base64[a-zA-Z0-9+/=]{20,}",
]

def corrupt_string(s, corruption_rate=0.75, insertion_rate=0.5, deletion_rate=0.25):
    """
    Corrupts the input string by altering, inserting, or deleting characters.
    - corruption_rate: probability that a given character will be altered.
    - insertion_rate: probability to insert a random character before a given character.
    - deletion_rate: probability that a given character will be skipped.
    """
    result = []
    allowed_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;':,.<>/?"
    for char in s:
        if random.random() < deletion_rate:
            continue
        if random.random() < insertion_rate:
            result.append(random.choice(allowed_chars))
        if random.random() < corruption_rate:
            if char.isdigit():
                new_char = str((int(char) + random.randint(1, 9)) % 10)
                result.append(new_char)
            elif char.isalpha():
                shift = random.randint(1, 3)
                if char.isupper():
                    new_char = chr((ord(char) - ord('A') + shift) % 26 + ord('A'))
                else:
                    new_char = chr((ord(char) - ord('a') + shift) % 26 + ord('a'))
                result.append(new_char)
            else:
                result.append(char)
        else:
            result.append(char)
    return "".join(result)

def poison_sensitive_info(text):
    """
    Finds all substrings that match our sensitive patterns and corrupts them.
    (This function is used by safe_output if needed.)
    """
    for label, pattern in SENSITIVE_PATTERNS.items():
        def replace_match(match):
            original = match.group()
            corrupted = corrupt_string(original, corruption_rate=0.75, insertion_rate=0.5, deletion_rate=0.25)
            return corrupted
        text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    return text

def extract_entities(text):
    detected_entities = {}
    ner_results = ner_pipeline(text)
    for entity in ner_results:
        if entity["entity"] in ["B-ORG", "I-ORG", "B-PER", "I-PER"]:
            detected_entities[entity["entity"]] = entity["word"]
    return detected_entities

def detect_sensitive_patterns(text):
    for label, pattern in SENSITIVE_PATTERNS.items():
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            print(f"[DEBUG] Matched pattern for {label}: {match.group()}")
            return True, label, match
    return False, None, None

def safe_output(data):
    for label, pattern in SENSITIVE_PATTERNS.items():
        match = re.search(pattern, data, flags=re.IGNORECASE)
        if match:
            print(f"[DEBUG] {label} detected - Poisoning now...")
            if label in ["password", "api_key"]:
                secret = match.group("secret")
                corrupted = corrupt_string(secret, corruption_rate=0.3, insertion_rate=0.1, deletion_rate=0.1)
                return corrupted
            else:
                corrupted = corrupt_string(match.group(), corruption_rate=0.3, insertion_rate=0.1, deletion_rate=0.1)
                return corrupted
    print("[DEBUG] No sensitive data detected. Returning original output.")
    return data

def is_dangerous(output):
    result = classifier(output)
    return result[0]['label'] == "DANGEROUS"

def self_heal_output(output):
    if is_dangerous(output):
        inputs = tokenizer(output, return_tensors="pt", truncation=True, max_length=512)
        summary_ids = summary_model.generate(inputs["input_ids"], max_length=50, early_stopping=True)
        return tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return output

def honeypot_data(input_text):
    if any(re.search(pattern, input_text) for pattern in BLACKLIST_PATTERNS):
        return f"Fake API Key: {uuid.uuid4()}"
    return None

def check_data(data):
    regex_detected, category, _ = detect_sensitive_patterns(data)
    if regex_detected:
        return True, f"Regex pattern match: {category}"
    entities = extract_entities(data)
    if entities:
        return True, f"Sensitive entities detected: {entities}"
    return False, None

class LangSentry:
    def __init__(self, llm):
        self.llm = llm

    def process_input(self, input_text):
        # Step 1: Honeypot detection
        honeypot = honeypot_data(input_text)
        if honeypot:
            return honeypot

        # Step 2: Process input with LLM
        output = self.llm.generate(input_text)

        # Step 3: Self-heal dangerous outputs
        output = self_heal_output(output)

        # Step 4: If sensitive data is present, extract and poison it,
        # returning just the confidential secret.
        output = safe_output(output)
        return output

# Initialize LangSentry
llm = DummyLLM()
sentry = LangSentry(llm)

for test in test_inputs:
    print(f"\nInput: {test}")
    print(f"Output: {sentry.process_input(test)}")
    print("-" * 50)
