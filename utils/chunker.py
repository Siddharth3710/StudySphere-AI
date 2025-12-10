import re


def clean_text(text):
    text = re.sub(r"\n\s*\n", "\n\n", text)
    text = re.sub(r" +", " ", text)
    return text.strip()


def chunk_text(text, chunk_size=500, overlap=50):
    words = text.split()
    chunks = []

    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i : i + chunk_size])
        if len(chunk.strip()) > 30:
            chunks.append(chunk)

    return chunks
