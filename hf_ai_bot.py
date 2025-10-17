import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# --- Переменные из .env ---
TTELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL_NAME = "llama-3.1-8b-instant"

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1",
)

# --- ВАЖНО: ЗАПОЛНИТЕ ЭТИ ПЕРЕМЕННЫЕ ---
TELEGRAM_BOT_TOKEN = "8243442723:AAEoUun6mdVh2czsoIvUVpH1vk9dBZhPeTE" # Токен вашего Telegram-бота
GROQ_API_KEY = "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"             # API-ключ от Groq
GROQ_MODEL_NAME = "llama-3.1-8b-instant"             # Или другая доступная модель, например "gemma2-9b-it", "llama-3.1-8b-instant"
# -------------------------------------

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализируем OpenAI SDK с базовым URL Groq
client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1", # Указываем URL API Groq
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение при команде /start."""
    user = update.effective_user
    await update.message.reply_html(
        rf"Привет! Я ИИ-ассистент, работающий на модели {GROQ_MODEL_NAME} через Groq. Задай мне любой вопрос."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение пользователя в Groq и возвращает ответ."""
    user_message = update.message.text
    user = update.effective_user

    # Логируем запрос (опционально)
    logger.info(f"Получен запрос от {user.id} ({user.first_name}): {user_message}")

    try:
        # Выполняем запрос к API Groq через OpenAI SDK
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "Ты полезный и вежливый ассистент в чате Telegram. Отвечай на вопросы пользователя. Будь кратким, но информативным.",
                },
                {
                    "role": "user",
                    "content": user_message,
                }
            ],
            model=GROQ_MODEL_NAME,
            temperature=0.7,
            max_tokens=1024, # Groq может поддерживать разные лимиты
        )

        # Извлекаем текст ответа
        ai_response = chat_completion.choices[0].message.content.strip()

        # Отправляем ответ пользователю
        await update.message.reply_text(ai_response)

        # Логируем ответ (опционально)
        logger.info(f"Отправлен ответ пользователю {user.id} ({user.first_name}): {ai_response[:100]}...") # Первые 100 символов

    except Exception as e:
        error_msg = str(e)
        await update.message.reply_text(f"Произошла ошибка при запросе к ИИ-сервису: {error_msg}")
        logger.error(f"Groq API Error: {e}")

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Groq AI-Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
