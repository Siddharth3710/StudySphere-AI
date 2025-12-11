#📚 StudySphere-AI
Your AI-powered learning assistant for PDFs, quizzes, flashcards, and summaries.

##✨ Overview

StudySphere-AI is an AI-driven learning platform that transforms PDFs into an interactive study environment using Retrieval-Augmented Generation (RAG) and modern LLMs.

Ask questions, generate summaries, build flashcards, create quizzes, and interact with your study material like never before.

##🚀 Features
###🔍 RAG-Based PDF Question Answering

Extracts text from PDFs

Cleans and chunks content

Builds embeddings using SentenceTransformers

Performs semantic search with FAISS

Produces grounded, context-aware answers

###💬 Interactive Chat Mode

Ask questions directly from your notes

AI responds using retrieved context

Smooth typing/streaming effect

###📝 Exam Generator

Auto-generate MCQs with correct answers

Create open-ended Q&A

Highlight → Focused quiz generation

###📇 Flashcards Mode (Click-to-Flip)

Automatically creates AI flashcards

Each card has a front/back flip animation

Perfect for revising concepts quickly

###🧠 Summarizer

Create bullet summaries

Generate detailed chapter summaries

Adjustable word length

###💾 Persistent Vector Storage

Saves FAISS index + chunks

No need to reprocess PDFs on every run

<img width="706" height="377" alt="image" src="https://github.com/user-attachments/assets/ac1f4d7d-2307-48ea-bebf-8c640a349fc9" />
<img width="691" height="618" alt="image" src="https://github.com/user-attachments/assets/da9255f5-0e74-46b0-8d81-62dfcf2f9d23" />
<img width="471" height="504" alt="image" src="https://github.com/user-attachments/assets/c27fd979-aa75-49e1-adaf-7a7e21fb095e" />
<img width="487" height="215" alt="image" src="https://github.com/user-attachments/assets/e5d841c8-5830-44c8-ba2f-40c5f94cfb3c" />
This prevents hallucinations and ensures responses come from your study material.

##🔒 Security

.env is ignored → API keys stay private

Your PDFs never leave your system

FAISS index and text chunks are stored locally

Only the LLM prompt is sent to OpenRouter

##🚧 Future Improvements

📦 Export flashcards to Anki

🧪 Multi-document knowledge base

🖥️ Offline GGUF-based local model

📊 Learning progress tracking

🗂️ Chapter-wise organization and tagging

🤝 Contributing

Pull requests, issues, and feature ideas are welcome.
Let’s grow StudySphere-AI together.

##📜 License

Licensed under the MIT License.

