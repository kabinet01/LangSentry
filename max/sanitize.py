import unicodedata
import re
import html
import shlex

# Unicode zero-width and tag characters
ZERO_WIDTH_CHARS = {
    '\u200B': '0',  # Zero-width space
    '\u200C': '1',  # Zero-width non-joiner
    '\u200D': '1',  # Zero-width joiner
    '\uFEFF': '',   # Zero-width no-break space (BOM)
}

TAG_CHARACTER_OFFSET = 0xE0000  # Unicode tag characters start at U+E0000

def detect_context(user_input: str) -> str:
    """
    Automatically detects the context of an input based on its contents.
    Returns one of: 'html/javascript', 'sql', 'shell', 'non-malicious', or 'invisible_unicode'.
    """

    # Detect Invisible Unicode Encoding (Zero-width or Tag Characters)
    if any(char in ZERO_WIDTH_CHARS or 0xE0000 <= ord(char) <= 0xE007F for char in user_input):
        return "invisible_unicode"

    # Detect HTML/XSS attack patterns
    if re.search(r'(?i)<script|onerror=|<iframe|javascript:', user_input):
        return "html/javascript"

    # Detect SQL Injection patterns
    if re.search(r"(?i)\b(SELECT|INSERT|DELETE|UPDATE|DROP|--|;|\bUNION\b|\bOR\b|\bAND\b)", user_input):
        return "sql"

    # Detect Shell Injection patterns
    if re.search(r'[\$`;&|><]', user_input) or re.search(r'(?i)\b(rm|chmod|chown|wget|curl|eval|exec|system)\b', user_input):
        return "shell"

    return "non-malicious"


def detect_and_decode_invisible_unicode(user_input: str) -> str:
    """
    Detects and decodes hidden Unicode characters encoded using Zero-width or Tag Unicode encoding.
    Returns the decoded hidden message if found, otherwise an empty string.
    """

    # Detect and decode zero-width Unicode encoding
    if any(char in ZERO_WIDTH_CHARS for char in user_input):
        binary_string = ''.join(ZERO_WIDTH_CHARS.get(char, '') for char in user_input)
        decoded_chars = [chr(int(binary_string[i:i+8], 2)) for i in range(0, len(binary_string), 8)]
        return ''.join(decoded_chars)

    # Detect and decode Unicode tag characters
    elif any(0xE0000 <= ord(char) <= 0xE007F for char in user_input):
        decoded_text = ''.join(chr(ord(char) - TAG_CHARACTER_OFFSET) for char in user_input if 0xE0000 <= ord(char) <= 0xE007F)
        return decoded_text

    return ""  # No hidden message found


def sanitize_input(user_input: str, max_length: int = 256) -> dict:
    """
    Detects input context, applies the appropriate sanitization, and returns a dictionary with:
    - category: The detected category (html, sql, shell, non-malicious, invisible_unicode)
    - sanitized_output: The sanitized (or original) input string.
    - decoded_hidden_message: If applicable, the decoded text.
    - decoded_category: Category of the decoded hidden text (if any).
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

    # Decode invisible Unicode if detected
    decoded_hidden_message = ""
    decoded_category = None
    if context == "invisible_unicode":
        decoded_hidden_message = detect_and_decode_invisible_unicode(user_input)
        if decoded_hidden_message:
            # Run the decoded message through the detection system again
            decoded_category = detect_context(decoded_hidden_message)

    return {
        "category": context,
        "sanitized_output": sanitized,
        "decoded_hidden_message": decoded_hidden_message,
        "decoded_category": decoded_category
    }


# Example Usage
if __name__ == "__main__":
    test_inputs = [
        "Hello <script>alert('XSS');</script>",  # HTML/XSS
        "SELECT * FROM users WHERE name='admin' --",  # SQL Injection
        "rm -rf /",  # Shell Command Injection
        "Normal text with no attacks.",  # Non-malicious
        "chmod 777 /etc/passwd",  # Shell Injection
        "Safe input without special characters.",  # Non-malicious
        "😀\u200B\u200C\u200B\u200B\u200C\u200B\u200C",  # Hidden binary message using zero-width encoding
        "😀󠁄󠁒󠁏󠁐󠀠󠁔󠁁󠁂󠁌󠁅󠀠󠁵󠁳󠁥󠁲󠁳"  # Hidden SQL Injection
    ]

    for test in test_inputs:
        result = sanitize_input(test)
        print(f"Input: {repr(test)}")
        print(f"Category: {result['category']}")
        print(f"Sanitized Output: {repr(result['sanitized_output'])}")

        if result["decoded_hidden_message"]:
            print(f"Decoded Hidden Message: {repr(result['decoded_hidden_message'])}")
            print(f"Decoded Hidden Category: {result['decoded_category']}")

        print("-" * 80)
