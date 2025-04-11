from flask import Flask, request, jsonify
from sentence_transformers import SentenceTransformer, util
from threading import Lock
import torch
import os
import re
import logging
from nltk.corpus import wordnet
import nltk

# Ensure NLTK resources are available
nltk.download('wordnet')

app = Flask(__name__)

# Setup logging
logging.basicConfig(level=logging.INFO)

# Thread safety for model access
lock = Lock()

# Load model once
model_name = os.getenv("MODEL_NAME", "all-MiniLM-L6-v2")
model = SentenceTransformer(model_name)

def load_qa_pairs(file_path="content.txt"):
    """Load Q&A pairs from a file."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"'{file_path}' not found. Please place it in the project directory.")

    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()

    # Extract Q&A pairs using regex
    qa_pattern = re.compile(r"Q:\s*(.*?)\nA:\s*(.*?)(?=\nQ:|\Z)", re.DOTALL)
    qa_pairs = qa_pattern.findall(content)
    return qa_pairs

def expand_query(query):
    """Expand the query with synonyms to improve matching."""
    words = query.split()
    expanded_words = set(words)
    for word in words:
        for synset in wordnet.synsets(word):
            for lemma in synset.lemmas():
                expanded_words.add(lemma.name())
    expanded_query = ' '.join(expanded_words)
    return expanded_query

# Precompute embeddings
try:
    file_path = os.getenv("QA_FILE_PATH", "content.txt")
    content_sections = load_qa_pairs(file_path)
    questions = [q.strip() for q, a in content_sections]
    answers = [a.strip() for q, a in content_sections]
    content_embeddings = model.encode(questions, convert_to_tensor=True, normalize_embeddings=True)
    logging.info("Q&A pairs and embeddings loaded successfully.")
except Exception as e:
    logging.error("Initialization Error: %s", str(e))
    exit(1)

@app.route("/query", methods=["POST"])
def query():
    """Handle incoming queries and return the most relevant response."""
    data = request.get_json()
    user_input = data.get("query", "").strip()

    if not user_input:
        return jsonify({"response": "Please enter a valid query.", "follow_up_needed": False})

    # Expand the user query
    expanded_user_input = expand_query(user_input)

    with lock:
        query_embedding = model.encode(expanded_user_input, convert_to_tensor=True, normalize_embeddings=True)
        similarities = util.cos_sim(query_embedding, content_embeddings)[0]

    top_idx = int(similarities.argmax())
    top_score = float(similarities[top_idx])

    # Debug log
    logging.debug("User Query: %s", user_input)
    logging.debug("Expanded Query: %s", expanded_user_input)
    logging.debug("Top Score: %s", top_score)
    logging.debug("Matched Answer Snippet: %s", answers[top_idx][:300])

    # Lower the threshold to 0.2 for testing
    if top_score < 0.2:
        return jsonify({
            "response": "I'm sorry, I don't have a relevant answer right now. Please try rephrasing your question or check our help resources.",
            "follow_up_needed": False,
            "suggestions": ["Try using different keywords.", "Check our FAQ section."]
        })

    response = summarize_response(answers[top_idx])
    return jsonify({"response": response, "follow_up_needed": True})

def summarize_response(text, max_length=300):
    """Summarize the response text to a given maximum length."""
    return text[:max_length].strip() + ("..." if len(text) > max_length else "")

if __name__ == '__main__':
    logging.info("Starting AI Assistant API...")
    app.run(host="0.0.0.0", port=5000, debug=True)
