# from flask import Flask, request, jsonify
# from sentence_transformers import SentenceTransformer, util
# import os

# app = Flask(__name__)

# # Step 1: Load Content
# def load_content():
#     if not os.path.exists("content.txt"):
#         print("Error: 'content.txt' file not found. Please create it in the same directory as app.py.")
#         exit(1)

#     with open("content.txt", "r", encoding="utf-8") as file:
#         content = file.read()

#     # Split content into sections using headers (#)
#     sections = content.split("\n# ")
#     sections = [sections[0]] + ["# " + section for section in sections[1:]]

#     # Debugging: Print each section to verify splitting
#     for i, section in enumerate(sections):
#         print(f"Section {i + 1}:\n{section[:100]}...\n")

#     return sections

# # Initialize the model and content embeddings
# model = SentenceTransformer("all-MiniLM-L6-v2")
# content_sections = load_content()
# content_embeddings = model.encode(content_sections)

# @app.route('/query', methods=['POST'])
# def query():
#     user_input = request.json.get("query")
#     if not user_input:
#         return jsonify({"response": "Please provide a valid query.", "follow_up_needed": False})

#     # Step 2: Relevance Checking
#     query_embedding = model.encode(user_input)
#     similarities = util.cos_sim(query_embedding, content_embeddings)[0]

#     # Debugging: Log similarity scores and matched sections
#     print(f"User Query: {user_input}")
#     print("Similarity Scores:", similarities)
#     most_relevant_idx = similarities.argmax().item()
#     print(f"Most Relevant Section (Index {most_relevant_idx}): {content_sections[most_relevant_idx][:200]}...")

#     # Adjust the threshold for relevance
#     if similarities[most_relevant_idx] < 0.4:  # Lowered threshold
#         return jsonify({"response": "Sorry, I currently have limited Resource,While I get Upgraded feel free to check www.zoho.com", "follow_up_needed": False})

#     # Step 3: Summarization (optional)
#     summary = summarize_response(content_sections[most_relevant_idx])

#     # Debugging: Log the final response
#     print(f"Final Response: {summary}")

#     return jsonify({"response": summary, "follow_up_needed": True})

# def summarize_response(text):
#     max_length = 300  # Adjust the maximum length as needed
#     if len(text) > max_length:
#         return text[:max_length] + "..."
#     return text

# if __name__ == '__main__':
#     # Ensure content.txt exists
#     if not os.path.exists("content.txt"):
#         print("Error: 'content.txt' file not found. Please create it in the same directory as app.py.")
#         exit(1)

#     # Start the Flask server
#     print("Starting Flask server...")
#     app.run(debug=True)

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

# Step 1: Load Content
def load_content():
    # Check if content.txt exists
    if not os.path.exists("content.txt"):
        print("Error: 'content.txt' file not found. Please create it in the same directory as app.py.")
        exit(1)

    # Read and split content into sections
    with open("content.txt", "r", encoding="utf-8") as file:
        content = file.read()

    # Split content into sections using headers (#)
    sections = content.split("\n# ")
    sections = [sections[0]] + ["# " + section.strip() for section in sections[1:]]

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
    # Step 2: Validate Input
    user_input = request.json.get("query")
    if not user_input or len(user_input.strip()) < 3:
        return jsonify({
            "response": "Please provide a valid query (minimum 3 characters).",
            "follow_up_needed": False
        })

    # Step 3: Encode Query and Calculate Similarity
    query_embedding = model.encode(user_input)
    similarities = util.cos_sim(query_embedding, content_embeddings)[0]

    with lock:
        query_embedding = model.encode(expanded_user_input, convert_to_tensor=True, normalize_embeddings=True)
        similarities = util.cos_sim(query_embedding, content_embeddings)[0]

    # Step 4: Check Relevance Threshold
    if similarities[most_relevant_idx] < 0.4:  # Adjust threshold as needed
        return jsonify({
            "response": "Sorry, I currently have limited resources. While I get upgraded, feel free to check www.zoho.com.",
            "follow_up_needed": False
        })

    # Step 5: Summarize Response
    response = summarize_response(content_sections[most_relevant_idx])

    # Debugging: Log the final response
    print(f"Final Response: {response}")

    return jsonify({
        "response": response,
        "follow_up_needed": True
    })

def summarize_response(text):
    max_length = 300  # Adjust the maximum length as needed
    if len(text) > max_length:
        return text[:max_length].rsplit(' ', 1)[0] + "..."  # Avoid cutting words in half
    return text

if __name__ == '__main__':
    logging.info("Starting AI Assistant API...")
    app.run(host="0.0.0.0", port=5000, debug=True)
