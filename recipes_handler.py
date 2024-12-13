#TODO: async def category_search_random
#TODO: async def random_dish
#TODO: async def random_dish

import aiohttp

from datetime import datetime
from random import choices as random_choice
from googletrans import Translator

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types

router = Router()
meals = 'https://www.themealdb.com/api/json/v1/1/list.php?c=list'
translator = Translator()

class InfoSaves(StatesGroup):
    data_backup = State()


@router.message(Command("category_search_random"))
async def category_search_random(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer('Вы забыли передать желаемое количество блюд')
        return
    async with aiohttp.ClientSession() as session:
        async with session.get(url=meals) as resp:
            data = await resp.json()
            await state.set_data({'count': command.args})
            builder = ReplyKeyboardBuilder()
            for meal in data['meals']:
                builder.add(types.KeyboardButton(text=meal['strCategory']))
            builder.adjust(4)
            await message.answer(f'Выберите блюдо:',
                                 reply_markup=builder.as_markup(resize_keyboard=True))
            await state.set_state(InfoSaves.data_backup.state)


@router.message(InfoSaves.data_backup)
async def choices(message: Message, state: FSMContext):
    count = (await state.get_data())['count']
    meal = message.text
    async with aiohttp.ClientSession() as session:
        async with session.get(
            url=f'https://www.themealdb.com/api/json/v1/1/filter.php?c={message.text}'
        ) as resp:
            data = await resp.json()
            if len(data['meals']) < int(count):
                random_dishes = data['meals']
            else:
                random_dishes = random_choice(data['meals'], k=int(count))
            text = 'Как Вам такие варианты: '
            for dish in random_dishes:
                text += f'{translator.translate(dish['strMeal'], dest='ru').text}, '
            button = [[types.KeyboardButton(text='Покажи рецепты')]]
            show_recipe = types.ReplyKeyboardMarkup(keyboard=button)

            await message.answer(text[:-2], reply_markup=show_recipe)



