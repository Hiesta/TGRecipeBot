# import aiohttp

from config import ow_token

WEATHER_TOKEN = ow_token


async def city_lat_lon(session, city):
    async with session.get(url=f'http://api.openweathermap.org/geo/1.0/direct?'
                               f'q={city}&limit=1&appid={WEATHER_TOKEN}') as resp:
        data = await resp.json()
        lat = data[0]['lat']
        lon = data[0]['lon']
        return lat, lon


async def forecast(session, lat, lon):
    async with session.get(url=f'api.openweathermap.org/data/2.5/forecast?'
                               f'lat={lat}&lon={lon}&appid={WEATHER_TOKEN}') as resp:
        data = await resp.json()
        return data
