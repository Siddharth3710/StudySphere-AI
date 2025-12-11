import os
import time
import pathlib
from dotenv import load_dotenv

# Load .env early
env_path = pathlib.Path(__file__).parent / ".env"
load_dotenv(env_path)

import streamlit as st
import numpy as np

# Local imports
from utils.pdf_processor import extract_text_from_pdf
from utils.chunker import clean_text, chunk_text
from utils.embeddings import (
    load_model,
    generate_embeddings,
    create_faiss,
    save_index,
    load_persisted_index,
)
from utils.rag import search
from utils.openrouter import call_ai
from utils.exam import (
    generate_mcq,
    generate_qa,
    generate_flashcards,
    generate_summary,
)

st.set_page_config(page_title="RAG PDF Chatbot", layout="wide")


# -------------------------------------------------------------------
# HELPER FUNCTIONS
# -------------------------------------------------------------------
def parse_mcq(text):
    """Parse MCQ text into structured format"""
    questions = []
    lines = text.strip().split("\n")

    current_q = None
    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect question (starts with Q1:, Q2:, etc.)
        if line.startswith("Q") and ":" in line[:5]:
            if current_q:
                questions.append(current_q)
            current_q = {
                "question": line.split(":", 1)[1].strip(),
                "options": [],
                "correct": "",
            }
        # Detect options (A), B), C), D))
        elif current_q and line[0] in "ABCD" and ")" in line[:3]:
            current_q["options"].append(line)
        # Detect correct answer
        elif current_q and line.lower().startswith("correct"):
            current_q["correct"] = (
                line.split(":", 1)[1].strip() if ":" in line else line.split()[-1]
            )

    if current_q:
        questions.append(current_q)

    return questions


def parse_qa(text):
    """Parse Q&A text into structured format"""
    questions = []
    lines = text.strip().split("\n")

    current_q = None
    current_answer = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect question
        if line.startswith("Q") and ":" in line[:5]:
            if current_q:
                current_q["answer"] = " ".join(current_answer).strip()
                questions.append(current_q)
                current_answer = []

            current_q = {"question": line.split(":", 1)[1].strip(), "answer": ""}
        # Detect answer
        elif current_q and (
            line.lower().startswith("answer:") or line.lower().startswith("a:")
        ):
            answer_text = line.split(":", 1)[1].strip() if ":" in line else ""
            current_answer.append(answer_text)
        # Continue answer
        elif current_q and current_answer:
            current_answer.append(line)

    if current_q:
        current_q["answer"] = " ".join(current_answer).strip()
        questions.append(current_q)

    return questions


def format_answer(text):
    """Format answer text for better readability with proper line breaks"""
    # Split by common delimiters
    lines = text.split("\n")
    formatted_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Handle numbered lists (1. 2. 3.)
        if line and line[0].isdigit() and ". " in line[:4]:
            formatted_lines.append(f"\n**{line}**")
        # Handle bullet points (- or * or •)
        elif line.startswith(("-", "*", "•")):
            formatted_lines.append(f"\n{line}")
        # Handle sentences ending with : (likely introducing a list)
        elif line.endswith(":"):
            formatted_lines.append(f"\n**{line}**")
        else:
            formatted_lines.append(line)

    # Join with proper spacing
    result = " ".join(formatted_lines)

    # Ensure bullet points and numbered items are on new lines
    result = result.replace(" \n", "\n")

    return result


# -------------------------------------------------------------------
# SESSION STATE
# -------------------------------------------------------------------
ss = st.session_state
for k, v in {
    "text": None,
    "chunks": None,
    "model": None,
    "embeddings": None,
    "index": None,
    "exam": None,
    "flashcards": None,
}.items():
    if k not in ss:
        ss[k] = v


# -------------------------------------------------------------------
# Try restoring saved FAISS index
# -------------------------------------------------------------------
if ss.index is None and ss.chunks is None:
    idx, chunks = load_persisted_index()
    if idx is not None:
        ss.index = idx
        ss.chunks = chunks
        ss.model = load_model()


# -------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["📤 Upload", "💬 Learn Mode", "📝 Exam Mode", "🧠 Summarizer", "📇 Flashcards"]
)

# -------------------------------------------------------------------
# TAB 1: UPLOAD
# -------------------------------------------------------------------
with tab1:
    st.header("Upload & Process PDF")
    pdf = st.file_uploader("Upload PDF", type="pdf")

    if pdf and st.button("Process PDF"):
        raw, pages = extract_text_from_pdf(pdf.read())
        cleaned = clean_text(raw)
        ss.text = cleaned

        chunks = chunk_text(cleaned)
        ss.chunks = chunks

        model = load_model()
        ss.model = model

        embs = generate_embeddings(chunks, model)
        index = create_faiss(embs)
        ss.index = index

        save_index(index, chunks)
        st.success(f"Processed {pages} pages into {len(chunks)} chunks & saved index!")


