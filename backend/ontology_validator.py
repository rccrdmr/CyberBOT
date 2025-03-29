import os
import json
import re
import logging
from llm_infer import get_response
from pathlib import Path

logger = logging.getLogger(__name__)

# ✅ Define Ontology File Path
ROOT_DIR = Path(__file__).resolve().parent
ONTOLOGY_PATH = ROOT_DIR / "dataset" / "ontology" / "ontology.txt"

def ontology_validation(question, answer, user_id):
    """Validates AI-generated answers against the full ontology and returns Pass/Not Pass, score, and explanation."""
    try:
        # ✅ Load entire ontology text
        try:
            with open(ONTOLOGY_PATH, "r") as f:
                ontology_text = f.read().strip()
        except Exception as e:
            logger.error(f"⚠️ Failed to load ontology file: {e}")
            return {"validation_result": "Error", "confidence_score": 0.0, "reasoning": "Failed to read ontology file."}

        # ✅ Strict JSON-Only Validation Prompt
        validation_prompt = f"""
        Your task is to evaluate whether the ANSWER correctly aligns with the ONTOLOGY provided below.

        Return ONLY a JSON response in the format:
        {{
        "validation_result": "Pass" or "Not Pass",
        "confidence_score": CONFIDENCE_SCORE_HERE (between 0 and 1),
        "reasoning": "A brief explanation of why the answer is valid or not."
        }}

        DO NOT include anything outside of this JSON structure.

        Here are a few examples:

        ---
        Example 1 (Cybersecurity - Valid Answer, High Confidence):
        QUESTION: What is a vulnerability in cybersecurity?
        ANSWER: A vulnerability is a weakness in a system that can be exploited by an attacker.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Pass",
        "confidence_score": 0.95,
        "reasoning": "Answer maps to 'system, can_expose, vulnerability' and 'attacker, can_exploit, vulnerability'."
        }}

        ---
        Example 2 (Cloud Computing - Valid Answer, High Confidence):
        QUESTION: What is virtualization in cloud computing?
        ANSWER: Virtualization is a technique that allows multiple virtual machines to run on a single physical system.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Pass",
        "confidence_score": 0.92,
        "reasoning": "Answer maps to 'Concept/technique = Virtualization' in cloud computing ontology."
        }}

        ---
        Example 3 (Cybersecurity - Valid Answer, Medium-High Confidence):
        QUESTION: What tool can be used to analyze vulnerabilities?
        ANSWER: A logging tool.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Pass",
        "confidence_score": 0.68,
        "reasoning": "Although brief, the answer is grounded in concepts like 'tool' and 'can_analyze vulnerability'."
        }}

        ---
        Example 4 (Cloud Computing - Valid Answer, Medium-High Confidence):
        QUESTION: What techniques are used for load distribution in cloud computing?
        ANSWER: Load balancing and auto-scaling are common techniques.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Pass",
        "confidence_score": 0.7,
        "reasoning": "Answer correctly reflects cloud computing techniques from the ontology."
        }}

        ---
        Example 5 (Cybersecurity - Vague Answer, Low Confidence):
        QUESTION: What are security techniques in cybersecurity?
        ANSWER: Techniques are used to protect systems.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Not Pass",
        "confidence_score": 0.4,
        "reasoning": "Answer is too vague and not grounded in specific ontology concepts like 'Risk Assessment' or 'HoneyPot'."
        }}

        ---
        Example 6 (Cloud Computing - Vague Answer, Low Confidence):
        QUESTION: What are characteristics of cloud computing?
        ANSWER: Cloud computing has many features.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Not Pass",
        "confidence_score": 0.35,
        "reasoning": "Answer is too vague and does not mention ontology-grounded concepts like 'on-demand self-service' or 'resource pooling'."
        }}

        ---
        Example 7 (Neither - Irrelevant Answer, Zero Confidence):
        QUESTION: What is the capital of France?
        ANSWER: Paris is the capital of France.
        EXPECTED VALIDATION RESPONSE:
        {{
        "validation_result": "Not Pass",
        "confidence_score": 0.0,
        "reasoning": "Answer is factually correct but completely unrelated to cybersecurity or cloud computing ontology."
        }}

        Now evaluate the actual input below:

        QUESTION:
        {question}

        ANSWER:
        {answer}

        ONTOLOGY:
        {ontology_text}
        """

        response = get_response(input_text=validation_prompt, user_id=user_id, max_tokens=200, skip_history_append=True)

        if response is None:
            logger.error(f"❌ Together AI returned None for validation")
            print("\n❌ Validation Decision: Error - No Response from AI")
            return {"validation_result": "Error", "confidence_score": 0.0, "reasoning": "No response from AI."}

        response_content = response.choices[0].message.content.strip()
        print("\n🔍 Validation Decision:", response_content)

        try:
            validation_data = json.loads(response_content)
        except json.JSONDecodeError:
            logger.warning(f"⚠️ AI Response not valid JSON: {response_content}")
            match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if match:
                try:
                    validation_data = json.loads(match.group(0))
                except json.JSONDecodeError:
                    logger.error(f"❌ Ontology validation failed: Could not parse extracted JSON")
                    return {"validation_result": "Error", "confidence_score": 0.0, "reasoning": "Failed to parse AI response."}
            else:
                logger.error(f"❌ Ontology validation failed: No JSON structure found")
                return {"validation_result": "Error", "confidence_score": 0.0, "reasoning": "No valid JSON found in AI response."}

        # ✅ Enforce expected validation result structure
        result = validation_data.get("validation_result", "Error")
        score = validation_data.get("confidence_score", 0.0)
        reasoning = validation_data.get("reasoning", "No reasoning provided")

        if result == "Pass":
            return {"validation_result": "Pass", "confidence_score": score, "reasoning": reasoning}
        else:
            return {"validation_result": "Not Pass", "confidence_score": score, "reasoning": reasoning}

    except Exception as e:
        logger.error(f"⚠️ Ontology Validation Error: {e}")
        print("\n⚠️ Validation Decision: Error - Exception Occurred")
        return {"validation_result": "Error", "confidence_score": 0.0, "reasoning": "Exception occurred during validation."}
