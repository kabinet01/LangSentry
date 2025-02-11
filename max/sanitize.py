import unicodedata
import re
import html
import shlex

def sanitize_input(user_input: str, context: str = "generic", max_length: int = 256) -> str:
    """
    Sanitizes user input based on the specified context:
    - 'generic': Applies general Unicode normalization, whitespace standardization, and special character filtering.
    - 'html': Escapes dangerous HTML characters to prevent XSS attacks.
    - 'sql': Only validates safe alphanumeric input and enforces length limits.
    - 'shell': Uses shell escaping to prevent command injection.

    :param user_input: The raw input string.
    :param context: The sanitization context ('generic', 'html', 'sql', 'shell').
    :param max_length: Maximum allowed length.
    :return: A sanitized version of the input.
    """

    # Enforce a strict length limit early
    user_input = user_input[:max_length]

    # Normalize Unicode to prevent homoglyph attacks
    sanitized = unicodedata.normalize('NFKC', user_input)

    # Standardize whitespace (replace multiple spaces/newlines with a single space)
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()

    if context == "html":
        # Escape HTML to prevent XSS (useful for web applications)
        sanitized = html.escape(sanitized)

    elif context == "sql":
        # Allow only alphanumeric characters + safe special characters for SQL input
        if not re.match(r"^[a-zA-Z0-9_@.\- ]*$", sanitized):
            raise ValueError("Invalid SQL input: contains unsafe characters.")

    elif context == "shell":
        # Escape shell input to prevent command injection
        sanitized = shlex.quote(sanitized)

    else:
        # Generic sanitization: Strip special characters commonly used in attacks
        sanitized = re.sub(r'[<>`"\';&]', '', sanitized)

    return sanitized

# Example Usage
if __name__ == "__main__":
    test_inputs = [
        {"input": "Hello <script>alert('XSS');</script>", "context": "html"},
        {"input": "SELECT * FROM users WHERE name='admin' --", "context": "sql"},
        {"input": "rm -rf /", "context": "shell"},
        {"input": "   Normal   text  with    spaces!   ", "context": "generic"},
    ]

    for test in test_inputs:
        print(f"Context: {test['context']}")
        print(f"Raw Input: {repr(test['input'])}")
        try:
            print(f"Sanitized: {repr(sanitize_input(test['input'], test['context']))}")
        except ValueError as e:
            print(f"Sanitization Failed: {e}")
        print("-" * 50)
