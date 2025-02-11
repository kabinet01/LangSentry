from transformers import AutoTokenizer
from datasets import load_dataset
from collections import defaultdict
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load and validate the dataset
def load_data(dataset_name):
    dataset = load_dataset(dataset_name)
    if 'train' not in dataset:
        raise ValueError("Dataset must have a 'train' split.")
    return dataset

# Initialization
def initialize_tokenizer(model_name):
    return AutoTokenizer.from_pretrained(model_name)

# Split tokens into smaller chunks
def split_tokens(tokens, max_len=512):
    return [tokens[i:i + max_len] for i in range(0, len(tokens), max_len)]

# Calculates token frequencies in the dataset
def token_freq(dataset, tokenizer):
    token_counts = defaultdict(int)
    total_tokens = 0

    for data in dataset['train']:
        if 'context' not in data or not isinstance(data['context'], str):
            logger.debug(f"Skipping row: {data}")
            continue

        text = data['context']
        tokens = tokenizer.tokenize(text)
        chunks = split_tokens(tokens)

        for chunk in chunks:
            for token in chunk:
                token_counts[token] += 1
                total_tokens += 1

    return token_counts, total_tokens

# Normalizing data
def normalize_freq(token_counts, total_tokens):
    return {token: count / total_tokens for token, count in token_counts.items()}

# Printing of no. of samples and frequencies
def print_sample_freq(dataset, tokenizer, num_samples=5, top_k=10):
    logger.info("Tokenized output:")
    for i, data in enumerate(dataset['train'][:num_samples]):
        if 'context' in data and isinstance(data['context'], str):
            text = data['context']
            tokens = tokenizer.tokenize(text)
            chunks = split_tokens(tokens)
            logger.info(f"Prompt {i + 1}: {text}")
            logger.info(f"Chunks: {chunks}")
        else:
            logger.debug(f"Skipping row: {data}")

    logger.info("\nToken frequencies (top %d):", top_k)
    for token, freq in sorted(token_counts.items(), key=lambda x: x[1], reverse=True)[:top_k]:
        logger.info(f"Token: {token}, Frequency: {freq}")

# Main execution
if __name__ == "__main__":
    dataset_name = "OpenRLHF/prompt-collection-v0.1"
    model_name = "gpt2"

    dataset = load_data(dataset_name)
    print("hi1")
    tokenizer = initialize_tokenizer(model_name)
    print("hi2")
    token_counts, total_tokens = token_freq(dataset, tokenizer)
    print("hi3")
    token_probabilities = normalize_freq(token_counts, total_tokens)
    print("hi4")

    print_sample_freq(dataset, tokenizer, num_samples=5, top_k=10)