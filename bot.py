import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
import os
import base64

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_TEXT_MODEL = "llama-3.1-8b-instant"  # Текст: Production, стабильная
GROQ_VISION_MODEL = "meta-llama/llama-4-scout-17b-16e-instruct"  # Фото: Preview Vision

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_html(
        "🤖 <b>Groq AI Vision Bot 2025</b>\n\n"
        "📝 Пиши вопросы (Llama 3.1 8B Instant)\n"
        "🖼️ Отправляй фото - распознаю! (Llama 4 Scout Vision)\n"
        "💬 Обновлено: 17.10.2025 | Исправлено изображение"
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_message = update.message.text
    user = update.effective_user
    logger.info(f"Текст от {user.id}: {user_message}")

    try:
        response = client.chat.completions.create(
            messages=[
                {"role": "system", "content": "Ты полезный ассистент. Отвечай кратко и точно на русском."},
                {"role": "user", "content": user_message}
            ],
            model=GROQ_TEXT_MODEL,
            temperature=0.7,
            max_tokens=1024,
        )
        await update.message.reply_text(response.choices[0].message.content.strip())
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка текста: {str(e)}")
        logger.error(f"Text Error: {e}")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    photo = update.message.photo[-1]
    logger.info(f"Фото от {user.id}")

    try:
        # Скачиваем фото как байты
        file = await context.bot.get_file(photo.file_id)
        photo_bytes = bytes(await file.download_as_bytearray())  # Преобразуем в bytes
        
        # Проверяем валидность данных (не пусто и не повреждено)
        if not photo_bytes or len(photo_bytes) == 0:
            raise ValueError("Пустое или поврежденное изображение")
        
        # Корректное кодирование в base64
        photo_base64 = base64.b64encode(photo_bytes).decode('utf-8')
        
        # Vision запрос
        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system", 
                    "content": "Ты эксперт по изображениям. Опиши подробно: что на фото, цвета, эмоции, текст. На русском!"
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Опиши это изображение максимально подробно!"},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{photo_base64}"
                            }
                        }
                    ]
                }
            ],
            model=GROQ_VISION_MODEL,
            temperature=0.3,
            max_tokens=1500,
        )
        
        ai_response = response.choices[0].message.content.strip()
        await update.message.reply_text(f"🖼️ <b>Анализ фото (Llama 4 Scout Vision):</b>\n\n{ai_response}", parse_mode='HTML')
        
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка фото: {str(e)}")
        logger.error(f"Vision Error: {e}")

def main() -> None:
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    
    print("🚀 Groq Vision Bot 2025 запущен! Исправлена обработка изображений.")
    application.run_polling()

if __name__ == '__main__':
    main()
