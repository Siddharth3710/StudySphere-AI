<div align="center">

<h1>
  <img src="https://img.shields.io/badge/📚-StudySphere_AI-1a4a2e?style=for-the-badge&labelColor=e8f2ec" alt="StudySphere AI"/>
</h1>

**An intelligent study companion that transforms static PDFs into an interactive learning environment.**

[![MIT License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-3b82f6?style=flat-square&logo=python&logoColor=white)](https://python.org)
[![Architecture](https://img.shields.io/badge/Architecture-RAG-f59e0b?style=flat-square)](https://arxiv.org/abs/2005.11401)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen?style=flat-square)](CONTRIBUTING.md)

</div>

---

## Overview

StudySphere AI combines **Retrieval-Augmented Generation (RAG)** with modern LLMs to help you engage deeply with study material. Instead of passively reading, you can interrogate your documents, surface key concepts, and test yourself — all from a single interface.

Every response is grounded in your actual content, eliminating the hallucinations common to generic AI chatbots.

---

## Features

### Semantic Question Answering
Ask any question about your PDF in plain language. FAISS-powered vector search retrieves the most relevant passages; the LLM synthesises a precise, source-grounded answer.

### Interactive Chat Mode
A conversational interface with a streaming typewriter effect. Follow-up questions maintain context from previously retrieved passages for a coherent, multi-turn study session.

### Exam Generator
Auto-generates multiple-choice and open-ended questions from any section of your document. Highlight a specific passage to create a focused quiz on that exact content.

### Flashcard Deck
AI-authored flashcards with smooth click-to-flip animation — ideal for spaced repetition on key concepts extracted directly from your notes.

### Summariser
Generate bullet-point or detailed chapter summaries at adjustable lengths, distilling hours of reading into a concise, structured overview.

### Persistent Vector Index
The FAISS index and text chunks are saved to disk after initial processing. Re-open any previously indexed document instantly — no re-embedding required.

---

## How It Works
```
PDF Extract  →  Clean & Chunk  →  Embed (SentenceTransformers)  →  FAISS Index
                                                                         ↓
                                       User Query  →  Semantic Retrieval  →  LLM  →  Response
```

Documents are split into overlapping chunks, each encoded into a dense vector and stored in a local FAISS index. At query time, the top-k semantically similar chunks are retrieved and injected into the LLM prompt — ensuring every response is directly traceable to your source material.

---

## Privacy & Security

| Concern | How it's handled |
|---|---|
| API keys | Stored in `.env`, excluded from version control via `.gitignore` |
| Your PDFs | Processed and stored entirely on your local machine |
| Vector index | FAISS index and chunk files never leave your device |
| External calls | Only the constructed LLM prompt (context + query) is sent to OpenRouter |

---



## Contributing

Pull requests, issues, and feature ideas are welcome. Please open an issue first to discuss any significant changes before submitting a PR.

---

## License

Released under the [MIT License](LICENSE).
