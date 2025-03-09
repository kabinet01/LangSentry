# Done by Keith 
import random
import uuid
import re
import spacy
from datetime import datetime
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from langsentry.check_output import DEFAULT_CONFIG, INDUSTRY_PROFILES, load_config, analyze_response

# Initialize spaCy and transformers pipelines
nlp = spacy.load("en_core_web_sm")
ner_pipeline = pipeline("ner", model="dslim/bert-base-NER")
summarizer_tokenizer = AutoTokenizer.from_pretrained("facebook/bart-large-cnn")
summary_model = AutoModelForSeq2SeqLM.from_pretrained("facebook/bart-large-cnn")
classifier = pipeline(
    "text-classification",
    model="roberta-large-mnli",
    tokenizer="roberta-large-mnli"
)

# Set up text-generation pipelines (using GPT-2 as an example)
address_generator = pipeline("text-generation", model="GPT2")
domain_generator = pipeline("text-generation", model="GPT2")

WHITELIST = [
    "HealthBot",
    "MediCare Health Services"
]

CULTURES = {
    "Indian": {
        "male_first": [
            "Amit", "Ravi", "Vikram", "Rajesh", "Manish", 
            "Deepak", "Suresh", "Arun", "Naveen", "Rahul",
            "Kunal", "Sanjay", "Anil", "Gopal", "Pranav",
            "Rohan", "Siddharth", "Akash", "Varun", "Karthik"
        ],
        "female_first": [
            "Priya", "Sneha", "Ananya", "Pooja", "Neha",
            "Asha", "Meera", "Kavita", "Swati", "Divya",
            "Rashmi", "Lata", "Geeta", "Sakshi", "Anjali",
            "Bhavana", "Nidhi", "Monika", "Shweta", "Komal"
        ],
        "last": [
            "Patel", "Sharma", "Reddy", "Singh", "Chopra",
            "Varma", "Kapoor", "Bose", "Iyer", "Nair",
            "Gupta", "Malhotra", "Saxena", "Dubey", "Yadav",
            "Bhatia", "Bhattacharya", "Chaudhary", "Desai", "Gandhi"
        ]
    },
    "Korean": {
        "male_first": [
            "Minjun", "Jihoo", "Hyunwoo", "Sungmin", "Joon",
            "Daeho", "Taehyung", "Jinwoo", "Youngsoo", "Donghyun",
            "Seungwon", "Minsik", "Junho", "Chanwoo", "Sanghyuk",
            "Hoseok", "Kyungsoo", "Seongjin", "Gwangsoo", "Yongmin"
        ],
        "female_first": [
            "Jiwoo", "Hyejin", "Soojin", "Jihye", "Minji",
            "Eunji", "Yuna", "Haerin", "Ara", "Bora",
            "Hyeri", "Seoyeon", "Nayoung", "Jiyeon", "Somin",
            "Chaeyoung", "Eunjin", "Mina", "Hana", "Yeji"
        ],
        "last": [
            "Kim", "Lee", "Park", "Choi", "Jung",
            "Kang", "Yoon", "Lim", "Han", "Oh",
            "Seo", "Shin", "Kwon", "Hwang", "Song",
            "Hong", "Jeon", "Bae", "Baek", "Yu"
        ]
    },
    "Japanese": {
        "male_first": [
            "Hiroshi", "Kenji", "Takashi", "Naoki", "Kazuo",
            "Shinji", "Yuji", "Ryota", "Daichi", "Kenta",
            "Haruto", "Ren", "Yuto", "Sota", "Tatsuya",
            "Jun", "Toru", "Makoto", "Shigeru", "Masashi"
        ],
        "female_first": [
            "Yuki", "Sakura", "Aiko", "Ayumi", "Miyuki",
            "Haruka", "Akiko", "Emi", "Yuna", "Rina",
            "Asuka", "Nana", "Miku", "Mei", "Hinata",
            "Rei", "Nao", "Chihiro", "Eri", "Kaori"
        ],
        "last": [
            "Sato", "Suzuki", "Tanaka", "Watanabe", "Ito",
            "Nakamura", "Kobayashi", "Yamamoto", "Matsumoto", "Inoue",
            "Sasaki", "Kato", "Yoshida", "Yamada", "Abe",
            "Ogawa", "Ishikawa", "Maeda", "Fujita", "Fukuda"
        ]
    },
    "English": {
        "male_first": [
            "Oliver", "George", "Jack", "Harry", "Charlie",
            "Thomas", "James", "William", "Henry", "Daniel",
            "Samuel", "Joseph", "Oscar", "Archie", "Leo",
            "Edward", "Freddie", "Arthur", "Benjamin", "Max"
        ],
        "female_first": [
            "Amelia", "Emily", "Sophie", "Jessica", "Grace",
            "Lucy", "Chloe", "Charlotte", "Hannah", "Olivia",
            "Ellie", "Isabella", "Mia", "Daisy", "Freya",
            "Evie", "Ruby", "Scarlett", "Millie", "Alice"
        ],
        "last": [
            "Smith", "Johnson", "Brown", "Taylor", "Anderson",
            "Thomas", "Jackson", "White", "Harris", "Martin",
            "Thompson", "Garcia", "Clark", "Lewis", "Robinson",
            "Walker", "Young", "Allen", "King", "Scott"
        ]
    },
    "Spanish": {
        "male_first": [
            "Carlos", "Miguel", "Rafael", "Juan", "Pedro",
            "Alejandro", "Diego", "Luis", "Manuel", "Sergio",
            "Jose", "Antonio", "Javier", "Fernando", "Francisco",
            "Ricardo", "Pablo", "Hugo", "Adrian", "Mario"
        ],
        "female_first": [
            "Lucia", "Sofia", "Maria", "Paula", "Sara",
            "Valeria", "Alba", "Noelia", "Carmen", "Laura",
            "Ana", "Elena", "Patricia", "Nuria", "Carla",
            "Eva", "Raquel", "Ines", "Rocio", "Angela"
        ],
        "last": [
            "Garcia", "Martinez", "Rodriguez", "Lopez", "Hernandez",
            "Gonzalez", "Perez", "Sanchez", "Ramirez", "Torres",
            "Flores", "Morales", "Ortega", "Vargas", "Castro",
            "Ramos", "Gutierrez", "Navarro", "Reyes", "Cruz"
        ]
    },
    "Chinese": {
        "male_first": [
            "Wei", "Lei", "Jun", "Hao", "Peng",
            "Jie", "Qiang", "Bo", "Chao", "Chen",
            "Long", "Feng", "Yu", "Bin", "Tao",
            "Rui", "Zhi", "Shu", "Guang", "Xiang"
        ],
        "female_first": [
            "Xia", "Mei", "Ling", "Hua", "Li",
            "Fen", "Lan", "Juan", "Qiu", "Ying",
            "Dan", "Yun", "Yue", "Na", "Yan",
            "Ting", "Ning", "Rou", "Cai", "Shan"
        ],
        "last": [
            "Wang", "Li", "Zhang", "Liu", "Chen",
            "Yang", "Huang", "Zhao", "Wu", "Zhou",
            "Xu", "Sun", "Ma", "Hu", "Zhu",
            "Guo", "He", "Lin", "Gao", "Lu"
        ]
    },
    "Malay": {
        "male_first": [
            "Ahmad", "Azman", "Rizal", "Zulkifli", "Faiz",
            "Hafiz", "Rahim", "Shahrul", "Amir", "Hakim",
            "Imran", "Syed", "Hadi", "Farid", "Kamal",
            "Zain", "Arif", "Taufik", "Nasir", "Rashid"
        ],
        "female_first": [
            "Siti", "Nur", "Faridah", "Aisyah", "Laila",
            "Zarina", "Rohana", "Haslina", "Ain", "Suhana",
            "Nadia", "Fatin", "Syikin", "Hani", "Rina",
            "Izzah", "Amani", "Mariam", "Salmiah", "Norliza"
        ],
        "last": [
            "Abdullah", "Ismail", "Rahman", "Omar", "Yusof",
            "Mahmud", "Hassan", "Salleh", "Zakaria", "Saad",
            "Tahir", "Rashid", "Razak", "Aziz", "Kassim",
            "Ahmad", "Basri", "Yunus", "Ramli", "Zainudin"
        ]
    }
}

