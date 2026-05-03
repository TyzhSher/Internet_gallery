**Internet Gallery**

Internet Gallery — это backend-сервис для управления коллекцией художественных работ с системой персонализированных рекомендаций. Пользователи могут создавать аккаунты, добавлять картины в общую галерею, формировать списки любимых художников и жанров, а также получать умные рекомендации на основе своих предпочтений.

**Требования**
```
    Python 3.10+
    pip или poetry
```

**Установка и запуск**

Установка зависимостей:

```bash
pip install -r requirements.txt # install 3-rd party modules
uvicorn app.main:app --reload # run app
```
Запуск тестов:
```bash
pytest tests/test_service.py -v # Run tests without coverage
pytest --cov=app --cov-report term-missing --cov-report html # Run tests with coverage
```

**Автор**

Иванова Полина Олеговна, студент 1 курса магситратуры ФОПФ
