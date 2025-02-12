import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np
from create_embeddings import create_embeddings


def clean_sentences():
    df = pd.read_csv('malicious.csv')
    sentences = [sentence.lower().replace('br', '').replace('<', "").replace(">", "").replace('\\', "").replace('/', "")
                 for sentence in df.prompt]
    return sentences


def get_embeddings():
    try:
        return np.load("embeddings.npy")
    except FileNotFoundError:
        return create_embeddings()


def get_cossim(my_embedding, embeddings, sentences):
    # Compute cosine similarity between my sentence, and each one in the corpus
    cos_sim = util.cos_sim(my_embedding, embeddings)

    winners = []
    for arr in cos_sim:
        for i, each_val in enumerate(arr):
            winners.append([sentences[i], each_val])

    final_winners = sorted(winners, key=lambda x: x[1], reverse=True)
    return final_winners


def main():
    # load our Sentence Transformers model pre trained!!
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = clean_sentences()
    embeddings = get_embeddings()

    while True:
        query = input("test: ")
        my_embedding = model.encode(query)

        final_winners = get_cossim(my_embedding, embeddings, sentences)
        if float(final_winners[0][1]) > 0.55:
            print("Prompt is malicious")
        else:
            print("Prompt is not malicious")
        print(f'\nScore :   {final_winners[0][1]}')
        print(f'\nSentence :   {final_winners[0][0]}')


if __name__ == "__main__":
    main()