PERSON_REPLACEMENTS = {}
EMAIL_REPLACEMENTS = {}

def build_patient_mapping(config):
    """
    Builds a mapping from normalized patient name and normalized email local part
    to a tuple (fake_name, fake_email) using the healthcare database from the config.
    """
    mapping = {}
    db = config.get("healthcare_database")
    if not db or "patients" not in db:
        return mapping

    for patient in db["patients"]:
        original_name = patient.get("name", "")
        original_email = patient.get("email", "")
        norm_name = normalize_name(original_name)
        # Normalize the email's local part as well
        email_local = original_email.partition("@")[0]
        norm_email = normalize_name(email_local)
        fake_name = generate_fake_name()         # Generate one fake name per patient
        fake_email = generate_fake_email(fake_name)  # Generate a fake email from that fake name
        # Store both keys in the mapping so that a lookup by name OR email works.
        mapping[norm_name] = (fake_name, fake_email)
        mapping[norm_email] = (fake_name, fake_email)
    return mapping

def generate_valid_output(generator, prompt, pattern, max_new_tokens, default, max_attempts=5, temperature=0.5):
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
    gender = random.choice(["male", "female"])
    culture = random.choice(list(CULTURES.keys()))
    if gender == "male":
        first_name = random.choice(CULTURES[culture]["male_first"])
    else:
        first_name = random.choice(CULTURES[culture]["female_first"])
    last_name = random.choice(CULTURES[culture]["last"])
    return f"{first_name} {last_name}"

