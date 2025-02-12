import secrets


def generate_canary_token() -> str:
    """
    Generate an 8-character random hex canary token.
    """
    return secrets.token_hex(4)


def add_canary_token(prompt: str, canary_token: str = None) -> tuple[str, str]:
    """
    Embed a canary token at the start and end of the prompt.

    Args:
        prompt (str): Text to embed the token in.
        canary_token (str, optional): A custom token; generates one if None.

    Returns:
        tuple[str, str]: The modified prompt and the canary token.
    """
    if canary_token is None:
        canary_token = generate_canary_token()
    
    return (f"{canary_token} {prompt} {canary_token}", canary_token)


def check_for_canary_leak(output: str, canary_token: str) -> bool:
    """
    Check if a canary token appears in the output.

    Args:
        output (str): Text to scan.
        canary_token (str): Token to look for.

    Returns:
        bool: True if found, False otherwise.
    """
    return canary_token in output
