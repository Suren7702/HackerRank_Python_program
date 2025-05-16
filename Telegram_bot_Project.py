import os
import requests
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

BOT_TOKEN = '7654814282:AAGbZVFe4Nm5uNKcck1n3610S67H2PPkTyI'

def start(update, context):
    update.message.reply_text("Send me a Terabox video link and I'll try to download it for you!")

def extract_video_url(terabox_link):
    api_url = "https://teraboxdown.com/api/download"
    response = requests.post(api_url, json={"url": terabox_link})
    
    if response.status_code == 200:
        data = response.json()
        if 'download_url' in data:
            return data['download_url']
    return None

def handle_link(update, context):
    link = update.message.text.strip()

    if "terabox" not in link:
        update.message.reply_text("Please send a valid Terabox link.")
        return

    update.message.reply_text("Processing your Terabox link...")

    video_url = extract_video_url(link)
    if not video_url:
        update.message.reply_text("Failed to extract the video link. Try another link or later.")
        return

    try:
        filename = "video.mp4"
        with requests.get(video_url, stream=True) as r:
            r.raise_for_status()
            with open(filename, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)

        if os.path.getsize(filename) > 2 * 1024 * 1024 * 1024:
            update.message.reply_text("Video is too large for Telegram (max 2 GB).")
        else:
            with open(filename, 'rb') as video:
                update.message.reply_video(video=video)

        os.remove(filename)
    except Exception as e:
        update.message.reply_text(f"Error downloading video: {e}")

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_link))

    print("Bot is running...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
