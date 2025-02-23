import spacy
import subprocess

def download_spacy_model():
    try:
        spacy.load("en_core_web_sm")
        print("spaCy model 'en_core_web_sm' is already installed.")
    except OSError:
        print("Downloading 'en_core_web_sm' model...")
        subprocess.run(["python", "-m", "spacy", "download", "en_core_web_sm"], check=True)

if __name__ == "__main__":
    download_spacy_model()
