import unicodedata
import re
import html
import shlex

def detect_context(user_input: str) -> str:
    """
    Automatically detects the context of an input based on its contents.
    Returns one of: 'html', 'sql', 'shell', or 'generic'.
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

    # If no specific attack pattern is found, treat as generic text
    return "generic"

def sanitize_input(user_input: str, max_length: int = 256) -> str:
    """
    Detects input context and applies the appropriate sanitization.
    """

    # Detect context automatically
    context = detect_context(user_input)
    print(f"DEBUG: Detected context: {context}")  # Debugging statement

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
            raise ValueError("Invalid SQL input: contains unsafe characters.")

    elif context == "shell":
        sanitized = shlex.quote(sanitized)  # Escape shell input

    else:  # Generic sanitization
        sanitized = re.sub(r'[<>`"\';&]', '', sanitized)

    return sanitized, context

# Example Usage
if __name__ == "__main__":
    test_inputs = [
        "Hello <script>alert('XSS');</script>",  # HTML/XSS
        "SELECT * FROM users WHERE name='admin' --",  # SQL Injection
        "rm -rf /",  # Shell Command Injection
        "   Normal   text  with    spaces!   ",  # Generic Text
        "chmod 777 /etc/passwd"  # Shell Injection
    ]

    for test in test_inputs:
        try:
            sanitized, detected_context = sanitize_input(test)
            print(f"Detected Context: {detected_context}")
            print(f"Raw Input: {repr(test)}")
            print(f"Sanitized: {repr(sanitized)}")
            print("-" * 50)
        except ValueError as e:
            print(f"Sanitization Failed: {e}")
            print("-" * 50)
