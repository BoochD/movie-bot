**Movie-bot** - a bot for searching and watching movies, anime, TV series, and other video content.

**Main features:**
- `/start` command -- A welcome message offering assistance.
- `/help` command -- A message listing the bot's capabilities.
- `/history` command -- Your request history with the bot.
- `/stats` command -- Statistics of the movies recommended to you.

**(You need to change the commands in the code from Russian to your language)**
- A message like `Watch "movie title"` -- Sends the movie (if found) with its description, rating, and a link to free streaming (if available).
- A message like `Recommend something` -- Sends a movie with its description, rating, and a link to free streaming (if available) from the top 100 movies by IMDb and Kinopoisk ratings.

Also, in response to your sticker, it can send a funny sticker of its own :))

**Implementation**:

The bot is fully asynchronous and built using `aiogram3`. For handling web requests, `aiohttp` was used, and for working with databases - `aiosqlite`.

In the `app/database/database.py` module, the logic for working with the database is described. Specifically: adding a user, adding request information and statistics, as well as retrieving information and statistics.

In the `app/kp_connections.py` module, functions for retrieving movie information from the Kinopoisk database are described.

In the `scrapers.py` module, functions for scraping requests and obtaining websites with free movies are described. The search is implemented with priority across different search engines (*Google*, *Yandex*, *DuckDuckGo*).

In the `handlers.py` module, the logic for processing user messages is described.

**How does it work?**

Message processing is implemented using regular expressions that extract keywords like *watch, description, movie*, etc. 
The search is parsed using `BeautifulSoup`. 
This is done across multiple search engines; if the movie is not found in the first one, the bot moves to the next, and so on.

*<The bot was developed as part of a Python course at SHАD (School of Data Analysis) Yandex.>*
