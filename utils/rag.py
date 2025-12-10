def search(query, model, index, chunks, top_k=3):
    query_vec = model.encode([query]).astype("float32")
    distances, indices = index.search(query_vec, top_k)

    results = []
    for idx, dist in zip(indices[0], distances[0]):
        results.append({"chunk": chunks[idx], "score": float(1 / (1 + dist))})

    return results
