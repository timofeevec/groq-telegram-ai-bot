import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests # Импортируем библиотеку для выполнения HTTP-запросов
import json # Импортируем для работы с JSON

# --- ВАЖНО: ЗАПОЛНИТЕ ЭТИ ПЕРЕМЕННЫЕ ---
TELEGRAM_BOT_TOKEN = "8243442723:AAEoUun6mdVh2czsoIvUVpH1vk9dBZhPeTE" # Токен вашего Telegram-бота
HF_API_TOKEN = "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" # API-токен от Hugging Face (можно оставить пустым, но не рекомендуется)
HF_MODEL_NAME = "microsoft/DialoGPT-medium" # Или другая подходящая модель, например, "google/gemma-2-9b-it"
HF_API_URL = f"https://api-inference.huggingface.co/models/{HF_MODEL_NAME}"
# -------------------------------------

# Включаем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Глобальный словарь для хранения истории чатов (для DialoGPT)
# В реальных приложениях используйте базу данных
chat_history = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение при команде /start."""
    user_id = update.effective_user.id
    chat_history[user_id] = [] # Инициализируем историю для нового пользователя
    await update.message.reply_html(
        rf"Привет! Я ИИ-ассистент, работающий на модели {HF_MODEL_NAME}. Задай мне любой вопрос."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Отправляет сообщение пользователя в Hugging Face Inference API и возвращает ответ."""
    user_id = update.effective_user.id
    user_message = update.message.text
    user = update.effective_user

    # Инициализируем историю, если пользователя нет
    if user_id not in chat_history:
        chat_history[user_id] = []

    # Логируем запрос (опционально)
    logger.info(f"Получен запрос от {user.id} ({user.first_name}): {user_message}")

    # --- Специфика DialoGPT ---
    # DialoGPT работает с историей диалога. Добавим сообщение пользователя.
    chat_history[user_id].append(user_message)
    # Объединяем историю в одну строку, разделяя специальным токеном (часто просто '\n')
    full_prompt = " <SEP> ".join(chat_history[user_id]) + " <SEP>"

    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}", # Используем токен, если он есть
        "Content-Type": "application/json"
    }

    payload = {
        "inputs": full_prompt,
        "parameters": {
            "max_new_tokens": 150, # Максимальное количество новых токенов в ответе
            "temperature": 0.7,    # Контролирует креативность
            "top_k": 50,
            "top_p": 0.95,
            "repetition_penalty": 1.2, # Пытаемся избежать повторений
            "return_full_text": False # Возвращаем только сгенерированный текст
        }
    }

    try:
        # Выполняем POST-запрос к Inference API
        response = requests.post(HF_API_URL, headers=headers, json=payload)
        response.raise_for_status() # Проверяем на HTTP ошибки

        # Извлекаем JSON-ответ
        result = response.json()
        # print(result) # Для отладки

        # Извлекаем текст ответа из ответа API (структура может отличаться в зависимости от модели)
        # Для DialoGPT и большинства генеративных моделей:
        if isinstance(result, list) and len(result) > 0:
            generated_text = result[0].get('generated_text', 'Извините, не удалось сгенерировать ответ.')
        else:
            generated_text = 'Извините, не удалось сгенерировать ответ.'

        # --- Обновляем историю для DialoGPT ---
        # Добавляем ответ модели к истории
        chat_history[user_id].append(generated_text)

        # Отправляем ответ пользователю
        await update.message.reply_text(generated_text)

        # Логируем ответ (опционально)
        logger.info(f"Отправлен ответ пользователю {user.id} ({user.first_name}): {generated_text[:100]}...") # Отправляем первые 100 символов

    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 429: # Слишком много запросов
            await update.message.reply_text("Слишком много запросов к ИИ-сервису. Повторите позже.")
            logger.error(f"HF API Rate Limit (429): {e}")
        else:
            await update.message.reply_text(f"Ошибка HTTP при запросе к ИИ-сервису: {e.response.status_code} - {e.response.text}")
            logger.error(f"HF API HTTP Error: {e}")
    except requests.exceptions.RequestException as e:
        await update.message.reply_text("Ошибка при запросе к ИИ-сервису. Повторите позже.")
        logger.error(f"HF API Request Error: {e}")
    except Exception as e:
        await update.message.reply_text("Произошла ошибка при обработке запроса.")
        logger.error(f"Непредвиденная ошибка: {e}")

def main() -> None:
    """Запускает бота."""
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Hugging Face AI-Бот запущен. Нажмите Ctrl+C для остановки.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
