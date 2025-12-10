# StudySphere-AI 📚

**StudySphere-AI** — An AI-powered learning assistant that transforms PDFs and study material into an interactive learning platform: chat, summaries, quizzes, flashcards, and more.

## 🚀 Features

- 📄 **PDF Ingestion & RAG Search** — Upload PDF/text material, automatically chunk it into semantic pieces, embed with SentenceTransformers, store in FAISS vector index, and retrieve relevant chunks for context-aware answers.  
- 💬 **Chat Mode** — Ask questions about the material, get context-aware answers powered by LLMs.  
- 📝 **Exam Generator** — Automatically generate MCQs or open-ended Q&A based on document content.  
- 🧠 **Flashcards Generator** — Instantly generate flashcards from document or selected text for quick revision.  
- 🎯 **Highlight-to-Quiz** — Paste or highlight a paragraph/section — get a focused quiz on just that part.  
- 📚 **Summarizer** — Generate summaries (short bullet-style or detailed) for chapters or sections.  
- 🔄 **Vector Store Persistence** — FAISS index + embeddings are saved locally so you don’t need to reprocess PDFs every time.  
- 🌙 **Dark / Polished UI** — Streamlit-based, with a clean, modern UI.

## 🛠️ Tech Stack

- Python 3.x  
- Streamlit — web UI  
- FAISS + Sentence‑Transformers — embeddings + semantic search  
- PyMuPDF (fitz) — PDF text extraction  
- OpenRouter API + Llama 3.1 — LLM inference  
- Native JS + CSS (within Streamlit) — flashcard flip animation  

## 🧑‍💻 Getting Started

### 1. Clone the repo  
```bash
git clone https://github.com/Siddharth3710/StudySphere-AI.git
cd StudySphere-AI
