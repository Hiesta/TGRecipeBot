import asyncio

import logging
import sys

from aiogram.client.default import DefaultBotProperties
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import F
from aiogram.utils.formatting import Bold, as_list, as_marked_section

from config import bot_token
from weather_handler import router

dp = Dispatcher()
dp.include_router(router=router)
TOKEN = bot_token

kb = [
    [
        types.KeyboardButton(text="Команды"),
        types.KeyboardButton(text="Описание"),
    ],
]
keyboard = types.ReplyKeyboardMarkup(
    keyboard=kb,
    resize_keyboard=True
)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f'Привет {message.chat.full_name}', reply_markup=keyboard)


@dp.message(F.text.lower() == "команды")
async def commands(message: Message) -> None:
    response = as_list(
        as_marked_section(
            Bold('Команды:'),
            "/weather - weather by city",
            "/forecast - forecast 1 - 5 days",
            "/weather_time - weather by date/time",
            marker="✅ ",
        ),
    )
    await message.answer(**response.as_kwargs())


@dp.message(F.text.lower() == "описание")
async def description(message: Message) -> None:
    await message.answer('Этот бот предоставляет информацию о погоде')


async def main() -> None:
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())