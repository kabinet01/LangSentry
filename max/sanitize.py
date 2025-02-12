import unicodedata
import re
import html
import shlex

def detect_context(user_input: str) -> str:
    """
    Automatically detects the context of an input based on its contents.
    Returns one of: 'html', 'sql', 'shell', or 'non-malicious'.
    """

    # Detect HTML/XSS attack patterns
    if re.search(r'(?i)<script|onerror=|<iframe|javascript:', user_input):
        return "html/javascript"

    # Detect SQL Injection patterns
    if re.search(r"(?i)\b(SELECT|INSERT|DELETE|UPDATE|DROP|--|;|\bUNION\b|\bOR\b|\bAND\b)", user_input):
        return "sql"

    # Detect Shell Injection patterns
    if re.search(r'[\$`;&|><]', user_input) or re.search(r'(?i)\b(rm|chmod|chown|wget|curl|eval|exec|system)\b', user_input):
        return "shell"

    # If no specific attack pattern is found, classify as 'non-malicious'
    return "non-malicious"

def sanitize_input(user_input: str, max_length: int = 256) -> dict:
    """
    Detects input context, applies the appropriate sanitization, and returns a dictionary with:
    - category: The detected category (html, sql, shell, non-malicious)
    - sanitized_output: The sanitized (or original) input string.
    """

    # Detect context automatically
    context = detect_context(user_input)

    # Enforce a strict length limit early
    user_input = user_input[:max_length]

    # Normalize Unicode to prevent homoglyph attacks
    sanitized = unicodedata.normalize('NFKC', user_input)

    # Standardize whitespace (replace multiple spaces/newlines with a single space)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()

    if context == "html/javascript":
        sanitized = html.escape(sanitized)  # Escape HTML special characters

    elif context == "sql":
        if not re.match(r"^[a-zA-Z0-9_@.\- ]*$", sanitized):
            sanitized = re.sub(r'[^a-zA-Z0-9_@.\- ]', '', sanitized)  # Strip unsafe characters

    elif context == "shell":
        sanitized = shlex.quote(sanitized)  # Escape shell input

    # If input is non-malicious, return it as is
    if context == "non-malicious":
        sanitized = user_input

    return {
        "category": context,
        "sanitized_output": sanitized
    }

# Example Usage
if __name__ == "__main__":
    test_inputs = [
        "Hello <script>alert('XSS');</script>",  # HTML/XSS
        "SELECT * FROM users WHERE name='admin' --",  # SQL Injection
        "rm -rf /",  # Shell Command Injection
        "Normal text with no attacks.",  # Non-malicious
        "chmod 777 /etc/passwd",  # Shell Injection
        "Safe input without special characters."  # Non-malicious
    ]

    for test in test_inputs:
        result = sanitize_input(test)
        print(f"Input: {repr(test)}")
        print(f"Category: {result['category']}")
        print(f"Sanitized Output: {repr(result['sanitized_output'])}")
        print("-" * 80)
