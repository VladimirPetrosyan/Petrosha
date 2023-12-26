import pandas as pd
from transformers import pipeline
from telegram.ext import Updater, Filters, CommandHandler, MessageHandler, CallbackContext, CallbackQueryHandler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
import random
import asyncio

# Загрузка предобученной модели GPT-2
generator = pipeline('text-generation', model='EleutherAI/gpt-neo-2.7B')

# Загрузка вашего датасета один раз при запуске
dataset = pd.read_csv('datasetForBot.csv')

# Функция генерации ответа с использованием GPT-2
async def generate_answer(question: str) -> str:
    loop = asyncio.get_running_loop()
    answer = await loop.run_in_executor(None, lambda: generator(question, max_length=50, num_return_sequences=1)[0]['generated_text'])
    return answer

# Функция обработки команды /start
def start(update: Update, context: CallbackContext) -> None:
    message = "Привет! Я Ероша, помогу создать вам игру. Не стесняйтесь, задавайте вопрос!"

    # Генерация inline-кнопок с рандомными вопросами
    random_questions = dataset.sample(n=4)['Question'].tolist()
    keyboard = [
        [InlineKeyboardButton(question, callback_data=f'question_{idx}')] for idx, question in enumerate(random_questions)
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Отправка сообщения с inline-кнопками
    update.message.reply_text(message, reply_markup=reply_markup)

# Функция обработки inline-кнопок
def button_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    question_id = int(query.data.split('_')[1])

    # Получение ответа на выбранный вопрос
    question = dataset.iloc[question_id]['Question']
    answer = find_answer(question)

    # Отправка ответа
    query.edit_message_text(text=f"Вопрос: {question}\nОтвет: {answer}")

# Функция обработки текстовых сообщений
async def handle_text(update: Update, context: CallbackContext) -> None:
    user_question = updzr(user_question)

    # Если ответ не найден, используйте GPT-2
    if not answer:
        answer = await generate_answer(user_question)

    update.message.reply_text(answer)

# Функция поиска ответа в датасете
def find_answer(question: str) -> str:
    # Поиск вопроса в датасете и возвращение соответствующего ответа
    result = dataset[dataset['Question'] == question]
    if not result.empty:
        return result.iloc[0]['Answer']
    return 'Извините, но на этот вопрос я пока не могу ответить'

def main() -> None:
    updater = Updater("6898851730:AAHO3r9mQymYciOT4LEqiet4XP1oqWFU_JM")
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CallbackQueryHandler(button_callback))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, lambda update, context: asyncio.run(handle_text(update, context))))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