def normalize_name(name_text):
    # Lowercase, remove punctuation, and collapse spaces
    name_text = name_text.lower()
    name_text = re.sub(r'[^\w\s]', '', name_text)  # remove punctuation
    name_text = re.sub(r'\s+', ' ', name_text).strip()
    return name_text

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

def generate_fake_email(fake_name):
    domains = ["gmail.com", "yahoo.com", "hotmail.com", "outlook.com"]
    domain = random.choice(domains)
    email_username = fake_name.lower().replace(" ", "_")
    return f"{email_username}@{domain}"

def generate_fake_email_from_original(original_email, config):
    if original_email in EMAIL_REPLACEMENTS:
        return EMAIL_REPLACEMENTS[original_email]

    username, _, _ = original_email.partition("@")
    # Normalize the username to form a candidate key (e.g., "john smith")
    candidate_key = normalize_name(username)

    # Try to find an existing fake name (and email) for this candidate key in the patient mapping.
    patient_mapping = config.get("patient_mapping", {})
    for norm_name, (fake_name, fake_email) in patient_mapping.items():
        if candidate_key in norm_name or norm_name in candidate_key:
            EMAIL_REPLACEMENTS[original_email] = fake_email
            return fake_email

    # No match found; generate a new fake name and corresponding fake email.
    new_fake_name = generate_fake_name()
    new_fake_email = generate_fake_email(new_fake_name)
    # Save the mapping for consistency
    patient_mapping[candidate_key] = (new_fake_name, new_fake_email)
    config["patient_mapping"] = patient_mapping
    EMAIL_REPLACEMENTS[original_email] = new_fake_email
    return new_fake_email

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
    if "patient_mapping" not in config:
        config["patient_mapping"] = build_patient_mapping(config)
    patient_mapping = config["patient_mapping"]

    # Replace emails.
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'
    text = re.sub(email_pattern, lambda m: generate_fake_email_from_original(m.group(), config), text)
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
    
    # Process entities with spaCy
    doc = nlp(text)
    for ent in doc.ents:
        print(f"  Detected entity: '{ent.text}' (label: {ent.label_})")
        
        # Check if this entity contains any whitelisted terms
        whitelisted_term = None
        for w in WHITELIST:
            if w.lower() in ent.text.lower():
                whitelisted_term = w
                break
        
        if whitelisted_term:
            print(f"  -> '{ent.text}' contains whitelisted term '{whitelisted_term}'. Skipping replacement.")
            continue

        if ent.label_ == "PERSON":
            norm_ent = normalize_name(ent.text)
            if norm_ent in patient_mapping:
                fake_name, _ = patient_mapping[norm_ent]
            else:
                fake_name = generate_fake_name()
                # Optionally, store it if you want consistency for new names:
                patient_mapping[norm_ent] = (fake_name, generate_fake_email(fake_name))
            PERSON_REPLACEMENTS[norm_ent] = fake_name
            text = text.replace(ent.text, fake_name)
        elif ent.label_ == "ORG":
            text = text.replace(ent.text, generate_fake_org())
        elif ent.label_ == "GPE":
            text = text.replace(ent.text, generate_fake_location())

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
        # analysis = analyze_response(output, self.config)
        # verdict = analysis.get("verdict")
        # reason = analysis.get("reason", "No specific reason provided")
        
        # if verdict in ["block", "flag"]:
            # print(f"Malicious content detected ({reason}). Triggering output transformation.")
            # output = segregate_sensitive_info(output, self.config)
        # else:
            # print("All checks passed. Returning original output.")
        # return output

        print("Running segregate_sensitive_info() on all outputs.")
        output = segregate_sensitive_info(output, self.config)
        return output
