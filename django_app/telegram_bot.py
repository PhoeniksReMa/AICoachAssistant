# CoachAsistant/telegram_bot.py

import os
import sys
import django

# 1) Добавляем в PYTHONPATH корень проекта (/home/Dev/AICoachAssistant),
#    чтобы Python нашёл пакет AICoachAssistant и приложение CoachAsistant.
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# BASE_DIR стал /home/Dev/AICoachAssistant/django_app/CoachAsistant -> dirname -> /home/Dev/AICoachAssistant/django_app
PROJECT_ROOT = os.path.dirname(BASE_DIR)
# PROJECT_ROOT -> /home/Dev/AICoachAssistant
sys.path.append(PROJECT_ROOT)

# 2) Устанавливаем настройку DJANGO_SETTINGS_MODULE в 'config.settings'
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

# 3) Инициализируем Django
django.setup()

# Только после django.setup() можно импортировать модели и сервисы
from CoachAsistant.servises import (
    OpenAIAssistantService,
    OpenAIThreadService,
    TelegramUserService,
)
from CoachAsistant.models import OpenAIAssistant, OpenAIThread, TelegramUser

import asyncio
from asgiref.sync import sync_to_async
from dotenv import load_dotenv
import openai
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram import Router
import re
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Дальше идёт вся логика вашего бота
load_dotenv()
ASSISTANT_ID = os.getenv('ASSISTANT_ID')
VECTOR_STORE_ID = []
BOT_TOKEN = os.getenv('BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
openai.api_key = OPENAI_API_KEY

client = openai.OpenAI()
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()

assistant = OpenAIAssistant.objects.first()
if not assistant:
    assistant = OpenAIAssistantService().create_assistant()


@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    try:
        await sync_to_async(TelegramUser.objects.get)(chat_id=message.chat.id)
        await message.reply('Продолжим?')
    except:
        await message.reply('Здравствуйте! Меня зовут AI Coach, и сегодня мы вместе займёмся исследованием ваших жизненных ценностей. Это важный и интересный процесс, который поможет вам лучше понять, что для вас действительно ценно и значимо. Начнем?')


@dp.message(F.text, Command('clearall'))
async def my_handler(message: Message):
    # Синхронная функция clear_tread оборачивается
    thread = OpenAIThreadService()
    text = await sync_to_async(thread.clear_tread)(message.chat.id)
    await message.reply(f'{text}')


@dp.message()
async def handle_message(message: types.Message):
    user_text = message.text
    try:
        # Синхронный вызов get_thread_by_user оборачиваем
        user_service = TelegramUserService(chat_id=message.chat.id)
        thread_obj = await sync_to_async(user_service.get_thread_by_user)()
        thread_id = thread_obj.id if thread_obj else None

        if thread_id:
            thread_service = OpenAIThreadService(
                thread_id=thread_id,
                assistant_id=assistant.id
            )
            # Синхронный вызов add_message_tread оборачиваем
            await sync_to_async(thread_service.add_message_tread)(user_text)
        else:
            thread_service = OpenAIThreadService(assistant_id=assistant.id)
            await sync_to_async(thread_service.create_thread)(user_text, VECTOR_STORE_ID)
            # Синхронный вызов create_thread оборачиваем
            await sync_to_async(user_service.create_user)(assistant_id=thread_service.assistant_id, thread_id=thread_service.thread_id)

        # Синхронный вызов run_tread оборачиваем
        run = await sync_to_async(thread_service.run_tread)()


        if run.status == 'completed':
            # Синхронный вызов OpenAI API оборачиваем
            messages_resp = await sync_to_async(
                client.beta.threads.messages.list
            )(thread_id=thread_service.thread_id)

            answer = messages_resp.data[0].content[0].text.value
            clear_answer = re.sub(r'【\d+:\d+†[^】]+】', '', answer)

            button_hi = [[KeyboardButton(text='/clearall')]]
            greet_kb1 = ReplyKeyboardMarkup(
                keyboard=button_hi,
                resize_keyboard=True
            )

            await bot.send_message(
                chat_id=message.chat.id,
                text=clear_answer,
                parse_mode='Markdown',
                reply_markup=greet_kb1,
            )
        else:
            await message.answer(f'Статус запроса: {run.status}')

    except Exception as e:
        error_text = f'Произошла ошибка при обработке запроса: {e}'
        await message.answer(error_text)


async def main():
    print('Бот запущен...')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
