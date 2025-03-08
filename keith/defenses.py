import random
import uuid
import re
import spacy
from datetime import datetime
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from langsentry.check_output import DEFAULT_CONFIG, INDUSTRY_PROFILES, load_config, analyze_response
# from test import DummyLLM, test_inputs

# Initialize spaCy and transformers pipelines
nlp = spacy.load("en_core_web_sm")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")
summarizer_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
classifier = pipeline("text-classification", model="C:/ICT2214-Web-Security - New/LangSentry/keith/fine_tuned_roberta_mnli", tokenizer="C:/ICT2214-Web-Security - New/LangSentry/keith/fine_tuned_roberta_mnli")

# Set up text-generation pipelines (using GPT-2 as an example)
name_generator = pipeline("text-generation", model="gpt2")
address_generator = pipeline("text-generation", model="gpt2")
domain_generator = pipeline("text-generation", model="gpt2")

def generate_valid_output(generator, prompt, pattern, max_new_tokens, default, max_attempts=3, temperature=0.7):
    """
    Calls a text generator with a given prompt until the output matches the provided regex pattern.
    Falls back to a default value if no valid output is generated.
    """
    for _ in range(max_attempts):
        result = generator(
            prompt,
            max_new_tokens=max_new_tokens,
            truncation=True,
            pad_token_id=50256,
            num_return_sequences=1,
            do_sample=True,
            temperature=temperature
        )[0]['generated_text']
        text = result[len(prompt):].strip().split("\n")[0]
        if re.match(pattern, text):
            return text
    return default

def generate_fake_name():
    prompt = ("Output only a realistic full name from any culture, written in English. "
              "Do not include any extra text, numbers, or URLs. "
              "For example: Mary Smith, Rajesh Kumar, Mei Ling, Hiro Tanaka, Hans Mueller, Kim Min.\n")
    pattern = r'^[A-Z][a-zA-Z]+(?: [A-Z][a-zA-Z]+)+$'
    result = name_generator(
        prompt,
        max_new_tokens=15,
        truncation=True,
        pad_token_id=50256,
        num_return_sequences=1,
        do_sample=True,
        temperature=0.7
    )[0]['generated_text']
    
    # Debug print for diagnosis
    print("DEBUG raw output:", result)
    
    text = result[len(prompt):].strip().split("\n")[0]
    text = re.sub(r'http\S+', '', text).strip()
    
    match = re.match(pattern, text)
    if match:
        extracted_name = match.group(0).strip()
        print("DEBUG: extracted name:", extracted_name)
        return extracted_name
    else:
        words = text.split()
        valid_words = [w for w in words if w[0].isupper() and len(w) > 1 and not re.search(r'\d', w)]
        if len(valid_words) >= 2:
            fallback_name = " ".join(valid_words[:2])
            print("DEBUG: fallback name from words:", fallback_name)
            return fallback_name
        print("DEBUG: using default name: John Doe")
        return "John Doe"

def generate_fake_org():
    prompt = "Output a realistic company name: "
    pattern = r'^[A-Z][A-Za-z0-9]+( [A-Z][A-Za-z0-9]+)?$'
    return generate_valid_output(name_generator, prompt, pattern, max_new_tokens=5, default="ExampleCorp")

def generate_fake_location():
    prompt = "Output a realistic city name: "
    pattern = r'^[A-Z][a-z]+$'
    return generate_valid_output(name_generator, prompt, pattern, max_new_tokens=5, default="Springfield")

def generate_fake_address():
    prompt = "Output a realistic street address: "
    pattern = r'^\d+ [A-Z][a-zA-Z ]+$'
    return generate_valid_output(address_generator, prompt, pattern, max_new_tokens=10, default="123 Main Street")

def generate_fake_email():
    fake_name = generate_fake_name().lower().replace(" ", ".")
    prompt = "Output a realistic email domain: "
    pattern = r'^[a-z]+\.(com|net|org)$'
    domain = generate_valid_output(domain_generator, prompt, pattern, max_new_tokens=5, default="gmail.com")
    return f"{fake_name}@{domain}"

def generate_fake_credit_card():
    card_type = random.choice(["Visa", "MasterCard", "American Express"])
    if card_type == "Visa":
        second_digit = str(random.randint(2,6))
        prefix = "4" + second_digit + "".join(str(random.randint(0,9)) for _ in range(4))
        remaining_length = 16 - len(prefix)
        number = prefix + "".join(str(random.randint(0,9)) for _ in range(remaining_length))
        formatted = "-".join(number[i:i+4] for i in range(0, 16, 4))
        return formatted
    elif card_type == "MasterCard":
        start = str(random.randint(51, 55))
        prefix = start + "".join(str(random.randint(0,9)) for _ in range(4))
        remaining_length = 16 - len(prefix)
        number = prefix + "".join(str(random.randint(0,9)) for _ in range(remaining_length))
        formatted = "-".join(number[i:i+4] for i in range(0, 16, 4))
        return formatted
    else:  # American Express
        start = random.choice(["34", "37"])
        prefix = start + "".join(str(random.randint(0,9)) for _ in range(4))
        remaining_length = 15 - len(prefix)
        number = prefix + "".join(str(random.randint(0,9)) for _ in range(remaining_length))
        formatted = number[:4] + " " + number[4:10] + " " + number[10:]
        return formatted

