import telebot
import sqlite3
from telebot import types
from config import TOKEN, ADMIN_PASSWORD
import hashlib    
from classify import classify_message, get_training_data, train_model
from logic import save_request

bot = telebot.TeleBot(TOKEN)

messages, labels = get_training_data()
message_embeddings, label_embeddings = train_model(messages, labels)

# Database setup
def init_db():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT,
        department TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        username TEXT
    )''')
    conn.commit()
    conn.close()

# Fetch answer from FAQ database
def get_faq_answer(question):
    conn = sqlite3.connect('faq.db')
    cursor = conn.cursor()
    cursor.execute("SELECT answer FROM faq WHERE question=?", (question,))
    result = cursor.fetchone()
    conn.close()
    if result:
        return result[0]
    return None

# Menu buttons
def create_main_menu():
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    item1 = types.KeyboardButton("FAQ")
    item2 = types.KeyboardButton("Submit an Issue")
    item3 = types.KeyboardButton("Admin")
    markup.add(item1, item2, item3)
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Welcome to the technical support bot. How can I help you?", reply_markup=create_main_menu())

# FAQ Hash Map
faq_hash_map = {}

@bot.message_handler(func=lambda message: message.text.lower() == "faq")
def show_faq_list(message):
    conn = sqlite3.connect('faq.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM faq")
    questions = cursor.fetchall()
    conn.close()

    if not questions:
        bot.reply_to(message, "FAQ list is currently empty.")
        return

    markup = types.InlineKeyboardMarkup()
    for question in questions:
        q_text = question[0]
        q_hash = hashlib.md5(q_text.encode()).hexdigest()[:16]
        markup.add(types.InlineKeyboardButton(text=q_text, callback_data=f"faq_{q_hash}"))
        faq_hash_map[q_hash] = q_text

    bot.send_message(message.chat.id, "Select a question:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("faq_"))
def handle_faq_button(call):
    q_hash = call.data[4:]
    question = faq_hash_map.get(q_hash)
    if not question:
        bot.send_message(call.message.chat.id, "Invalid question.")
        return

    answer = get_faq_answer(question)
    if answer:
        bot.send_message(call.message.chat.id, f"*{question}*\n\n{answer}", parse_mode="Markdown")
    else:
        bot.send_message(call.message.chat.id, "Answer not found.")

    bot.send_message(call.message.chat.id, "Return to the main menu.", reply_markup=create_main_menu())

@bot.message_handler(func=lambda message: message.text.lower() == "submit an issue")
def handle_issue_submission(message):
    bot.reply_to(message, "Please describe your issue in detail.")
    bot.register_next_step_handler(message, process_issue)

def process_issue(message):
    user_message = message.text
    username = message.from_user.username or f"id_{message.from_user.id}"

    department, timestamp = classify_message(
        user_message,
        message_embeddings,
        label_embeddings,
        labels,
        username
    )

    save_request(message.from_user.id, user_message, department, username)

    bot.reply_to(message, f"Your issue has been submitted to the {department} department.")
    bot.send_message(message.chat.id, "Return to the main menu.", reply_markup=create_main_menu())

@bot.message_handler(func=lambda message: message.text.lower() == "admin")
def prompt_admin_password(message):
    bot.reply_to(message, "Please enter the admin password:")
    bot.register_next_step_handler(message, verify_admin_password)

def verify_admin_password(message):
    if message.text == ADMIN_PASSWORD:
        show_admin_menu(message)
    else:
        bot.reply_to(message, "Incorrect password.", reply_markup=create_main_menu())

def show_admin_menu(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("Add Training Example", "Add Label", "Add FAQ", "Back to Menu")
    bot.send_message(message.chat.id, "Admin Menu:", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Add Training Example")
def admin_add_training_example(message):
    bot.reply_to(message, "Send the message text followed by '::' and the label.\nExample: I can't log in::Support")
    bot.register_next_step_handler(message, save_training_example)

def save_training_example(message):
    try:
        message_text, label = message.text.split("::")
        conn = sqlite3.connect('database.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO messages (message, label) VALUES (?, ?)", (message_text.strip(), label.strip()))
        conn.commit()
        conn.close()
        bot.reply_to(message, "Training example added.")
    except:
        bot.reply_to(message, "Invalid format. Use: message::label")

@bot.message_handler(func=lambda message: message.text == "Add Label")
def admin_add_label(message):
    bot.reply_to(message, "Send the new label name:")
    bot.register_next_step_handler(message, save_label)

def save_label(message):
    label = message.text.strip()
    # Labels are learned dynamically, no DB action needed unless storing predefined ones
    bot.reply_to(message, f"Label '{label}' noted. You can now add examples with it.")

@bot.message_handler(func=lambda message: message.text == "Add FAQ")
def admin_add_faq(message):
    bot.reply_to(message, "Send the question followed by '::' and the answer.")
    bot.register_next_step_handler(message, save_faq)

def save_faq(message):
    try:
        question, answer = message.text.split("::")
        conn = sqlite3.connect('faq.db')
        cursor = conn.cursor()
        cursor.execute("INSERT INTO faq (question, answer) VALUES (?, ?)", (question.strip(), answer.strip()))
        conn.commit()
        conn.close()
        bot.reply_to(message, "FAQ added.")
    except:
        bot.reply_to(message, "Invalid format. Use: question::answer")

@bot.message_handler(func=lambda message: message.text == "Back to Menu")
def return_to_main(message):
    bot.send_message(message.chat.id, "Returned to main menu.", reply_markup=create_main_menu())

if __name__ == "__main__":
    init_db()
    bot.polling(none_stop=True)