# -------------------------------------------------------------------
# TAB 2: LEARN MODE (IMPROVED)
# -------------------------------------------------------------------
with tab2:
    st.header("💬 Chat with PDF")

    if not ss.index:
        st.warning("⚠️ Upload or load stored index first.")
    else:
        # Initialize chat history in session state
        if "chat_history" not in ss:
            ss.chat_history = []

        # Question input with button
        col1, col2 = st.columns([5, 1])
        with col1:
            q = st.text_input(
                "Ask something from PDF:",
                placeholder="e.g., What are the key concepts in this document?",
                key="learn_question",
            )
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            ask_button = st.button("🚀 Ask", use_container_width=True, type="primary")

        if ask_button and q:
            with st.spinner("🔍 Searching and generating answer..."):
                # Search for relevant chunks
                results = search(q, ss.model, ss.index, ss.chunks)
                context = "\n\n".join([r["chunk"] for r in results])

                # Improved prompt for better formatting
                prompt = f"""Context from the document:
{context}

Question: {q}

Please provide a clear, well-formatted answer. If listing multiple points:
- Use bullet points (one per line)
- Number steps if showing a process
- Use clear paragraph breaks
- Be concise but complete"""

                answer = call_ai(prompt)

                # Store in chat history
                ss.chat_history.append(
                    {"question": q, "answer": answer, "sources": results}
                )

        # Display chat history
        if ss.chat_history:
            st.divider()

            for i, chat in enumerate(reversed(ss.chat_history)):
                # Question card
                st.markdown(
                    f"""
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            padding: 15px 20px; border-radius: 12px; margin: 10px 0;">
                    <strong style="color: white; font-size: 16px;">❓ {chat['question']}</strong>
                </div>
                """,
                    unsafe_allow_html=True,
                )

                # Answer card with better formatting
                st.markdown(
                    """
                <div style="background: rgba(34, 197, 94, 0.1); padding: 20px; 
                            border-radius: 12px; border-left: 4px solid #22c55e; margin: 10px 0;">
                """,
                    unsafe_allow_html=True,
                )

                # Format the answer for better readability
                formatted_answer = format_answer(chat["answer"])
                st.markdown(formatted_answer)

                st.markdown("</div>", unsafe_allow_html=True)

                # Sources in expander
                with st.expander("📚 View Sources", expanded=False):
                    for idx, src in enumerate(chat["sources"], 1):
                        st.markdown(f"**Source {idx}** (Relevance: {src['score']:.2%})")
                        st.text_area(
                            "",
                            src["chunk"],
                            height=100,
                            disabled=True,
                            key=f"source_{i}_{idx}",
                            label_visibility="collapsed",
                        )

                st.divider()

            # Clear history button
            if st.button("🗑️ Clear Chat History", use_container_width=True):
                ss.chat_history = []
                st.rerun()


