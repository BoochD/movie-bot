import aiohttp
from bs4 import BeautifulSoup


async def google_scrape(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = f"https://www.google.com/search?q={query.replace(' ', '+')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                results = []
                for g in soup.find_all("div", class_="tF2Cxc"):
                    title = g.find("h3").text if g.find("h3") else "Без названия"
                    link = g.find("a")["href"] if g.find("a") else None
                    if link:
                        results.append({"title": title, "url": link})
                return results
            else:
                return []
            
async def yandex_scrape(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = f"https://yandex.ru/search/?text={query.replace(' ', '+')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                results = []
                for g in soup.find_all("li", class_="serp-item"):
                    title_element = g.find("h2")
                    link_element = g.find("a", href=True)
                    if title_element and link_element:
                        title = title_element.text.strip()
                        link = link_element["href"]
                        results.append({"title": title, "url": link})
                return results
            else:
                return []

async def duckduckgo_scrape(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                results = []
                for g in soup.find_all("a", class_="result__a"):
                    title = g.text.strip()
                    link = g["href"]
                    results.append({"title": title, "url": link})
                return results
            else:
                return []
            
async def bing_scrape(query):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
    }
    url = f"https://www.bing.com/search?q={query.replace(' ', '+')}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                html = await response.text()
                soup = BeautifulSoup(html, "html.parser")
                results = []
                for g in soup.find_all("li", class_="b_algo"):
                    title_element = g.find("h2")
                    link_element = g.find("a", href=True)
                    if title_element and link_element:
                        title = title_element.text.strip()
                        link = link_element["href"]
                        results.append({"title": title, "url": link})
                return results
            else:
                return []
            
async def search_with_priority(query, engine_name):
    if engine_name.lower() =='google':
        engine_function = google_scrape
    elif engine_name.lower() =='yandex':
        engine_function = yandex_scrape
    elif engine_name.lower() =='bing':
        engine_function = bing_scrape
    elif engine_name.lower() =='duckduckgo':
        engine_function = duckduckgo_scrape
    try:
        results = await engine_function(query)
        if results:
            return results
    except Exception as e:
        print(f"{engine_name} не сработал: {e}")
    return []

async def scrap_search(query):
    tokens = ['rutube.ru', 'vk.com/video', 'lordfilm', 'lordserial', 'jut.su', 'animego',
            'ok.ru', 'youtube.com', 'yandex.ru/video']
    engines = ['Google', 'Yandex', 'DuckDuckGo']
    result_link = None
    backup_link = None
    mute = []
    for engine in engines:
        check_res = await search_with_priority(query, engine)
        if check_res:
            for res in check_res[:10]:
                for token in tokens:
                    if token in res['url']:
                        if result_link is None:
                            result_link = res['url']
                            # mute.append(token)
                        # elif backup_link is None:
                        #     backup_link = res['url']
                        if result_link is not None:
                            break    
                if result_link is not None:
                    break
        if result_link is not None:
                break
    return result_link, backup_link