# Groq Telegram AI Bot

Это бот для Telegram, использующий Groq AI для обработки текстов и изображений (Vision). Поддерживает команды и анализ фото!

## Функции
- Отвечает на текстовые вопросы
- Анализирует загруженные фото
- Работает 24/7 после деплоя

## Установка
1. Склонируйте репозиторий: `git clone https://github.com/timofeevec/groq-telegram-ai-bot.git`
2. Установите зависимости: `pip install -r requirements.txt`
3. Создайте `.env` с токенами: TELEGRAM_BOT_TOKEN=ваш_токен
                               GROQ_API_KEY=ваш_ключ
4. Запустите: `python bot.py`

## Технологии
- Python
- Telegram API
- Groq AI (llama-3.1-8b-instruct)

## Автор
[timofeevec](https://github.com/timofeevec)
