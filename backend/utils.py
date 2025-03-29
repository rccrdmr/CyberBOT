from evaluate import load
from torch.utils.data import Dataset
import os
import logging


logger = logging.getLogger(__name__)


class QADataset(Dataset):
    def __init__(self, questions, answers, tokenizer, max_len=256):
        assert type(questions) == type(answers), "Questions and answers must be of the same type."

        if type(questions) is not list and hasattr(questions, 'tolist'):
            questions = questions.tolist()
            answers = answers.tolist()
        else:
            assert type(questions) is list, "Questions and answers must be of type list or can be converted to list."
            
        self.questions = questions
        self.answers = answers
        self.tokenizer = tokenizer
        self.max_len = max_len
    
    def __len__(self):
        return len(self.questions)

    def __getitem__(self, item):
        question = self.questions[item]
        answer = self.answers[item]
        inputs = self.tokenizer(question, max_length=self.max_len, truncation=True, padding="max_length", return_tensors='pt')
        return {
            'question': question,
            'answer': answer,
            'input_ids': inputs['input_ids'].squeeze(),
            'attention_mask': inputs['attention_mask'].squeeze()}
    

def evaluate_answer(predictions, references):
    # Load evaluation metrics
    meteor = load('meteor')
    bertscore = load('bertscore')
    rouge = load('rouge')
    bleu = load('bleu')
    
    # Evaluate using BERTScore
    bertscore_result = bertscore.compute(predictions=predictions, references=references, lang="en")
    bertscore_f1 = sum(bertscore_result['f1']) / len(bertscore_result['f1'])

    # Evaluate using METEOR
    meteor_score = meteor.compute(predictions=predictions, references=references)['meteor']
    
    # Evaluate using ROUGE
    rouge_result = rouge.compute(predictions=predictions, references=references)
    
    print("BERTScore F1:", bertscore_f1)
    print("METEOR Score:", meteor_score)
    print("ROUGE-1 Score:", rouge_result["rouge1"])
    print("ROUGE-2 Score:", rouge_result["rouge2"])

    return bertscore_f1, meteor_score, rouge_result["rouge1"], rouge_result["rouge2"]


def remove_prompt(questions, predictions):
    predictions = [p.replace(q, '').strip() for q, p in zip(questions, predictions)]
    return predictions


# 📦 Utility to extract clean user question from full prompt
def extract_user_question(full_prompt: str) -> str:
    try:
        return full_prompt.split("QUESTION:")[-1].split("ANSWER:")[0].strip()
    except Exception:
        return full_prompt.strip()

# 📦 Utility to extract clean answer from full model response
def extract_model_answer(full_response: str) -> str:
    try:
        return full_response.split("Validation Result:")[0].strip()
    except Exception:
        return full_response.strip()