def generate_fake_phone():
    country_codes = ["+1", "+44", "+61", "+49"]
    country_code = random.choice(country_codes)
    area = random.randint(200, 999)
    first_part = random.randint(100, 999)
    second_part = random.randint(1000, 9999)
    return f"{country_code} {area}-{first_part}-{second_part}"

def generate_fake_birthdate():
    current_year = datetime.now().year
    min_year = current_year - 90
    max_year = current_year - 18
    year = random.randint(min_year, max_year)
    month = random.randint(1, 12)
    if month in {1, 3, 5, 7, 8, 10, 12}:
        day = random.randint(1, 31)
    elif month in {4, 6, 9, 11}:
        day = random.randint(1, 30)
    else:
        day = random.randint(1, 28)
    return f"{day:02d}/{month:02d}/{year}"

def corrupt_string(s, digit_rate=0.65, letter_rate=0.4, special_sub_rate=0.55):
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

def is_dangerous(output):
    result = classifier(output, truncation=True)
    return result[0]['label'] == "DANGEROUS"

def self_heal_output(output):
    if is_dangerous(output):
        inputs = summarizer_tokenizer(output, return_tensors="pt", truncation=True, max_length=512)
        summary_ids = summary_model.generate(inputs["input_ids"], max_new_tokens=50, early_stopping=True)
        return summarizer_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
    return output

def honeypot_data(input_text, config):
    for pattern in config.get("blacklist_patterns", []):
        if re.search(pattern, input_text):
            return f"Fake API Key: {uuid.uuid4()}"
    return None

def segregate_sensitive_info(text, config):
    # Replace emails.
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    text = re.sub(email_pattern, lambda m: generate_fake_email(), text)
    # Replace dates.
    date_pattern = r'\b(\d{1,2}/\d{1,2}/\d{4})\b'
    text = re.sub(date_pattern, lambda m: generate_fake_birthdate(), text)
    # Replace addresses.
    address_pattern = r'\b\d+\s+[A-Z][a-zA-Z ]+\b'
    text = re.sub(address_pattern, lambda m: generate_fake_address(), text)
    # Replace phone numbers.
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    text = re.sub(phone_pattern, lambda m: generate_fake_phone(), text)
    # Replace credit card numbers.
    cc_pattern = r'\b(?:\d{4}-){3}\d{4}\b|\b\d{4} \d{6} \d{5}\b'
    text = re.sub(cc_pattern, lambda m: generate_fake_credit_card(), text)
    # Replace entities using spaCy NER.
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ == "PERSON":
            text = text.replace(ent.text, generate_fake_name())
        elif ent.label_ == "ORG":
            text = text.replace(ent.text, generate_fake_org())
        elif ent.label_ == "GPE":
            text = text.replace(ent.text, generate_fake_location())
    # Replace passwords using the regex from the config.
    password_conf = config.get("sensitive_patterns", {}).get("password", {})
    password_regex = password_conf.get("regex")
    if password_regex:
        text = re.sub(password_regex, lambda m: corrupt_string(m.group()), text)
    return text

class LangSentry:
    def __init__(self, llm, config=None):
        self.llm = llm
        # Load configuration; if none is provided, load defaults.
        if config is None:
            self.config = load_config()
        else:
            self.config = config

    def process_input(self, input_text):
        # Whitelist the system prompt so it isn't manipulated.
        import re
        system_prompt_identifier = re.compile(r"You are HealthBot, a helpful and friendly healthcare assistant for MediCare Health Services.", re.IGNORECASE)
        if system_prompt_identifier.search(input_text):
            return self.llm.generate(input_text)

        honeypot = honeypot_data(input_text, self.config)
        if honeypot:
            return honeypot

        output = self.llm.generate(input_text)
        output = self_heal_output(output)
        # Analyze the output using the configuration.
        analysis = analyze_response(output, self.config)
        verdict = analysis.get("verdict")
        reason = analysis.get("reason", "No specific reason provided")
        
        if verdict in ["block", "flag"]:
            print(f"Malicious content detected ({reason}). Triggering output transformation.")
            output = segregate_sensitive_info(output, self.config)
        else:
            print("All checks passed. Returning original output.")
        return output

# Initialize the dummy LLM and LangSentry.
# llm = DummyLLM()
# sentry = LangSentry(llm)

# Uncomment the lines below to run your test cases:
# for test in test_inputs:
#     print(f"\nInput: {test}")
#     print(f"Output (raw): {sentry.llm.generate(test)}")
#     print(f"Output (defended): {sentry.process_input(test)}")
#     print("-" * 50)
