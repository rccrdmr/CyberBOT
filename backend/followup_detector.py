# followup_detector.py

import re
from typing import Tuple

# Generalized follow-up keyword set (contextual and semantic indicators)
FOLLOWUP_KEYWORDS = {
    # Clarification & Precision
    "clarify", "clarification", "elaborate", "explain", "expand", "detail",
    "precise", "specific", "rephrase", "example", "examples",

    # Confusion & Repetition
    "confused", "unclear", "vague", "repeat", "restate", "again", "simplify",

    # Continuation & Follow-up
    "more", "else", "additionally", "next", "another", "continue", "further",

    # Confirmation
    "right", "correct", "sure", "true",

    # Discourse Markers / Fillers
    "well", "so", "then", "also", "okay", "thanks", "but",

    # Interactive / Request verbs
    "tell", "show", "describe", "demonstrate", "illustrate", "talk", "speak"
}

REFERENTIAL_PHRASES = [
    "in that case", "from that", "based on that", "with that",
    "as mentioned", "as described", "as we discussed"
]

PRONOUNS = {"it", "they", "this", "that", "those", "these", "he", "she", "him", "her"}

STARTER_PHRASES = [
    "can you be more specific", "can you elaborate", "can you explain",
    "please clarify", "what else", "how so", "why is that", "i’m still confused",
    "be more precise", "tell me more", "give me another example",
    "is that right", "am i correct", "so you mean"
]

def is_followup_question(question: str) -> Tuple[bool, str]:
    """
    Classifies whether a question is likely a follow-up.
    Returns (True/False, reason_string)
    """
    question = question.strip().lower()
    words = set(question.split())

    # Rule 1: Exact phrase match (starter phrases)
    for phrase in STARTER_PHRASES:
        if phrase in question:
            return True, f"Matched starter phrase: '{phrase}'"

    # Rule 2: Presence of vague/interactive keywords
    keyword_matches = words.intersection(FOLLOWUP_KEYWORDS)
    if keyword_matches:
        return True, f"Matched follow-up keywords: {', '.join(keyword_matches)}"

    # Rule 3: Pronouns used in short question
    if len(words) <= 6 and words.intersection(PRONOUNS):
        return True, f"Short question with pronoun(s): {', '.join(words.intersection(PRONOUNS))}"

    # Rule 4: Short ambiguous questions
    if len(words) <= 6:
        return True, "Question is very short and likely ambiguous"

    # Rule 5: Starts with discourse markers
    if re.match(r"^(so|well|then|also|but|okay)\\b", question):
        return True, "Starts with discourse marker"

    # Rule 6: Referential phrases
    for phrase in REFERENTIAL_PHRASES:
        if phrase in question:
            return True, f"Matched referential phrase: '{phrase}'"

    #  Rule 7: Context-dependent starters
    if question.startswith("is there a way") or question.startswith("what kind of"):
        return True, "Generic follow-up phrasing detected"

    return False, "No follow-up indicators detected"


# Example usage / test block
if __name__ == "__main__":
    test_questions = [
        "Can you elaborate on that?",
        "What is virtualization in cloud computing?",
        "Tell me more about encryption",
        "So what else should I ask?",
        "It is important, right?",
        "Describe a real-world attack",
        "What else?",
        "Give me another example"
    ]

    for q in test_questions:
        result, reason = is_followup_question(q)
        print(f"\n🧠 Question: {q}\n🔍 Follow-up? {result} | Reason: {reason}")
