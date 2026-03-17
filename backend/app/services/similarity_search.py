import numpy as np


def cosine_similarity(a, b):

    a = np.array(a)
    b = np.array(b)

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


async def retrieve_similar(query_embedding, docs, top_k=5):

    scores = []

    for d in docs:

        score = cosine_similarity(query_embedding, d["embedding"])

        scores.append((score, d))

    scores.sort(reverse=True, key=lambda x: x[0])

    return [s[1] for s in scores[:top_k]]