from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext
import os
import time

# === CONFIGURATION ===
BOT_TOKEN = '7672661539:AAGncUPEjQbAsoM9mUo0BHiR7RmvUwri4Kw'  # Replace with your actual bot token
ROOT_FOLDER = 'E:/Surendhar_Documents'  # Root folder to access
PASSWORD = 'Suren2301#'  # Set your password here
SESSION_TIMEOUT = 100  # Timeout duration in seconds (5 minutes)

# === /start COMMAND ===
def start(update: Update, context: CallbackContext):
    update.message.reply_text("🔒 Please enter the password to access the bot:")

# === PASSWORD CHECK COMMAND ===
def check_password(update: Update, context: CallbackContext):
    if 'password_attempt' not in context.user_data:
        context.user_data['password_attempt'] = 0

    if 'last_interaction' in context.user_data:
        # Check if session is expired
        elapsed_time = time.time() - context.user_data['last_interaction']
        if elapsed_time > SESSION_TIMEOUT:
            context.user_data['authenticated'] = False
            context.user_data.pop('last_interaction', None)
            context.user_data.pop('current_path', None)
            context.user_data.pop('password_attempt', None)
            update.message.reply_text("⏰ Your session has expired. Please log in again by typing the password.")
            return

    # Check if password is correct
    if update.message.text == PASSWORD:
        context.user_data['password_attempt'] = 0  # Reset the password attempts
        context.user_data['authenticated'] = True
        context.user_data['current_path'] = ROOT_FOLDER
        context.user_data['last_interaction'] = time.time()  # Track the last interaction time
        update.message.reply_text("✅ Password correct! You can now access the files.\nUse /listfiles to view files.")
    else:
        context.user_data['password_attempt'] += 1
        if context.user_data['password_attempt'] < 3:
            update.message.reply_text(f"❌ Incorrect password. Attempt {context.user_data['password_attempt']}/3.")
        else:
            update.message.reply_text("🚫 Too many incorrect attempts. Please restart the bot.")
            context.user_data['password_attempt'] = 0

# === /listfiles COMMAND ===
def list_files(update: Update, context: CallbackContext):
    if context.user_data.get('authenticated', False):
        # Check session timeout before listing files
        if 'last_interaction' in context.user_data:
            elapsed_time = time.time() - context.user_data['last_interaction']
            if elapsed_time > SESSION_TIMEOUT:
                context.user_data['authenticated'] = False
                context.user_data.pop('last_interaction', None)
                context.user_data.pop('current_path', None)
                update.message.reply_text("⏰ Your session has expired. Please log in again by typing the password.")
                return
        path = context.user_data.get('current_path', ROOT_FOLDER)
        send_folder_contents(update, context, path)
    else:
        update.message.reply_text("🔒 You need to log in first. Please enter the password using /start.")

# === SEND FOLDER CONTENTS ===
def send_folder_contents(update, context, folder_path):
    try:
        entries = sorted(os.listdir(folder_path))
        buttons = []

        for item in entries:
            full_path = os.path.join(folder_path, item)
            if os.path.isdir(full_path):
                buttons.append([InlineKeyboardButton(f"📁 {item}", callback_data=f"open|{item}")])
            elif os.path.isfile(full_path):
                buttons.append([InlineKeyboardButton(f"📄 {item}", callback_data=f"file|{item}")])

        # Add back button if not at root
        if os.path.abspath(folder_path) != os.path.abspath(ROOT_FOLDER):
            buttons.append([InlineKeyboardButton("🔙 Back", callback_data="back")])

        reply_markup = InlineKeyboardMarkup(buttons)

        if update.callback_query:
            update.callback_query.edit_message_text("📂 Contents of folder:", reply_markup=reply_markup)
        else:
            update.message.reply_text("📂 Contents of folder:", reply_markup=reply_markup)

        # Save current path
        context.user_data['current_path'] = folder_path
        context.user_data['last_interaction'] = time.time()  # Update last interaction time

    except Exception as e:
        update.message.reply_text(f"❌ Error: {str(e)}")

# === BUTTON HANDLER ===
def button_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    query.answer()
    action, *args = query.data.split("|")
    current_path = context.user_data.get('current_path', ROOT_FOLDER)

    if action == "open":
        folder_name = args[0]
        new_path = os.path.join(current_path, folder_name)
        if os.path.isdir(new_path):
            send_folder_contents(update, context, new_path)
        else:
            query.message.reply_text("❌ Folder not found.")

    elif action == "file":
        filename = args[0]
        file_path = os.path.join(current_path, filename)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                query.message.reply_document(f)
        else:
            query.message.reply_text("❌ File not found.")

    elif action == "back":
        parent_path = os.path.dirname(current_path)
        if os.path.abspath(parent_path).startswith(os.path.abspath(ROOT_FOLDER)):
            send_folder_contents(update, context, parent_path)
        else:
            query.message.reply_text("🚫 You're at the root folder.")

# === MAIN SETUP ===
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, check_password))
    dp.add_handler(CommandHandler("listfiles", list_files))
    dp.add_handler(CallbackQueryHandler(button_handler))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
