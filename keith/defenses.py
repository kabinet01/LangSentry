import random
import uuid
import re
import spacy
from langsentry.check_output import SENSITIVE_PATTERNS, BLACKLIST_PATTERNS, detect_sensitive_patterns
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from test import DummyLLM, test_inputs

nlp = spacy.load("en_core_web_sm")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")
summarizer_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
classifier = pipeline("text-classification", model="./fine_tuned_roberta_mnli", tokenizer="./fine_tuned_roberta_mnli")

def corrupt_string(s, digit_rate=0.65, letter_rate=0.4, special_sub_rate=0.55):
    """
    Corrupts the input string by substituting characters.
    """
    result = []
    special_chars = "!@#$%^&*()_+-=[]{}|;':,.<>/?"
    for char in s:
        if char.isdigit():
            if random.random() < digit_rate:
                new_char = str((int(char) + random.randint(1, 9)) % 10)
                result.append(new_char)
            else:
                result.append(char)
        elif char.isalpha():
            if random.random() < letter_rate:
                if random.random() < special_sub_rate:
                    result.append(random.choice(special_chars))
                else:
                    shift = random.randint(1, 2)
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
    """
    for label, pattern in SENSITIVE_PATTERNS.items():
        def replace_match(match):
            original = match.group()
            corrupted = corrupt_string(original)
            return corrupted
        text = re.sub(pattern, replace_match, text, flags=re.IGNORECASE)
    return text

def is_dangerous(output):
    result = classifier(output)
    return result[0]['label'] == "DANGEROUS"

def self_heal_output(output):
    if is_dangerous(output):
        inputs = summarizer_tokenizer(output, return_tensors="pt", truncation=True, max_length=512)
        summary_ids = summary_model.generate(inputs["input_ids"], max_length=50, early_stopping=True)
        return summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return output

def honeypot_data(input_text):
    if any(re.search(pattern, input_text) for pattern in BLACKLIST_PATTERNS):
        return f"Fake API Key: {uuid.uuid4()}"
    return None

def classify_output(output):
    prompt = (
        "You are a security administrator tasked with detecting any exposure of internal or confidential data. "
        "If the text reveals sensitive information (e.g., passwords, API keys, SSNs, account numbers, secrets, or suspicious patterns), "
        "respond 'MALICIOUS'. Otherwise, respond 'BENIGN'.\n\n"
        "Output: " + output
    )
    result = classifier(prompt)
    # print("Classifier result:", result)
    return result[0]['label'].upper() == "LABEL_1"

class LangSentry:
    def __init__(self, llm):
        self.llm = llm

    def process_input(self, input_text):
        honeypot = honeypot_data(input_text)
        if honeypot:
            return honeypot
        
        output = self.llm.generate(input_text)
        output = self_heal_output(output)

        regex_flag, _ = detect_sensitive_patterns(output)
        classifier_flag = classify_output(output)
        if regex_flag:
            print("Check 1 failed")
            if classifier_flag:
                print("Check 2 failed")
                print("Malicious content detected. Triggering output poisoning")
                output = corrupt_string(output)
        else:
            print("Check 1 passed")
            if classifier_flag:
                print("Check 2 failed")
                print("Malicious content detected. Triggering output poisoning")
                output = corrupt_string(output)
            else:
                print("Both checks passed. Returning original output")
        return output

llm = DummyLLM()
sentry = LangSentry(llm)

# for test in test_inputs:
    # print(f"\nInput: {test}")
    # print(f"Output: {sentry.process_input(test)}")
    # print("-" * 50)
