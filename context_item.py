from typing import Dict, List, Optional
from pydantic import BaseModel
from json import dumps, loads
import re

class ContextItem(BaseModel):
    name: str = ""
    annotation: str = ""
    content: str = ""
    authors: List[str] = []
    journal: str = ""
    year: str = ""
    link: str = ""

    def __init__(self, name: str = "", annotation: str = "", content: str = "", authors: List[str] = [], journal: str = "", year: str = "", link: str = ""):
        super().__init__(name=name, annotation=annotation, content=content, authors=authors, journal=journal, year=year, link=link)

    def gost_record(self):
        """
        Формирует библиографическую запись по ГОСТ для статьи в журнале с полными именами авторов.
        Возвращает строку с библиографической записью.
        Пример вывода:
        Киселев Алексей Алексеевич. Сравнение технологий WebSocket и Socket.IO // Инновационные аспекты развития науки и техники. 2021. (URL: /article/...)
        """
        
        def clean_html(text: Optional[str]) -> str:
            """Удаляет простые HTML-теги и приводит пробелы в порядок."""
            if not text:
                return ""
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'\s+', ' ', text).strip()
            return text
            
        title = clean_html(self.name)
        authors = ', '.join(self.authors)
        journal = clean_html(self.journal)
        year = str(self.year).strip()

        def normalize_title(t: str) -> str:
            if not t:
                return ""
            letters = re.findall(r'[A-Za-zА-Яа-яЁё]', t)
            if letters and sum(1 for ch in letters if ch.isupper()) / len(letters) > 0.6:
                t = t.lower()
                t = t[0].upper() + t[1:]
            return t

        title = normalize_title(title)

        parts = []
        if authors:
            parts.append(f"{authors}.")
        if title:
            parts.append(f"{title}")
        if journal:
            parts.append(f"// {journal}.")
        if year:
            parts.append(f" {year}.")
        record = " ".join(p.strip() for p in parts if p).replace(" .", ".")
        record = re.sub(r'\s+', ' ', record).strip()
        return record
    
    def from_json(self, json: str):
        self.from_dict(loads(json))
    
    def from_dict(self, json: Dict):
        self.name = json.get('name', "")
        self.annotation = json.get('annotation', "")
        self.content = json.get('content', "")
        self.authors = json.get('authors', [])
        self.journal = json.get('journal', "")
        self.year = json.get('year', "")
        self.link = json.get('link', "")

    def __repr__(self):
        return f'{self.name} ({self.annotation})'

    def __str__(self):
        return dumps(self.__dict__)
    
    def find_contexts(self, words: List[str]):
        sentences = self.content.split('.')
        return list(filter(lambda i: any(map(lambda j: j in i, words)), sentences))