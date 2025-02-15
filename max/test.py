import pyperclip


def convert_to_tag_chars(input_string):
    return ''.join(chr(0xE0000 + ord(ch)) for ch in input_string)