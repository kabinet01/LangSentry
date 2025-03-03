import argparse
import json
import os
import pandas as pd
from check_output import load_config, extract_entities, detect_sensitive_patterns, detect_anomalies, analyze_response

CONFIG_PATH = "config.json"


def save_default_config(path=CONFIG_PATH):
    """Creates a default configuration file if none exists."""
    DEFAULT_CONFIG = {
        "strictness": "medium",
        "entity_labels": {
            "flag": ["PERSON", "ORG", "GPE", "MONEY", "DATE", "CARDINAL"],
            "ignore": ["USER_HANDLE", "SCREEN_NAME"]
        },
        "sensitive_patterns": {
            "password": {"regex": "(?=.*[A-Za-z])(?=.*\\d)[A-Za-z\\d!@#$%^&*()_+]{12,}"},
            "account_number": {"regex": "\\b\\d{12,}\\b"},
            "email": {"regex": "\\b[A-Za-z0-9._%+-]+@securehospital\\.com\\b"},
            "ssn": {"regex": "\\b\\d{3}-\\d{2}-\\d{4}\\b"}
        },
        "whitelist": [],
        "blacklist_patterns": []
    }
    if not os.path.exists(path):
        with open(path, "w") as f:
            json.dump(DEFAULT_CONFIG, f, indent=4)
        print(f"Default config saved to {path}")


def simulate_industries():
    """Simulates different industry datasets."""
    industries = {
        "Healthcare": pd.DataFrame({
            "Patient ID": ["12345", "67890"],
            "Name": ["John Doe", "Jane Smith"],
            "SSN": ["123-45-6789", "987-65-4321"],
            "Diagnosis": ["Diabetes", "Hypertension"],
            "Email": ["john.doe@securehospital.com", "jane.smith@securehospital.com"],
            "Balance": ["$5000", "$2000"]
        }),
        "Finance": pd.DataFrame({
            "Account ID": ["ACC123", "ACC456"],
            "Holder": ["Alice Brown", "Bob White"],
            "Balance": ["$15000", "$20000"],
            "Card Number": ["4111-1111-1111-1111", "5500-0000-0000-0004"],
            "SSN": ["567-89-0123", "234-56-7890"]
        }),
        "Enterprise Security": pd.DataFrame({
            "User ID": ["U001", "U002"],
            "Username": ["admin_user", "supervisor"],
            "Password": ["P@ssw0rd1234!", "Qwerty$5678"],
            "Last Login": ["2025-02-20", "2025-02-21"]
        })
    }
    return industries


def run_test_cases(config):
    """Executes various test cases with evasion techniques."""
    test_cases = {
        "Healthcare Leak": "Patient John D0e has SSN 123-45-6789 and was diagnosed with H1gh BP. Contact: j0hn.doe@securehospital.com.",
        "Finance Leak": "Bob W. has an acc# 4111-****-****-1111 with a bal of $20k.",
        "Security Credentials": "User `admin_user` logged in with pass: 'P@ss*****1234!'.", 
        "Obfuscated Data": "The account number is four-one-one-one-1111-1111-1111, and user creds are Qwerty$5****."
    }
    
    results = {}
    for case, text in test_cases.items():
        print(f"\n--- {case} ---")
        result = analyze_response(text, config)
        print(json.dumps(result, indent=4))
        results[case] = result
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Test AI Response Analyzer for Multiple Industries")
    parser.add_argument("-c", "--config", type=str, default=CONFIG_PATH, help="Path to config file")
    args = parser.parse_args()
    
    save_default_config(args.config)
    config = load_config(args.config)
    
    print("\n--- Simulated Industry Datasets ---")
    industries = simulate_industries()
    for industry, df in industries.items():
        print(f"\n{industry} Data:")
        print(df.to_string(index=False))
    
    print("\n--- Running Advanced Test Cases ---")
    test_results = run_test_cases(config)
    
    print("\n--- Summary of All Test Results ---")
    print(json.dumps(test_results, indent=4))


if __name__ == "__main__":
    main()
