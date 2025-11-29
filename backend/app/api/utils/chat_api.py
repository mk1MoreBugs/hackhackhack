import json
from uuid import uuid4

import requests

from app.core.config import settings


def user_query_summarizer(query: str) -> str:
    prompt = (f"Запрос пользователя: {query}. Выдай краткий пересказ того, что хочет пользователь. "
              f"Пиши конкретные работы, которые хочет сделать пользователь, но без упоминания пользователя"
              f"(сделать что-либо, перенести что-либо)"
              f" Объем - 5-15 слов")
    request_data = {
        "model": "GigaChat",
        "messages": [
            {
                "role": "system",
                "content": "Ты - пользователь, который обращается Бюро технической инвентаризации (БТИ)"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
    }
    request_data_json = json.dumps(request_data)
    headers = {
        "Authorization": get_bearer_token(),
    }

    response = requests.post(
        url="https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        verify=False,
        headers=headers,
        data=request_data_json,
    )
    response_body = response.json()

    if "choices" not in response_body:
        print(response_body)

    return response_body["choices"][0]["message"]["content"]


def create_final_answer(query: str, docs: list[dict]) -> str:
    prompt = (f"Запрос пользователя: {query}."
              f"Что говорят по этому поводу нормативные документы: {docs}."
              f"Опираясь на эти документы, определи, можно ли делать то, что хочет делать пользователь"
              f"Ответ аргументируй нормативными актами, которые приведены в выше."
              f"Пиши от лица сотрудника БТИ"
              f"Длина ответа - 200-400 символов")
    request_data = {
        "model": "GigaChat-2-Pro",
        "messages": [
            {
                "role": "system",
                "content": "Ты - опытный сотрудник Бюро технической инвентаризации (БТИ)"
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "stream": False,
    }
    request_data_json = json.dumps(request_data)
    headers = {
        "Authorization": get_bearer_token(),
    }

    response = requests.post(
        url="https://gigachat.devices.sberbank.ru/api/v1/chat/completions",
        verify=False,
        headers=headers,
        data=request_data_json,
    )
    response_body = response.json()

    if "choices" not in response_body:
        print(response_body)

    return response_body["choices"][0]["message"]["content"]

def get_bearer_token() -> str:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid4()),
        "Authorization": f"Basic {settings.CHAT_TOKEN}",
    }
    request_data = {
        "scope": "GIGACHAT_API_PERS",
    }

    response = requests.post(
        url="https://ngw.devices.sberbank.ru:9443/api/v2/oauth",
        verify=False,
        headers=headers,
        data=request_data,
    )
    response_body = response.json()

    access_token = response_body["access_token"]
    return f"Bearer {access_token}"