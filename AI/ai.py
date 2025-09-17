from mistralai import Mistral, ChatCompletionResponse
from .api_key import KEY
from typing import List, Dict
from context_item import ContextItem
from json import loads


client = Mistral(KEY)
MODEL = 'ministral-8b-2410'
ARGS = {
    "temperature": 0.7,
    "max_tokens": 128000,
    "top_p": 1
}
TOKEN_PRICE = {
    'prompt_tokens': 0.1,
    'completion_tokens': 0.1
}

class AI:
    used_tokens = {
        'prompt_tokens': 0,
        'completion_tokens': 0
    }
    

    def get_queries(self, theme: str) -> List[str]:
        """
        Получает поисковые запросы из 3-6 слов, что дадут наиболее релевантные ответы в системе поиска научной литературы, что будет полезна пользователю выполняющему исследование по указанной им теме.
        """

        chat_response = client.chat.complete(
            model = MODEL,
            messages = [
                {
                    "role": "system",
                    "content": """Твоя задача - подобрать поисковые запросы из 3-6 слов, что дадут наиболее релевантные ответы в системе поиска научной литературы, что будет полезна пользователю выполняющему исследование по указанной им теме.
                    Ответ представь в формате json {"result": ["тема1", "тема2"]}. Запросы представляй на русском языке, не искажая имена терминов""",
                },
                {
                    "role": "user",
                    "content": theme,
                }
            ],
            response_format = {
                "type": "json_object",
            }
        )
        self.__calculate_usage(chat_response)
        return loads(chat_response.choices[0].message.content)['result']

    def filter_articles(self, theme: str, context: List[ContextItem]) -> List[int]:
        """
        Фильтрует статьи из списка, которые будут полезны учёному выполняющему исследование темы. Возвращает список индексов статей.
        """

        prompt_context = '\n'.join([f'{i}. {repr(v)}' for i, v in enumerate(context)])
        
        chat_response = client.chat.complete(
            model = MODEL,
            messages = [
                {
                    "role": "system",
                    "content": """Твоя задача - указать научные статьи из списка представленных пользователем, которые будет полезны учёному выполняющему исследование темы.
                    Ответ представь в формате json {"result": [индекс1, индекс2]}, в виде списка чисел, показывающий индексы полезных публикаций""",
                },
                {
                    "role": "user",
                    "content": f"""Тема: {theme}
                    Статьи: {prompt_context}""",
                }
            ],
            response_format = {
                "type": "json_object",
            }
        )
        self.__calculate_usage(chat_response)
        return loads(chat_response.choices[0].message.content)['result']

    def get_words_to_find_in_articles(self, theme: str) -> List[str]:
        """
        Получает слова для поиска контекстов в научных статьях, которые имеет смысл процитировать в научной статье по теме заданной пользователем.
        """

        chat_response = client.chat.complete(
            model = MODEL,
            messages = [
                {
                    "role": "system",
                    "content": """Твоя задача - формировать списки слов для поиска контекстов в научных статьях, которые имеет смысл процитировать в научной статье по теме заданной пользователем.
                                Ответ представь в формате json {"result": ["слово1", "слово2"]} указывай строго по одному слову в строке""",
                },
                {
                    "role": "user",
                    "content": f"""Тема: {theme}""",
                }
            ],
            response_format = {
                "type": "json_object",
            }
        )
        self.__calculate_usage(chat_response)
        return loads(chat_response.choices[0].message.content)['result']

    def build_article_fragment(self, theme: str, fragment_name: str, contexts_dict: List[Dict[str, str | List[str]]], conversation_id: str = None) -> str:
        """
        Строит фрагмент статьи по теме и списку статей. Возвращает строку с статьёй.
        """

    
        chat_response = None
        if conversation_id == None:
            chat_response = client.beta.conversations.start(
                model = MODEL,
                inputs = [
                    {
                        "role": "assistant",
                        "content": f"""Твоя задача - написать фрагмент статьи, готовой к публикации в респектабельном научном журнале по теме предоставленной пользователем, обязательно процитировав статьи указанные пользователем. Они будут предоставлены в формате json.
                        Верно укажи библиографические записи. Цитируй статьи сразу после использования их содержимого вот так: [Запись по гост, например Киселев Алексей Алексеевич. Сравнение технологий WebSocket и Socket.IO // Инновационные аспекты развития науки и техники. 2021.]. Не обрамляй статью лишним контентом
                        Тема: {theme}
                        Статьи: {contexts_dict}""",
                    },
                    {
                        "role": "user",
                        "content": f"""Фрагмент: {fragment_name}""",
                    }
                ]
            )
        else:
            chat_response = client.beta.conversations.append(
                conversation_id=conversation_id,
                inputs = [
                    {
                        "role": "user",
                        "content": f"""Фрагмент: {fragment_name}""",
                    }
                ]
            )
        self.__calculate_usage(chat_response)
        return (chat_response.conversation_id, chat_response.outputs[0].content)

    def plan_article(self, theme: str) -> List[str]:
        """
        Планирует статью по теме и списку статей. Возвращает список с планом статьи.
        """

        chat_response = client.chat.complete(
            model = MODEL,
            messages = [
                {
                    "role": "system",
                    "content": """Твоя задача - написать план объемной статьи, готовой к публикации в респектабельном научном журнале по теме предоставленной пользователем. Сделай всё как требуется в большинстве научных журналов.
                    Ответ представь в формате json {"result": ["раздел1", "раздел2"]}""",
                },
                {
                    "role": "user",
                    "content": f"""Тема: {theme}""",
                }
            ],
            response_format = {
                "type": "json_object",
            }
        )
        self.__calculate_usage(chat_response)
        return loads(chat_response.choices[0].message.content)['result']

    def __calculate_usage(self, responce: ChatCompletionResponse):
        self.used_tokens['prompt_tokens'] += responce.usage.prompt_tokens
        self.used_tokens['completion_tokens'] += responce.usage.completion_tokens
        print('Вход:', self.used_tokens['prompt_tokens'], f'${TOKEN_PRICE["prompt_tokens"] / 1000000 * self.used_tokens['prompt_tokens']}', sep='\t')
        print('Выход:', self.used_tokens['completion_tokens'], f'${TOKEN_PRICE["completion_tokens"] / 1000000 * self.used_tokens['completion_tokens']}', sep='\t')