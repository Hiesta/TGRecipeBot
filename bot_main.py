import asyncio
import logging
import sys

from googletrans import Translator
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.client.default import DefaultBotProperties
from aiogram.filters import CommandStart
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram import Bot, Dispatcher, types
from aiogram import F

from recipes_handler import router

dp = Dispatcher()
dp.include_router(router)
bot_token = '7006631554:AAH3IK9ve4i0mErwMz6sU0Eh4ExBLXQszQo'


kb = [[types.KeyboardButton(text="Команды"),
       types.KeyboardButton(text="Описание"),]]
keyboard = types.ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True)


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer(f'Привет {message.chat.full_name}', reply_markup=keyboard)


@dp.message(F.text.lower() == "команды")
async def commands(message: Message) -> None:
    text = as_list(
        as_marked_section(
            Bold('Команды:'),
            "/category_search_random <кол-во> - случайные блюда по выбранной категории",
        )
    )
    await message.answer(**text.as_kwargs())


@dp.message(F.text.lower() == "описание")
async def description(message: Message) -> None:
    await message.answer('Этот бот предоставляет информацию о рецептах')


async def main() -> None:
    bot = Bot(token=bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)
#FIXME: translator = Translator()
#FIXME: recipe = translator.translate('text', dest='ru')
#FIXME: print(recipe.text)


if __name__ == '__main__':
    asyncio.run(main())
