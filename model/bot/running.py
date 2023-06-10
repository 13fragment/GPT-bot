from aiogram import Dispatcher, executor, types, Bot
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import StatesGroup,State
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
import json


with open('/home/max/PycharmProjects/GPT-bot/config/config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)
API_TOKEN = config["token"]
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())

with open('/home/max/PycharmProjects/GPT-bot/config/greeting.txt', encoding='utf-8') as greeting:
    welcome_msg = greeting.read()
commands_welcome = ['start', 'начать', 'Начать', 'НАЧАТЬ', 'Start']

keyboard = ReplyKeyboardMarkup(keyboard = [[KeyboardButton('Summarise It')]],
resize_keyboard=True,one_time_keyboard=True)

class Summary(StatesGroup):
    URL = State()

@dp.message_handler (commands=['start'])
async def greeting(message:types.Message):
    await message.answer(text=welcome_msg,parse_mode='HTML',reply_markup=keyboard)

@dp.message_handler(Text(equals='Summarise It', ignore_case=True), state=None)
async def greeting(message:types.Message):
    await Summary.URL.set()
    await message.reply('Введите ссылку на видео')

@dp.message_handler(state=Summary.URL)
async def a_login(message:types.Message,state: FSMContext):
    async with state.proxy() as data:
        data['URL'] = message.text
    await message.answer(data["URL"])

@dp.message_handler(commands=['help','помощь'])
async def help_command(message:types.Message):
    await message.reply('Связь с тех поддержкой: @mgo1ubev')


if __name__ == '__main__':
    executor.start_polling(dp,skip_updates='True')