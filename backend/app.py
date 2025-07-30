from flask import Flask, request, jsonify
from transformers import T5Tokenizer, T5ForConditionalGeneration
import torch
import pdfplumber
import os
from flask_cors import CORS
app = Flask(__name__)
CORS(app)

# Load T5 Model
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
tokenizer = T5Tokenizer.from_pretrained("google/t5-efficient-tiny")
model = T5ForConditionalGeneration.from_pretrained("google/t5-efficient-tiny", 
    low_cpu_mem_usage=True,
    torch_dtype=torch.float16  # Use half precision
).to(device)
torch.cuda.empty_cache()  # Clear CUDA cache

# Global variable to store extracted text
pdf_text = ""

# Extract text from PDF
def extract_text_from_pdf(file_path):
    text = ""
    with pdfplumber.open(file_path) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

# Summarization
def summarize_pdf(text):
    input_text = "summarize: " + text
    with torch.no_grad():  # Disable gradient tracking to save memory
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True).to(device)
        output = model.generate(
            input_ids, 
            max_length=150,
            min_length=30,
            num_beams=2,  # Reduced beam search
            early_stopping=True
        )
        summary = tokenizer.decode(output[0], skip_special_tokens=True)
        del input_ids, output  # Explicit cleanup
        torch.cuda.empty_cache()
    return summary

# Question Answering
def ask_question(text, question):
    input_text = f"question: {question} context: {text}"
    with torch.no_grad():  # Disable gradient tracking to save memory
        input_ids = tokenizer.encode(input_text, return_tensors="pt", max_length=512, truncation=True).to(device)
        output = model.generate(
            input_ids,
            max_length=100,
            num_beams=2,  # Reduced beam search
            early_stopping=True
        )
        answer = tokenizer.decode(output[0], skip_special_tokens=True)
        del input_ids, output  # Explicit cleanup
        torch.cuda.empty_cache()
    return answer

@app.route("/upload-pdf", methods=["POST"])
def upload_pdf():
    global pdf_text

    if "file" not in request.files:
        return jsonify({"error": "No file provided"}), 400

    file = request.files["file"]
    file_path = os.path.join("temp.pdf")
    file.save(file_path)

    pdf_text = extract_text_from_pdf(file_path)
    os.remove(file_path)

    return jsonify({"message": "PDF uploaded and processed successfully."})

@app.route("/ask-question", methods=["POST"])
def qa():
    global pdf_text

    if not pdf_text:
        return jsonify({"error": "No PDF uploaded yet."}), 400

    data = request.get_json()
    question = data.get("question")

    if not question:
        return jsonify({"error": "No question provided."}), 400

    answer = ask_question(pdf_text, question)
    return jsonify({"question": question, "answer": answer})

@app.route("/summary", methods=["GET"])
def summary():
    global pdf_text

    if not pdf_text:
        return jsonify({"error": "No PDF uploaded yet."}), 400

    summary = summarize_pdf(pdf_text)
    return jsonify({"summary": summary})

if __name__ == "__main__":
    app.run(debug=True)
