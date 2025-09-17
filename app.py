from search.cyberleninka import Cyberleninka
from AI.ai import AI


cbr = Cyberleninka()
ai = AI()
theme = input('Какова твоя тема исследования? ')

plan = ai.plan_article(theme)
print(plan)
print('План:', ', '.join(plan))

queries = ai.get_queries(theme) + plan
print('Ищу литературу:', ', '.join(queries))
contexts = []
for query in queries:
    for i in cbr.search(query):
        if i not in contexts:
            contexts.append(i)
print('Найдено:', len(contexts))

filtered = ai.filter_articles(theme, contexts)
print('Статей принято:', len(filtered))

words = ai.get_words_to_find_in_articles(theme)
print('Слов для поиска в статьях:', len(words))

contexts_dict = []
for i in filtered:
    try:
        gost = contexts[i].gost_record()
        cbr.get_content(contexts[i])
        contexts_dict.append({'gost_record': gost, 'contexts': contexts[i].find_contexts(words)})
    except Exception as e:
        print(f'Ошибка {e} при чтении статьи, пропускаем')

print('Статьи прочитаны, контексты собраны')
with open('res.md', 'w', encoding='utf-8') as file:
    conversation_id = None
    for fragment in plan:
        print('Написание:', fragment)
        conversation_id, content = ai.build_article_fragment(theme, fragment, contexts_dict, conversation_id)
        file.write(content)
        file.flush()

print('Статья готова! Смотри файл res.md')
