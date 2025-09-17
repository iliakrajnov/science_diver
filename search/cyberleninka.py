import requests
import json
import io
from PyPDF2 import PdfReader
from typing import List, Optional
import re
from context_item import ContextItem


class Cyberleninka:
    def __init__(self):
        pass
    
    def search(self, query: str, start_pos: int = 0) -> List[ContextItem]:
        """Ищет научные тексты по заданной теме

        Args:
            query (str): Запрос

        Returns:
            List[ContextItem]: Список классов ContextItem
        """
        url = "https://cyberleninka.ru/api/search"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:143.0) Gecko/20100101 Firefox/143.0",
            "Accept": "*/*",
            "Accept-Language": "ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type": "application/json",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "User-Agent": "<K> diver AI"
        }
        payload = {
            "mode": "articles",
            "q": query,
            "size": 5,
            "from": start_pos
        }

        response = requests.post(url, headers=headers, data=json.dumps(payload), cookies={}, allow_redirects=True)
        current_articles = response.json().get('articles', [])

        res = []
        for article in current_articles:
            current_article = ContextItem()
            current_article.from_dict(article)
            current_article.link = 'https://cyberleninka.ru/' + current_article.link + '/pdf'
            res.append(current_article)
        return res

    def get_content(self, article: ContextItem) -> str:
        """Получает содержимое статьи и записывает его в объект статьи

        Args:
            article (ContextItem): объект статьи
        """
        
        resp = requests.get(article.link)
        reader = PdfReader(io.BytesIO(resp.content))
        res ="\n\n".join(page.extract_text() or "" for page in reader.pages)
        article.content = res
