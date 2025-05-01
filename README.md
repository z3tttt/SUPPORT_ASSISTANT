Support Bot 🤖
A technical support bot that classifies user issues, responds with pre-existing FAQ answers, and allows administrators to add new training data, labels, and FAQs securely.

Features ✨
Message Classification 🏷️: Uses AI to classify user issues into different departments (e.g., Sales, Billing).

FAQ System 📚: Users can retrieve answers to frequently asked questions.

Admin Access 🔐: Admin users can add new training examples, labels, and FAQ entries by providing a password.

Data Storage 💾: Stores user requests, FAQ entries, and classification data in SQLite databases.

Requirements 📋
Python 3.x

telebot library (for interacting with Telegram API)

sentence-transformers library (for message classification)

sqlite3 (for database management)

Install Required Libraries 📦
To install the necessary libraries, run the following command in your terminal:

pip install -r requirements.txt

Configuration ⚙️
config.py
The config.py file contains sensitive information like your Telegram Bot Token and admin password. Below is an example of what the file should look like:

TOKEN = "your_telegram_bot_token_here"
ADMIN_PASSWORD = "your_secure_admin_password_here"

Replace the following:

"your_telegram_bot_token_here" with your Telegram Bot token.

"your_secure_admin_password_here" with the password that only admin users should know.

Database Setup 🗃️
The bot uses two SQLite databases:

database.db: Stores user requests with message, department, timestamp, and username.

faq.db: Stores frequently asked questions (FAQ) with corresponding answers.

To initialize these databases, ensure the following functions are executed in your bot's code:

init_db()  # Initializes the 'requests' table in 'database.db'
init_faq_db()  # Initializes the 'faq' table in 'faq.db'

Bot Workflow 🛠️
1. Start the Bot 🎉
The bot welcomes users and provides them with two main options:

FAQ ❓: Display a list of frequently asked questions.

Submit an Issue 📝: Let users submit a support request.

2. FAQ 📚
Users can select questions from the list and view corresponding answers.

If an answer is not found, the bot will inform the user.

3. Submit an Issue 📝
Users can describe their issues, which the bot will classify into appropriate departments (e.g., Sales, Billing) using AI.

The issue is then saved in the database, and the user is informed that the issue has been submitted.

4. Admin Access 🔑
Admin users can access an admin menu to add new FAQs, training examples, and labels.

Admin access is protected by a password defined in config.py.

Admins can add new FAQ entries directly from the menu.

Admin Menu 👑
The admin menu allows the following actions:

Add New Training Examples ➕: Admins can add new examples to train the AI model.

Add New Labels 🏷️: Admins can create new labels for classifying user issues.

Add New FAQ Entries ❓💬: Admins can add new FAQ questions and their answers.

To enter the admin section, the bot will prompt for the admin password. If the password matches the one in config.py, the admin menu will be displayed.

Running the Bot 🚀
To run the bot, simply execute the Python script:

python bot.py

Make sure your config.py file is properly set up and your databases are initialized before starting the bot.