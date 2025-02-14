import pandas as pd
from sentence_transformers import SentenceTransformer, util
import numpy as np


def create_embeddings():
    model = SentenceTransformer('all-MiniLM-L6-v2')
    sentences = clean_sentences()
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


def get_embeddings(sentences):
    print("Checking for updates...")
    try:
        embeddings = np.load("embeddings.npy")
        if len(embeddings) == len(sentences):
            print("No updates found. Proceeding...")
            return embeddings
        else:
            print("Update to database found. Importing...")
            return create_embeddings()
    except FileNotFoundError:
        print("No database found. Importing...")
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
    embeddings = get_embeddings(sentences)
    while True:
        query = input("Enter prompt: ")
        if len(query.split(" ")) > 2:
            my_embedding = model.encode(query)

            final_winners = get_cossim(my_embedding, embeddings, sentences)
            if float(final_winners[0][1]) > 0.6:
                print("Prompt is malicious")
            else:
                print("Prompt is not malicious")
            print(f'\nScore :   {final_winners[0][1]}')
            print(f'\nSentence :   {final_winners[0][0]}')
        else:
            print("Prompt is not malicious")


if __name__ == "__main__":
    main()
