# my_package/__init__.py
from .analyze import some_function
from .canary import generate_canary_token, add_canary_token, check_for_canary_leak
from .misinformation import check_misinformation
__version__ = "0.1.0"