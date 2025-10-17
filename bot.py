import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = "llama-3.1-8b-instruct"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "🤖 <b>Groq AI Vision Bot</b>\n\n"
        "📝 Пиши вопросы\n"
        "🖼️ Отправляй фото - распознаю!\n"
        "💬 <i>Llama 3.1 Vision</i>"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко и точно."},
                {"role": "user", "content": user_message}
            ],
            model=GROQ_MODEL_NAME,
            temperature=0.7,
            max_tokens=1024,
        )
        await update.message.reply_text(response.choices[0].message.content.strip())
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    photo = update.message.photo[-1]
    try:
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = await file.download_as_bytearray()
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Опиши изображение подробно: что на фото, цвета, эмоции, текст. На русском!"},
                {"role": "user", "content": [
                    {"type": "text", "text": "Опиши это изображение максимально подробно!"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{photo_bytes.hex()}"}}
                ]}
            ],
            model="llama-3.1-8b-instruct",
            temperature=0.3,
            max_tokens=1500,
        )
        await update.message.reply_text(f"🖼️ <b>Анализ фото:</b>\n\n{response.choices[0].message.content.strip()}", parse_mode='HTML')
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка анализа фото: {e}")

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    print("🚀 Vision Bot запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()