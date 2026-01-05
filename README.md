# Currency MCP Agent

Бизнес-ориентированный AI-агент для конвертации валют и отслеживания курсов через MCP-сервер.

## Описание

Агент автоматизирует рутинные финансовые операции для бизнес-пользователей (бухгалтерия, закупки, продажи):
- Получение актуальных курсов валют
- Конвертация сумм между валютами
- Отслеживание доступных валют

Решение использует публичное API exchangerate-api.com и соответствует протоколу MCP (Model Context Protocol). Готово к интеграции в каталог Evolution AI Agents.

## Архитектура

- **MCP-сервер** (FastMCP): предоставляет 3 инструмента для работы с валютами
- **AI-агент** (LangChain): обрабатывает запросы на естественном языке
- **Evolution Foundation Models**: используется для интерпретации запросов

## Требования

- Python 3.9+
- API ключ от [exchangerate-api.com](https://www.exchangerate-api.com/) (бесплатный тариф)
- Доступ к Evolution Foundation Models (для работы агента)

## Установка и настройка

1. Клонируйте репозиторий:
```bash
git clone https://github.com/yourusername/currency-mcp-agent.git
cd currency-mcp-agent 
```
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Настройте переменные окружения:
```bash
cp .env.example .env
# Отредактируйте .env, добавив ваш API ключ
```
4. Получите API ключи:
- Зарегистрируйтесь на exchangerate-api.com для бесплатного ключа
- Получите доступ к Evolution Foundation Models (при необходимости)

# Использование

## Запуск MCP-сервера
```bash
mcp_server/server.py
```
Сервер запустится на stdio (для MCP-протокола) и HTTP (для тестирования).

## Примеры запросов через агента
```bash
from agent.agent import CurrencyAgent
agent = CurrencyAgent()
#Конвертация валют
result = agent.query("Сколько будет 100 долларов в рублях?")
print(result)
#Получение курса
result = agent.query("Какой курс евро к доллару?")
print(result)
#Список валют
result = agent.query("Покажи доступные валюты")
print(result)
```

## Прямые вызовы MCP-сервера
```bash
import requests
import json
````

# Конвертация валют
```bash
response = requests.post(
    "http://localhost:8000/tools/convert_currency",
    json={
        "amount": 100,
        "from_currency": "USD",
        "to_currency": "RUB"
    }
)
print(json.dumps(response.json(), indent=2))

#Получение курса
response = requests.post(
    "http://localhost:8000/tools/get_exchange_rate",
    json={
        "base_currency": "EUR",
        "target_currency": "USD"
    }
)
print(json.dumps(response.json(), indent=2))
```

## Структура проекта
```
currency-mcp-agent/
├── README.md                    #Эта документация
├── requirements.txt             #Зависимости Python
├── .env.example                #Шаблон переменных окружения
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── mcp_server/
│   ├── __init__.py
│   └── server.py              #MCP-сервер с 3 инструментами
├── agent/
│   ├── __init__.py
│   └── agent.py               #AI-агент на LangChain
├── config/
│   └── tools.json             #Конфигурация инструментов MCP
└── tests/
    └── test_mcp_server.py     #Тесты MCP-сервера
```
## Инструменты MCP-сервера
1. get_exchange_rate - получение текущего курса между двумя валютами
- Параметры: base_currency, target_currency
- Возвращает: курс, временную метку, обратный курс
2. convert_currency - конвертация суммы из одной валюты в другую
- Параметры: amount, from_currency, to_currency
- Возвращает: конвертированную сумму, курс, отформатированный результат
3. list_available_currencies - список доступных валют
- Параметры: нет
- Возвращает: список валют с кодами, названиями и курсами к USD

## Бизнес-ценность
- Экономия времени: автоматизация рутинных запросов курсов валют
- Точность: использование актуальных данных из проверенного источника
- Интеграция: возможность встраивания в бизнес-процессы компаний
- Масштабируемость: готовность к работе в мультиагентных системах

## Критерии соответствия заданию
- Бизнес-ориентированность: решает реальную бизнес-проблему
- Использование MCP: реализован MCP-сервер с 3 инструментами
- Обработка ошибок: валидация входных данных, обработка сетевых ошибок
- Готовность к интеграции: совместимость с Evolution AI Agents
- Документирование: полная документация и инструкции
- Тестируемость: включены тесты для MCP-сервера

## Развертывание на Cloud.ru
Проект готов к развертыванию на платформе Cloud.ru Evolution AI Agents:

1. Убедитесь, что у вас есть доступ к платформе Cloud.ru

2. Настройте переменные окружения в панели управления

3. Загрузите проект через интерфейс Evolution AI Agents

4. Протестируйте работу агента через веб-интерфейс

# Тестирование
Запустите тесты для проверки функциональности:
```bash
-m pytest tests/test_mcp_server.py -v
```
## Лицензия
MIT License
