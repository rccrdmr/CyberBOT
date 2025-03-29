import os
import logging
from together import Together
from collections import defaultdict
from utils import extract_user_question, extract_model_answer

# Logging Configuration
logger = logging.getLogger(__name__)

# Together AI API Configuration
TOGETHER_API_KEY = os.getenv("TOGETHER_API_KEY")

if not TOGETHER_API_KEY:
    raise ValueError("❌ Missing Together API key! Set TOGETHER_API_KEY as an environment variable.")

# Define Model for Answering
MODEL_NAME = "meta-llama/Llama-3.3-70B-Instruct-Turbo"

# Initialize Client
client = Together(api_key=TOGETHER_API_KEY)

# Maintain per-user chat history
chat_histories = defaultdict(lambda: [
    {"role": "system", "content": "You are an expert assistant in cybersecurity and cloud computing. Answer user queries clearly and helpfully."}
])

def get_response(input_text, user_id, max_tokens=None, skip_history_append=False):
    try:
        clean_question = extract_user_question(input_text)

        # Only store clean question in memory
        if not skip_history_append:
            chat_histories[user_id].append({"role": "user", "content": clean_question})

        # Model sees chat memory + full prompt for current turn
        full_messages = chat_histories[user_id][:-1] + [{"role": "user", "content": str(input_text)}]

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=full_messages,
            max_tokens=max_tokens,
            temperature=0.7,
            top_p=1.0
        )

        if response is None or not hasattr(response, "choices") or not response.choices:
            logger.warning("❌ Empty or malformed Together AI response.")
            return None

        # Append assistant reply
        full_answer = response.choices[0].message.content.strip()
        clean_answer = extract_model_answer(full_answer)

        if not skip_history_append:
            chat_histories[user_id].append({"role": "assistant", "content": clean_answer})

        return response

    except Exception as e:
        logger.exception("❌ Error calling Together AI API")
        return None

def augment_question(user_id, current_question, max_tokens=100):
    """
    Use LLM to generate an intent-aware version of the current user question
    based on chat history context.
    """
    # Build the last 2 user-assistant exchanges (up to 4 messages)
    memory = ""
    for msg in chat_histories[user_id][-4:]:
        memory += f"{msg['role'].capitalize()}: {msg['content']}\n"

    rewrite_prompt = f"""You are an assistant that rewrites vague or follow-up user questions based on previous conversation history.
    Given the chat history and current question, rewrite the question to make it fully self-contained, specific, and intent-aware.

    CHAT HISTORY:
    {memory}

    CURRENT QUESTION:
    {current_question}

    REWRITTEN QUESTION:
    """

    # print(f"\n📤 Prompt sent to LLM for question rewriting (user {user_id}):\n{rewrite_prompt.strip()}\n")

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are a rewrite assistant. You ONLY return rewritten user questions, nothing else. No commentary."},
            {"role": "user", "content": rewrite_prompt}
        ],
        max_tokens=max_tokens,
        temperature=0.5,
        top_p=1.0
    )

    if response and response.choices:
        rewritten_question = response.choices[0].message.content.strip()
        if rewritten_question != current_question:
            logger.info(f"Original: {current_question}\nRewritten: {rewritten_question}")
        return rewritten_question

    return current_question  # fallback if rewrite fails


# Optional test block
if __name__ == "__main__":
    response = get_response("What is a vulnerability in cybersecurity?", max_tokens=100)
    print(response.choices[0].message.content.strip() if response else "❌ Failed to get response.")

    response = get_response("How can attackers exploit it?", max_tokens=100)
    print(response.choices[0].message.content.strip() if response else "❌ Failed to get response.")
