import unicodedata
import re

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


def process_input(user_input: str, max_length: int = 256) -> dict:
    """
    Detects input context but does NOT apply any sanitization.
    Returns:
    - category: The detected category (html, sql, shell, non-malicious, invisible_unicode)
    - final_output: The original input (even if it is malicious).
    """

    # Detect context automatically
    context = detect_context(user_input)

    # Enforce a strict length limit early (but do NOT sanitize)
    user_input = user_input[:max_length]

    # Decode invisible Unicode if detected
    decoded_hidden_message = ""
    if context == "invisible_unicode":
        decoded_hidden_message = detect_and_decode_invisible_unicode(user_input)

    # Final output is always the original input
    final_output = user_input

    return {
        "category": context,
        "final_output": final_output,
        "decoded_hidden_message": decoded_hidden_message
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
        "😀"  # Normal Unicode character
    ]

    for test in test_inputs:
        result = process_input(test)
        print(f"Input: {repr(test)}")
        print(f"Category: {result['category']}")

        if result["decoded_hidden_message"]:
            print(f"Decoded Hidden Message: {repr(result['decoded_hidden_message'])}")

        print(f"Final Output: {repr(result['final_output'])}")  # Original input, malicious or not
        print("-" * 80)
