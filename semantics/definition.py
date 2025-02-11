from nltk import pos_tag
from nltk import word_tokenize
import nltk
from nltk.wsd import lesk
#nltk.download('punkt')
#nltk.download('wordnet')
# Example sentence
sentence = "I went to the bank to deposit money."
tokens = word_tokenize(sentence)
# Disambiguate the word 'bank'
sense = lesk(tokens, 'city')
print("\nSense for 'bank':")
print(f"  Synset: {sense.name()}")
print(f"  Definition: {sense.definition()}")

#nltk.download('words')
#nltk.download('maxent_ne_chunker_tab')

text = "Somebody once told me the world was gonna roll me"
tokenized_text = word_tokenize(text)
tokens_tag = pos_tag(tokenized_text)
named_entities = nltk.ne_chunk(tokens_tag)
print("\nNamed Entities:")
print(named_entities)
