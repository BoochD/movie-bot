import re
import random
import math
from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from .database.database import add_user, save_request, get_user_requests, update_movie_count, get_user_movies
from .scrapers import scrap_search
from .kp_connection import get_info, get_random_info


router = Router()

WATCH_REG =  r'^(?:хочу\s+)?(?:посмотреть|смотреть|увидеть|почитать|описание)' \
            r'(?:\s*(мультике|фильме|сериале|мультфильме|мультика|фильма|сериала|мультфильма|мультик|фильм|аниме|сериал|мультфильм))?\s*"(.*)"$' \
            r'|^(?:хочу\s+)?(?:посмотреть|смотреть|увидеть|почитать|описание)' \
            r'(?:\s*(мультике|фильме|сериале|мультфильме|мультика|фильма|сериала|мультфильма|мультик|фильм|аниме|сериал|мультфильм))?\s*(.*)$'


@router.message(lambda message: message.sticker is not None)
async def handle_sticker(message: Message):
    stickers = [
        r'CAACAgIAAxkBAAENWqBnZAbVnBNrTRFvv5EQTwkAAZRsGFAAAlMBAAJ7TioQH1Qf9OSBQwk2BA',
        r'CAACAgIAAxkBAAENWqJnZAtoMRnQR3yz0DIxoqcMusltAwACp1wAAiK4kUn0lo1x9VwCvDYE',
        r'CAACAgIAAxkBAAENWpxnZAbP1b5hwk9kiNOOfjUScT5ivwAC7FMAAoB0kEuxRkD8V9DelTYE',
        r'CAACAgIAAxkBAAENWqRnZAuwiYNVg0uqPqnXLd5CmcoL2gACaAADZaIDLEOhZW-dvcUxNgQ'
    ]
    idx = random.randint(0, len(stickers) - 1)
    await message.answer_sticker(stickers[idx])

@router.message(CommandStart())
async def send_start(message: Message):
    await message.answer(
        "Здравствуйте!🤝\n"
        "Меня зовут 'cinema_bot' - бот для поиска и просмотра фильмов, аниме, сериалов и прочего видеоконтента.\n"
        "Подробнее о моих возможностях в /help\n\n\n"
        )

@router.message(Command('help'))
async def send_help(message: Message):
    await message.answer(
        "Вот мои возможности:\n"
        "✅ Посмотреть что-то конкретное - напишите:\nСмотреть \"название фильма\"\n\n"
        "✅ Предложить рандомный фильм - напишите:\nПосоветуй что-нибудь\n\n"
        "✅ Посмотреть историю запросов - введите команду:\n/history\n\n"
        "✅ Посмотреть статистику запросов - введите команду:\n/stats\n\n"
        "😎 Для крутых - напишите просто: Смотреть\n\n\n"
        "❗️ Если вдруг фильм появился с описанием, но без ссылки, попробуйте написать запрос еще раз."
        )

@router.message(Command('history'))
async def send_history(message: Message):
    history = await get_user_requests(message.from_user.id)
    text = "📋История последних 20-и запросов боту:\n\n"
    for i, item in enumerate(history):
        query = f"Запрос №{i + 1}: <{item[0]}>\n"
        time = f"Время запроса: {item[1]}\n\n"
        text += query
        text += time
    await message.answer(text)

@router.message(Command('stats'))
async def send_stats(message: Message):
    stats = await get_user_movies(message.from_user.id)
    text = "📋Статистика по предложенным фильмам:\n\n"
    for i, item in enumerate(stats):
        query = f"🔘{item[0]} — {item[1]}\n\n"
        text += query
    await message.answer(text)