# -------------------------------------------------------------------
# TAB 3: EXAM MODE (IMPROVED WITH SHOW ANSWER BUTTONS)
# -------------------------------------------------------------------
with tab3:
    st.header("📝 Practice Tests")

    if not ss.chunks:
        st.warning("⚠️ Upload a PDF first.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            t = st.selectbox("Type", ["MCQ", "Q&A"], key="exam_type_selector")
        with col2:
            n = st.slider("Count", 1, 15, 3, key="exam_count_slider")

        if st.button("🎯 Generate Test", type="primary", use_container_width=True):
            with st.spinner(f"Generating {n} {t} questions..."):
                context = "\n\n".join(ss.chunks[:8])
                if t == "MCQ":
                    ss.exam = generate_mcq(context, n)
                    ss.exam_type = "MCQ"
                else:
                    ss.exam = generate_qa(context, n)
                    ss.exam_type = "Q&A"

                # Reset answer visibility
                ss.show_answers = {}

            st.success(f"✅ Generated {n} {t} questions!")
            st.rerun()

        if ss.exam:
            st.divider()

            # Initialize answer visibility tracker
            if "show_answers" not in ss:
                ss.show_answers = {}

            # Parse and display based on type
            if ss.exam_type == "MCQ":
                # Parse MCQ format
                questions = parse_mcq(ss.exam)

                st.subheader(f"📋 Multiple Choice Questions ({len(questions)} total)")

                for i, q in enumerate(questions):
                    st.markdown(f"### Question {i+1}")

                    # Question card
                    st.markdown(
                        f"""
                    <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                padding: 20px; border-radius: 12px; color: white; margin: 10px 0;">
                        <strong style="font-size: 18px;">{q['question']}</strong>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Options
                    st.markdown(
                        """
                    <div style="background: rgba(255,255,255,0.05); padding: 15px; 
                                border-radius: 8px; margin: 10px 0;">
                    """,
                        unsafe_allow_html=True,
                    )

                    for opt in q["options"]:
                        st.markdown(f"**{opt}**")

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Show/Hide Answer button
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button(
                            (
                                "👁️ Show Answer"
                                if not ss.show_answers.get(f"mcq_{i}")
                                else "🔙 Hide Answer"
                            ),
                            key=f"toggle_mcq_{i}",
                            use_container_width=True,
                        ):
                            ss.show_answers[f"mcq_{i}"] = not ss.show_answers.get(
                                f"mcq_{i}", False
                            )
                            st.rerun()

                    # Display answer if toggled
                    if ss.show_answers.get(f"mcq_{i}"):
                        st.success(f"✅ **Correct Answer:** {q['correct']}")

                    st.divider()

            else:  # Q&A mode
                questions = parse_qa(ss.exam)

                st.subheader(f"💭 Open-Ended Questions ({len(questions)} total)")

                for i, q in enumerate(questions):
                    st.markdown(f"### Question {i+1}")

                    # Question card
                    st.markdown(
                        f"""
                    <div style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                                padding: 20px; border-radius: 12px; color: white; margin: 10px 0;">
                        <strong style="font-size: 18px;">{q['question']}</strong>
                    </div>
                    """,
                        unsafe_allow_html=True,
                    )

                    # Show/Hide Answer button
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button(
                            (
                                "👁️ Show Answer"
                                if not ss.show_answers.get(f"qa_{i}")
                                else "🔙 Hide Answer"
                            ),
                            key=f"toggle_qa_{i}",
                            use_container_width=True,
                        ):
                            ss.show_answers[f"qa_{i}"] = not ss.show_answers.get(
                                f"qa_{i}", False
                            )
                            st.rerun()

                    # Display answer if toggled
                    if ss.show_answers.get(f"qa_{i}"):
                        st.markdown(
                            """
                        <div style="background: rgba(34, 197, 94, 0.1); padding: 15px; 
                                    border-radius: 8px; border-left: 4px solid #22c55e; margin: 10px 0;">
                        """,
                            unsafe_allow_html=True,
                        )
                        st.markdown(f"**Answer:** {q['answer']}")
                        st.markdown("</div>", unsafe_allow_html=True)

                    st.divider()

            # Download and control buttons
            st.divider()
            col1, col2, col3 = st.columns(3)

            with col1:
                st.download_button(
                    "📥 Download Test",
                    ss.exam,
                    f"test_{ss.exam_type.lower()}.txt",
                    use_container_width=True,
                )

            with col2:
                if st.button("👁️ Show All Answers", use_container_width=True):
                    # Show all answers
                    if ss.exam_type == "MCQ":
                        for i in range(len(parse_mcq(ss.exam))):
                            ss.show_answers[f"mcq_{i}"] = True
                    else:
                        for i in range(len(parse_qa(ss.exam))):
                            ss.show_answers[f"qa_{i}"] = True
                    st.rerun()

            with col3:
                if st.button("🔙 Hide All Answers", use_container_width=True):
                    ss.show_answers = {}
                    st.rerun()


# -------------------------------------------------------------------
# TAB 4: SUMMARIZER
# -------------------------------------------------------------------
with tab4:
    st.header("Summarizer")

    if not ss.chunks:
        st.warning("Process a PDF first.")
    else:
        style = st.radio("Format", ["Short bullet points", "Detailed summary"])
        words = st.slider("Word limit", 100, 600, 250)
        custom = st.text_area("Paste section to summarize (optional):")

        if st.button("Generate Summary"):
            context = custom.strip() or "\n\n".join(ss.chunks[:10])
            summary = generate_summary(context, style, words)
            st.write(summary)


# -------------------------------------------------------------------
# TAB 5: FLASHCARDS (IMPROVED - SHOWS ALL CARDS)
# -------------------------------------------------------------------
with tab5:
    st.header("🎴 Flashcards")

    if not ss.chunks:
        st.warning("⚠️ Process a PDF first to generate flashcards.")
    else:
        col1, col2 = st.columns([2, 1])

        with col1:
            num = st.slider("Number of flashcards", 3, 20, 5, key="flash_num")
        with col2:
            st.metric("Cards to generate", num)

        base = st.text_area(
            "Optional: Paste specific text for focused flashcards",
            height=100,
            placeholder="Leave empty to generate from entire document...",
            key="flash_text",
        )

        if st.button(
            "✨ Generate Flashcards", type="primary", use_container_width=True
        ):
            with st.spinner("Creating flashcards..."):
                context = base.strip() or "\n\n".join(ss.chunks[:12])
                ss.flashcards = generate_flashcards(context, num)
                # Reset flip states
                ss.flipped_cards = set()

            # Show how many were actually generated
            if ss.flashcards:
                st.success(f"✅ Generated {len(ss.flashcards)} flashcards!")
                st.rerun()
            else:
                st.error("❌ Failed to generate flashcards. Please try again.")

        if ss.flashcards and len(ss.flashcards) > 0:
            st.divider()

            # Initialize flipped cards tracking
            if "flipped_cards" not in ss:
                ss.flipped_cards = set()

            # Show total count
            st.info(f"📚 Showing {len(ss.flashcards)} flashcards")

            # Control buttons
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                if st.button("🔄 Flip All", use_container_width=True):
                    if len(ss.flipped_cards) == len(ss.flashcards):
                        ss.flipped_cards = set()
                    else:
                        ss.flipped_cards = set(range(len(ss.flashcards)))
                    st.rerun()
            with col2:
                if st.button("🔀 Shuffle", use_container_width=True):
                    import random

                    random.shuffle(ss.flashcards)
                    ss.flipped_cards = set()
                    st.rerun()
            with col3:
                st.metric("Studied", f"{len(ss.flipped_cards)}/{len(ss.flashcards)}")
            with col4:
                if st.button("🗑️ Clear", use_container_width=True):
                    ss.flashcards = None
                    ss.flipped_cards = set()
                    st.rerun()

            st.divider()
            st.markdown("### 💡 Click 'Show Answer' to reveal each card")

            # CSS for card styling
            st.markdown(
                """
            <style>
            .flashcard {
                border-radius: 16px;
                padding: 25px 20px;
                margin: 8px 0;
                min-height: 140px;
                display: flex;
                flex-direction: column;
                justify-content: center;
                align-items: center;
                text-align: center;
                font-size: 16px;
                font-weight: 500;
                line-height: 1.5;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
                transition: all 0.3s ease;
                position: relative;
            }
            
            .flashcard:hover {
                box-shadow: 0 8px 16px rgba(0, 0, 0, 0.25);
                transform: translateY(-3px);
            }
            
            .card-front {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: 3px solid rgba(255, 255, 255, 0.3);
            }
            
            .card-back {
                background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
                color: white;
                border: 3px solid rgba(255, 255, 255, 0.3);
            }
            
            .card-badge {
                position: absolute;
                top: 10px;
                left: 12px;
                background: rgba(255, 255, 255, 0.35);
                padding: 5px 12px;
                border-radius: 15px;
                font-size: 12px;
                font-weight: bold;
            }
            
            .card-icon {
                position: absolute;
                top: 10px;
                right: 12px;
                font-size: 22px;
                opacity: 0.8;
            }
            
            .card-content {
                padding: 25px 15px 15px 15px;
                width: 100%;
            }
            </style>
            """,
                unsafe_allow_html=True,
            )

            # Display cards in a 3-column grid
            cols_per_row = 3

            # Process each card
            for i in range(0, len(ss.flashcards), cols_per_row):
                cols = st.columns(cols_per_row)

                for j in range(cols_per_row):
                    idx = i + j
                    if idx >= len(ss.flashcards):
                        break

                    card = ss.flashcards[idx]
                    is_flipped = idx in ss.flipped_cards

                    with cols[j]:
                        # Determine which side to show
                        if is_flipped:
                            # Show back (answer)
                            card_html = f"""
                            <div class="flashcard card-back">
                                <div class="card-badge">Card {idx + 1}</div>
                                <div class="card-icon">✓</div>
                                <div class="card-content">
                                    {str(card.get('back', 'Answer')).replace('<', '&lt;').replace('>', '&gt;')}
                                </div>
                            </div>
                            """
                        else:
                            # Show front (question)
                            card_html = f"""
                            <div class="flashcard card-front">
                                <div class="card-badge">Card {idx + 1}</div>
                                <div class="card-icon">❓</div>
                                <div class="card-content">
                                    {str(card.get('front', 'Question')).replace('<', '&lt;').replace('>', '&gt;')}
                                </div>
                            </div>
                            """

                        st.markdown(card_html, unsafe_allow_html=True)

                        # Flip button
                        button_label = (
                            "🔙 Show Question" if is_flipped else "👁️ Show Answer"
                        )
                        if st.button(
                            button_label, key=f"flip_{idx}", use_container_width=True
                        ):
                            if is_flipped:
                                ss.flipped_cards.discard(idx)
                            else:
                                ss.flipped_cards.add(idx)
                            st.rerun()

                # Add some spacing between rows
                st.markdown("<br>", unsafe_allow_html=True)

            # Download option
            st.divider()
            flashcard_text = "\n\n".join(
                [
                    f"Card {i+1}\nQ: {card['front']}\nA: {card['back']}"
                    for i, card in enumerate(ss.flashcards)
                ]
            )
            st.download_button(
                "📥 Download All Flashcards as Text File",
                flashcard_text,
                "flashcards.txt",
                use_container_width=True,
            )
