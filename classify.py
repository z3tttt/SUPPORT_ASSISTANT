from sentence_transformers import SentenceTransformer, util
from datetime import datetime
import sqlite3

model = SentenceTransformer('all-MiniLM-L6-v2')

# Retrieve training data from the database
def get_training_data():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT message, label FROM messages")
    data = cursor.fetchall()
    conn.close()
    messages = [item[0] for item in data]
    labels = [item[1] for item in data]
    return messages, labels

def train_model(messages, labels):
    message_embeddings = model.encode(messages)
    label_embeddings = model.encode(labels)
    return message_embeddings, label_embeddings

def classify_message(new_message, message_embeddings, label_embeddings, labels, username):
    new_message_embedding = model.encode([new_message])
    similarities = util.pytorch_cos_sim(new_message_embedding, message_embeddings)
    best_match_index = similarities.argmax()
    predicted_label = labels[best_match_index]
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return predicted_label, timestamp