import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
import re


def create_embeddings(sentences, model):
    embeddings = model.encode(sentences)
    np.save("embeddings.npy", embeddings)
    print("Database updated...")
    return embeddings


def clean_sentences():
    df = pd.read_csv('malicious.csv')
    sentences = [sentence.lower().replace('br', '').replace('<', "").replace(">", "").replace('\\', "").replace('/', "")
                 for sentence in df.prompt]
    print(len(sentences))
    return sentences


def get_embeddings(sentences, model):
    print("Checking for updates...")
    try:
        embeddings = np.load("embeddings.npy")
        if len(embeddings) == len(sentences):
            print("No updates found. Proceeding...")
            return embeddings
        else:
            print("Update to database found. Importing...")
            return create_embeddings(sentences, model)
    except FileNotFoundError:
        print("No database found. Importing...")
        return create_embeddings(sentences, model)


def get_cossim(my_embeddings, embeddings, sentences):
    # Compute cosine similarity between my sentence, and each one in the corpus
    winners = []
    for my_embedding in my_embeddings:
        cos_sim = util.cos_sim(my_embedding, embeddings)
        for arr in cos_sim:
            for i, each_val in enumerate(arr):
                winners.append([sentences[i], each_val])

    final_winners = sorted(winners, key=lambda x: x[1], reverse=True)
    print(final_winners[0:3])
    return final_winners


def initialize():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = clean_sentences()
    embeddings = get_embeddings(sentences, model)
    return model, sentences, embeddings


def similarity(query, model, sentences, embeddings):
    if len(query.split(" ")) > 2:
        parts = re.split(r'[.!?;:\-()\[\]{}]', query)
        chunks = [part.strip() for part in parts if part.strip()]
        my_embeddings = model.encode(chunks)

        final_winners = get_cossim(my_embeddings, embeddings, sentences)
        print(f'\nScore :   {final_winners[0][1]}')
        print(f'\nSentence :   {final_winners[0][0]}')
        if float(final_winners[0][1]) > 0.6:
            return True
        else:
            return False
    else:
        return False


def main():
    # load our Sentence Transformers model pre trained!!
    model, sentences, embeddings = initialize()
    while True:
        query = input("Enter prompt: ")
        if similarity(query, model, sentences, embeddings):
            print("Prompt is malicious")
        else:
            print("Prompt is not malicious")


if __name__ == "__main__":
    main()
