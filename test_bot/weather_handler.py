import aiohttp

from datetime import datetime

from aiogram.filters import Command, CommandObject
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram import Router, types

from utils import city_lat_lon, forecast

router = Router()


class OrderWeather(StatesGroup):
    waiting_for_forecast = State()


@router.message(Command("weather_time"))
async def weather_time(message: Message, command: CommandObject, state: FSMContext):
    if command.args is None:
        await message.answer('Ошибка: Не передали аргументы')
        return
    async with aiohttp.ClientSession() as session:
        lat, lon = await city_lat_lon(session=session, city=command.args)
        data = await forecast(session, lat, lon)

        data_dates = {datetime.fromtimestamp(item['dt']).isoformat(): item for item in data['list']}
        await state.set_data({'city': command.args, 'data_dates': data_dates})
        builder = ReplyKeyboardBuilder()
        for date_item in data_dates:
            builder.add(types.KeyboardButton(text=date_item))
        builder.adjust(4)
        await message.answer(
            f"Выберите время:",
            reply_markup=builder.as_markup(resize_keyboard=True),
        )
        await state.set_state(OrderWeather.waiting_for_forecast.state)


@router.message(OrderWeather.waiting_for_forecast)
async def weather_by_date(message: types.Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(
        f"Погода в городе {data['city']} в {message.text}:  "
        f"{round(data['data_dates'][message.text]['main']['temp'] - 273.15)} °C"
    )


@router.message(Command("weather"))
async def weather(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer('Error: Not found any arguments')
        return
    async with aiohttp.ClientSession() as session:
        lat, lon = await city_lat_lon(session=session, city=command.args)
        data = await forecast(session=session, lat=lat, lon=lon)
        dtime = datetime.now().timestamp()
        data_dates = {item['dt']: item for item in data['list']}
        data_dates = dict(sorted(data_dates.items()))
        resp = 0
        for date_key, date_value in data_dates.items():
            if date_key > dtime:
                resp = round(date_value['main']['temp']-273.15)
                break
        await message.answer(f'Погода в городе {command.args} на ближайшие часы: {resp} °C')


@router.message(Command("forecast"))
async def forecast_f(message: Message, command: CommandObject):
    if command.args is None:
        await message.answer('Error: Not found any arguments')
        return
    async with aiohttp.ClientSession() as session:
        lat, lon = await city_lat_lon(session=session, city=command.args)
        data = await forecast(session=session, lat=lat, lon=lon)
        forecast_res = {datetime.fromtimestamp(item['dt']): item['main']['temp'] for item in data['list']}
        needed_ids = {
            list(forecast_res.keys())[i].date():
                round(sum(list(forecast_res.values())[i:i + 8]) / 8 - 273.15)
            for i in range(0, len(forecast_res.keys()), 8)
        }
        response = as_list(
            as_marked_section(
                Bold(f"Привет, погода в городе {command.args} на 5 дней:"),
                *[f'{k}  {v} °C' for k, v in needed_ids.items()],
                marker="🌎",
            ),
        )
        await message.answer(**response.as_kwargs())

