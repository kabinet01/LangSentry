# my_package/__init__.py
from .analyze import some_function
from .canary import generate_canary_token, add_canary_token, check_for_canary_leak
from .misinformation import check_misinformation
from .check_output import load_config, extract_entities, detect_anomalies, detect_sensitive_patterns, analyze_response
from .sanitize import sanitize_input, detect_context, detect_and_decode_invisible_unicode

__version__ = "0.1.0"