from transformers import AutoTokenizer, AutoModel
import torch
import pandas as pd
import numpy as np
from torch.nn.functional import cosine_similarity
import gc
import os
from datetime import datetime
import json

def load_and_clean_data(csv_path, sample_size=462):
    """Load and clean the data from CSV"""
    print("Reading CSV file...")
    df = pd.read_csv(csv_path, usecols=['text'])
    
    total_rows = len(df)
    actual_sample_size = min(sample_size, total_rows)
    print(f"Processing {actual_sample_size} samples from {total_rows} total rows...")
    
    # Convert to list of strings instead of numpy array
    clean_sentences = (df['text']
                      .sample(n=actual_sample_size)
                      .str.lower()
                      .str.replace('br|<|>|\\|/', '', regex=True)
                      .tolist())  # Changed from .values to .tolist()
    return clean_sentences

def generate_bert_embedding(text, model, tokenizer):
    """Generate embedding for a single text"""
    encoded = tokenizer(
        text,
        padding=True,
        truncation=True,
        max_length=256,
        return_tensors='pt'
    )
    
    with torch.no_grad():
        outputs = model(**encoded)
        embedding = outputs.last_hidden_state[:, 0, :]
    
    return embedding

def generate_corpus_embeddings(texts, batch_size=8):
    """Generate BERT embeddings for corpus texts"""
    print("Loading model and tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', use_fast=True)
    model = AutoModel.from_pretrained('bert-base-uncased')
    model.eval()
    
    embeddings = []
    print("Generating corpus embeddings...")
    
    for i in range(0, len(texts), batch_size):
        # Convert batch to list of strings
        batch_texts = texts[i:i + batch_size]
        
        encoded = tokenizer(
            batch_texts,
            padding=True,
            truncation=True,
            max_length=256,
            return_tensors='pt'
        )
        
        with torch.no_grad():
            outputs = model(**encoded)
            batch_embeddings = outputs.last_hidden_state[:, 0, :]
            embeddings.append(batch_embeddings)
            
            del outputs
            gc.collect()
    
    final_embeddings = torch.cat(embeddings, dim=0)
    
    return final_embeddings, model, tokenizer

def save_corpus_data(embeddings, sentences, file_path):
    """Save corpus embeddings and sentences to file"""
    data = {
        'embeddings': embeddings.cpu().numpy().tolist(),
        'sentences': sentences,  # Already a list of strings
        'timestamp': datetime.now().isoformat()
    }
    
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
    print(f"Corpus data saved to {file_path}")

def load_corpus_data(file_path):
    """Load corpus embeddings and sentences from file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    embeddings = torch.tensor(data['embeddings'])
    sentences = data['sentences']  # Keep as list of strings
    return embeddings, sentences

def find_similar_sentences(query_embedding, corpus_embeddings, clean_sentences, top_k=2):
    """Find most similar sentences to query"""
    print("Computing similarities...")
    cos_scores = cosine_similarity(query_embedding, corpus_embeddings).squeeze()
    
    top_k = min(top_k, len(corpus_embeddings))
    top_values, top_indices = torch.topk(cos_scores, k=top_k)
    
    return top_values, top_indices

def main():
    # File paths
    csv_path = 'malignant.csv'
    corpus_file = 'corpus_data.json'
    
    # Get query from user (default value for testing)
    query = 'How to use pie charts'
    
    # Load or generate corpus embeddings
    if os.path.exists(corpus_file):
        print("Loading cached corpus data...")
        corpus_embeddings, clean_sentences = load_corpus_data(corpus_file)
        
        # Load model for query
        print("Loading model for query...")
        tokenizer = AutoTokenizer.from_pretrained('bert-base-uncased', use_fast=True)
        model = AutoModel.from_pretrained('bert-base-uncased')
        model.eval()
    else:
        print("Generating new corpus embeddings...")
        # Load and clean data
        clean_sentences = load_and_clean_data(csv_path)
        
        # Generate corpus embeddings and get model/tokenizer
        corpus_embeddings, model, tokenizer = generate_corpus_embeddings(clean_sentences)
        
        # Save corpus data for future use
        save_corpus_data(corpus_embeddings, clean_sentences, corpus_file)
    
    # Generate embedding for query
    print("Generating query embedding...")
    query_embedding = generate_bert_embedding(query, model, tokenizer)
    
    # Find similar sentences
    top_values, top_indices = find_similar_sentences(
        query_embedding, 
        corpus_embeddings, 
        clean_sentences
    )
    
    # Print results
    print("\nMost similar sentences to your query:", query)
    for score, idx in zip(top_values, top_indices):
        print(f'\nScore: {score.item():.4f}')
        print(f'Sentence: {clean_sentences[idx]}')
    
    # Clean up
    del model, tokenizer, corpus_embeddings
    gc.collect()

if __name__ == "__main__":
    main()