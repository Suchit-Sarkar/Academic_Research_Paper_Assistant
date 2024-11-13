from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline, AutoTokenizer, AutoModelForQuestionAnswering, AutoModelForSeq2SeqLM
from typing import Optional
from transformers import pipeline
# Initialize the FastAPI app
app = FastAPI()

# Load Hugging Face models for Summarization and Q&A
# Use a lightweight model like `distilbart-cnn-12-6` for summarization
# Use GPU for summarization by setting device=0 (for the first GPU)
summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6", framework="pt", device=0)


# Use a lightweight model for Question Answering, like `distilbert-base-uncased-distilled-squad`
tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased-distilled-squad")
qa_model = AutoModelForQuestionAnswering.from_pretrained("distilbert-base-uncased-distilled-squad")

class SummarizeRequest(BaseModel):
    content: str  # Text of the research paper

class QuestionRequest(BaseModel):
    context: str  # Text of the research paper
    question: str  # User's question

### Endpoint: Summarization ###
@app.post("/summarize/")
def summarize_paper(request: SummarizeRequest):
    content = request.content
    
    try:
        # Perform summarization on the provided content
        summary = summarizer(content, max_length=150, min_length=30, do_sample=False)
        return {"summary": summary[0]['summary_text']}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

### Endpoint: Question Answering ###
@app.post("/answer_question/")
def answer_question(request: QuestionRequest):
    context = request.context
    question = request.question

    try:
        # Tokenize input for the Q&A model
        inputs = tokenizer(question, context, return_tensors="pt", truncation=True)
        outputs = qa_model(**inputs)

        # Extract answer span with highest score
        answer_start = outputs.start_logits.argmax()
        answer_end = outputs.end_logits.argmax()
        answer = tokenizer.convert_tokens_to_string(
            tokenizer.convert_ids_to_tokens(inputs.input_ids[0][answer_start: answer_end + 1])
        )
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