async def format_and_answer(message, title, content_type, description,
                            rating, result_link, backup_link, poster):
    emoji_list = ['🤮','☹️','😕','🙂','😀']
    idx_1 = math.ceil(rating['kp'] / 2) - 1 if math.ceil(rating['kp'] / 2) - 1 >= 0 else 0
    idx_2 = math.ceil(rating['imdb'] / 2) - 1 if math.ceil(rating['imdb'] / 2) - 1 >= 0 else 0
    emoji_1 = emoji_list[idx_1]
    emoji_2 = emoji_list[idx_2]
    caption = (
        f"Описание {content_type.lower()} \"{title}\":\n\n{description}\n\n"
        f"🍿Рейтинг Кинопоиск: {rating['kp']}{emoji_1}\n🎞Рейтинг IMDB: {rating['imdb']}{emoji_2}"
    )
    if result_link is not None:
        caption += f"\n\n🎬Вот ссылка на просмотр: {result_link}"
    if backup_link is not None:
        caption += f"\n😁А вот запасная ссылка, ну так, на всякий: {backup_link}"
    if len(caption) > 1024:
        idx = 1024
        curr = caption[:idx]
        await message.answer_photo(poster, caption=curr)
        while len(curr) >= 1024: 
            curr = caption[idx:idx+1024]
            idx += 1024
            await message.answer(curr)
        await message.answer("Приносим свои извенения.\nСообщение разделилось, так как telegram не позволяет делать "
                            "их длиннее 1024 символов ☹️")
    else:
        await message.answer_photo(poster, caption=caption)

@router.message(lambda message: message.text.lower() == "посоветуй что-нибудь" or
                message.text.lower() == "посоветуй что нибудь")
async def send_random(message: Message):

    title, description, poster, movie_type, rating = await get_random_info()
    await add_user(message.from_user.id, message.from_user.username)
    await save_request(message.from_user.id, message.text)
    await update_movie_count(message.from_user.id, title)
    if movie_type in ['movie']:
            content_type = 'фильма'
    query = f'смотреть {content_type} {title} бесплатно онлайн'
    result_link, backup_link = await scrap_search(query)
    print(title)
    if title == 'Магия лунного света':
        result_link = 'https://lordfilms-sumerki.ru/magiya-lunnogo-sveta/'
            
    # print(f'{result_link=}')
    # print(f'{backup_link=}')
    await format_and_answer(message, title, content_type, description,
                             rating, result_link, backup_link, poster)
    
@router.message(lambda message: re.search(WATCH_REG, message.text, re.IGNORECASE))
async def watch(message: Message):
    await add_user(message.from_user.id, message.from_user.username)
    await save_request(message.from_user.id, message.text)
    found = re.search(
        WATCH_REG,
        message.text, 
        re.IGNORECASE
    )
    if found:
        if found.group(2):
            film_name = found.group(2).strip().capitalize()
        else:
            film_name = found.group(4).strip().capitalize()

        if not film_name:
           rayan_gosling = ['Драйв', 'Бегущий по лезвию','Славные парни','Человек на луне',
                            'Фанатик','Ла-ла ленд','Место под соснами','Ларс и настоящая девушка']
           idx_gosl = random.randint(0, len(rayan_gosling) - 1)
           title, description, poster, movie_type, rating = await get_info(rayan_gosling[idx_gosl])
           await message.answer('Вы не написали, что хотите посмотреть, поэтому вот Вам фильм с Райаном Гослингом😎')
        else: 
            title, description, poster, movie_type, rating = await get_info(film_name)

        await update_movie_count(message.from_user.id, title)

        if movie_type == 'anime':
            content_type = 'аниме'
        elif movie_type in ['movie', 'short', 'documentary']:
            content_type = 'фильма'
        elif movie_type in ['tv-series', 'miniseries']:
            content_type = 'сериала'
        elif movie_type in ['cartoon']:
            content_type = 'мультфильма'
        else:
            content_type = 'видео-контента'
       
        query = f'смотреть {content_type} {title} бесплатно онлайн'
        result_link, backup_link = await scrap_search(query)
        print(title)

        # print(f'{result_link=}')
        # print(f'{backup_link=}')
        await format_and_answer(message, title, content_type, description,
                                rating, result_link, backup_link, poster)
                  
    else:
        await message.answer(
            "Я не понял запрос 🤔.\n"
            "Попробуйте снова, придерживаясь шаблона:\n"
            "Смотреть \"Название фильма\""
            )

@router.message()
async def send_sorry(message: Message):
    await message.answer(
        "К сожалению, я пока не понимаю такие команды☹️.\n"
        "Чтобы узнать, что я умею, напишите /help"
    )
