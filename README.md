## BACKEND PROJECT Для прохождения в летнию школу Yandex:
## Технологии

* Python (FastAPI)
* PostgreSQL

# Реализовано:
    Базовые задачи:
            /imports
            /delete/{id}
            /nodes/{id}
    Дополнительные задачи:
            /sales

# Комментари:
    main.py - запуск проекта
    app - папка со всем проектом
        db - папка для реализации database и соединения
        queries - папка с запросами на database
        routers - папка с рутами 
        api.py - реализация проекта FastAPI c логгером
        exceptions.py - класс ошибок
        limiter.py - лимитер для ограничения кол-во запросов на руты
        models.py - модели Pydantic
        utils.py - аггрегация Record c database