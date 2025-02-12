import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
import time

# for importing from huggingface
# from datasets import load_dataset
# splits = {'train': 'data/train-00000-of-00001-2279f74035821199.parquet', 'validation': 'data/validation-00000-of-00001-a3f9d7ca008d6126.parquet', 'test': 'data/test-00000-of-00001-fec3804704adbfa8.parquet'}
# df = pd.read_parquet("hf://datasets/codesagar/malicious-llm-prompts/" + splits["train"])


def create_embeddings():
    start = time.time()
    model = SentenceTransformer('all-MiniLM-L6-v2')
    df = pd.read_csv('malicious.csv')
    sentences = [sentence.lower().replace('br', '').replace('<', "").replace(">", "").replace('\\', "").replace('/', "")
                 for sentence in df.prompt]  # Cleaning
    embeddings = model.encode(sentences)
    np.save("embeddings.npy", embeddings)
    end = time.time()
    print("Embedding done. Time elapsed:", end - start)
    return embeddings


def main():
    create_embeddings()


if __name__ == "__main__":
    main()
