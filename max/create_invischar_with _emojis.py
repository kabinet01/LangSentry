import pyperclip

def convert_to_tag_chars(input_string):
    """Converts a string into Unicode tag characters."""
    return ''.join(chr(0xE0000 + ord(ch)) for ch in input_string)

user_input = input("Enter a string to convert to tag characters: ")
tagged_output = convert_to_tag_chars(user_input)

# Append a smiley emoji 😀 at the beginning of the output
emoji_tagged_output = "😀" + tagged_output  

print("Tagged output with emoji:", emoji_tagged_output)

# Copy to clipboard
pyperclip.copy(emoji_tagged_output)
