import aiohttp
from config import API_TOKEN
import random


async def get_info(name: str):
    url = f'https://api.kinopoisk.dev/v1.4/movie/search'
    headers = {
        'X-API-KEY': API_TOKEN
    }
    params = {
        'query': name,
        'page': 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(response.status)
            if response.status == 200:
                data = await response.json() 
                docs = data['docs'][0]
                if docs:
                    description = docs['description']
                    name = docs['name']
                    poster = docs['poster']['url']
                    movie_type = docs['type']
                    rating = docs['rating']
                    return name, description, poster, movie_type, rating
    return None, None, None, None, None

async def get_random_info():
    url = 'https://api.kinopoisk.dev/v1.4/movie'
    headers = {
        'X-API-KEY': API_TOKEN
    }
    params = {
        'limit': 100,
        'page': 1,
        'sortField': 'rating.imdb',
        'sortType': -1,
        'type': ['movie'],
        'rating.kp': '8.0-10.0'
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params) as response:
            print(f"HTTP Status: {response.status}")
            if response.status == 200:
                data = await response.json()
                docs = data.get('docs', [])
                top_movies = [
                    {
                        'name': movie.get('name', 'Название неизвестно'),
                        'rating': movie.get('rating', {}),
                        'poster': movie.get('poster', {}).get('url', 'Постер отсутствует'),
                        'type': movie.get('type', 'Тип отсутствует'),
                        'description': movie.get('description', 'Описание отсутствует')
                    }
                    for movie in docs
                ]
                while True:
                    idx = random.randint(0, len(top_movies) - 1)
                    name = top_movies[idx]['name']
                    if not name:
                        continue
                    rating = top_movies[idx]['rating']
                    if rating['imdb'] < 8 or rating['kp'] < 8:
                        continue
                    description = top_movies[idx]['description']
                    if not description:
                        continue 
                    poster = top_movies[idx]['poster']
                    if not poster:
                        continue
                    movie_type =  top_movies[idx]['type']
                    if not movie_type:
                        continue
                    
                    break
                return name, description, poster, movie_type, rating
            else:
                return None, None, None, None, None