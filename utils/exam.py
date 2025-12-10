import json
import re
from utils.openrouter import call_ai


def generate_mcq(context: str, n: int):
    """Generate multiple choice questions"""
    prompt = f"""
Create {n} multiple-choice questions from the content below.

Follow this exact format:
Q1: [Question text]
A) [Option A]
B) [Option B]
C) [Option C]
D) [Option D]
Correct: [Letter]

Q2: [Question text]
...

Content:
{context}
"""
    return call_ai(
        prompt,
        system="You are an expert exam paper setter. Create clear, educational MCQs.",
        max_tokens=2500,
    )


def generate_qa(context: str, n: int):
    """Generate open-ended Q&A"""
    prompt = f"""
Create {n} open-ended questions and detailed answers from the content.

Format:
Q1: [Question]
Answer: [Detailed answer]

Q2: [Question]
Answer: [Detailed answer]

Content:
{context}
"""
    return call_ai(
        prompt,
        system="You are an expert teacher creating study questions.",
        max_tokens=2500,
    )


def generate_flashcards(context: str, n: int = 10):
    """
    Generate flashcards with EXTENSIVE debugging
    """
    # Simplified, more explicit prompt
    prompt = f"""Create {n} flashcards from this content. 

Output ONLY a JSON array like this example:
[{{"front":"What is IoT?","back":"Internet of Things - network of connected devices"}},{{"front":"Key benefit?","back":"Automation and efficiency"}}]

Rules:
- Output ONLY the JSON array, nothing else
- No markdown, no explanations, no code blocks
- Start with [ and end with ]
- Use double quotes for all strings
- Keep front and back short

Content to make flashcards from:
{context[:2000]}"""

    try:
        # Call AI with high token limit
        response = call_ai(
            prompt,
            system="You output ONLY valid JSON arrays. No other text.",
            max_tokens=3000,
        )

        print(f"\n=== DEBUG: RAW AI RESPONSE ===")
        print(f"Response length: {len(response)} chars")
        print(f"First 500 chars: {response[:500]}")
        print(f"Last 200 chars: {response[-200:]}")
        print(f"=== END DEBUG ===\n")

        # Clean response
        response = response.strip()

        # Method 1: Direct parse
        try:
            cards = json.loads(response)
            if isinstance(cards, list) and len(cards) > 0:
                valid_cards = [
                    {"front": str(c["front"])[:300], "back": str(c["back"])[:500]}
                    for c in cards
                    if isinstance(c, dict) and "front" in c and "back" in c
                ]
                if valid_cards:
                    print(f"✅ Method 1 SUCCESS: Parsed {len(valid_cards)} cards")
                    return valid_cards
        except json.JSONDecodeError as e:
            print(f"❌ Method 1 FAILED: {e}")

        # Method 2: Extract from code blocks
        json_match = re.search(r"```(?:json)?\s*(\[.*?\])\s*```", response, re.DOTALL)
        if json_match:
            try:
                cards = json.loads(json_match.group(1))
                if isinstance(cards, list) and len(cards) > 0:
                    valid_cards = [
                        {"front": str(c["front"])[:300], "back": str(c["back"])[:500]}
                        for c in cards
                        if isinstance(c, dict) and "front" in c and "back" in c
                    ]
                    if valid_cards:
                        print(f"✅ Method 2 SUCCESS: Parsed {len(valid_cards)} cards")
                        return valid_cards
            except json.JSONDecodeError as e:
                print(f"❌ Method 2 FAILED: {e}")

        # Method 3: Find array boundaries
        start = response.find("[")
        end = response.rfind("]") + 1
        if start != -1 and end > start:
            try:
                json_str = response[start:end]
                print(f"Method 3: Trying to parse: {json_str[:200]}...")
                cards = json.loads(json_str)
                if isinstance(cards, list) and len(cards) > 0:
                    valid_cards = [
                        {"front": str(c["front"])[:300], "back": str(c["back"])[:500]}
                        for c in cards
                        if isinstance(c, dict) and "front" in c and "back" in c
                    ]
                    if valid_cards:
                        print(f"✅ Method 3 SUCCESS: Parsed {len(valid_cards)} cards")
                        return valid_cards
            except json.JSONDecodeError as e:
                print(f"❌ Method 3 FAILED: {e}")

        # Method 4: Manual parsing as last resort
        # Try to find individual card objects
        card_pattern = r'\{\s*["\']front["\']\s*:\s*["\']([^"\']+)["\']\s*,\s*["\']back["\']\s*:\s*["\']([^"\']+)["\']\s*\}'
        matches = re.findall(card_pattern, response, re.IGNORECASE)

        if matches:
            manual_cards = [
                {"front": front.strip(), "back": back.strip()}
                for front, back in matches
            ]
            if manual_cards:
                print(f"✅ Method 4 SUCCESS: Manually parsed {len(manual_cards)} cards")
                return manual_cards

        # All methods failed - return detailed error
        return [
            {
                "front": "⚠️ Could Not Parse Response",
                "back": f"""All parsing methods failed.

Response length: {len(response)} chars
Started with: {response[:100]}
Ended with: {response[-100:]}

Check terminal/console for full debug output.""",
            }
        ]

    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        import traceback

        traceback.print_exc()

        return [
            {
                "front": "❌ Error in Flashcard Generation",
                "back": f"Exception: {str(e)}\n\nCheck console for full traceback.",
            }
        ]


def generate_summary(context: str, style: str, max_words: int):
    """Generate summary with specified style and length"""
    style_text = "bullet points" if "Short" in style else "detailed paragraphs"

    prompt = f"""
Summarize the following content using {style_text}.

Requirements:
- Target length: approximately {max_words} words
- Be clear and concise
- Capture key points and main ideas
- Use simple language

Content:
{context[:4000]}
"""
    return call_ai(
        prompt,
        system="You are a world-class summarizer. Create clear, accurate summaries.",
        max_tokens=2000,
    )
