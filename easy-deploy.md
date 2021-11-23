# Легкое и быстрое развертывание ToDo-бота

> :warning: Используйте эту инструкцию лишь для того, чтобы познакомиться с ботом и без
> особых усилий развернуть его.
> 
>Данная инструкция не предназначена для реальной и полноценной работы. Это упрощенный
> вариант полной инструкции 
> [README.md](https://github.com/ExpressApp/todo-bot/blob/master/README.md).


1. Воспользуйтесь инструкцией [Руководстве 
   администратора](https://express.ms/admin_guide.pdf) `-> Эксплуатация корпоративного 
   сервера -> Управление контактами -> Чат-боты`, чтобы создать бота в админке 
   eXpress. 
   Получите `secret_key` и `bot_id` кликнув на имя созданного бота. 
   Получите `cts_host` в строке браузера, когда вы в админке. 
   

2. Создайте директорию для бота на сервере и добавьте туда этот проект:

```bash
mkdir /opt/express/bots/todo-bot
git clone https://github.com/ExpressApp/todo-bot.git /opt/express/bots/todo-bot
cd /opt/express/bots/todo-bot
```

3. Создайте файл `docker-compose.yml` со следующим содержимым и 
   подставьте в `BOT_CREDENTIALS` реальные значения:

```yaml
version: "3.8"

services:
  todo-bot:
    build: .
    container_name: todo-bot
    environment:
      - BOT_CREDENTIALS=cts_host@secret_key@bot_id
      - DB_CONNECTION=postgres://postgres:postgres@postgres:5432/todo_bot_db
      - REDIS_DSN=redis://redis:6379/0
      - DEBUG=true
    ports:
      - "8000:8000"  # Отредактируйте порт хоста (первый), если он уже занят
    restart: always
    depends_on:
      - postgres
      - redis
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "10"

  postgres:
    image: postgres:13.2-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=todo_bot_db
    ports:
      - "5432:5432"
    restart: always
    volumes:
      - /tmp/postgresdata:/var/lib/postgresql/12/main

  redis:
    image: redis:6.2-alpine
    ports:
      - "6379:6379"
    restart: always
    volumes:
      - /tmp/redisdata:/var/lib/postgresql/data
```

4. Запустите контейнеры командой:

```bash
docker-compose up -d
```
5. Убедитесь, что в логах хранилищ нет ошибок.

```bash
docker-compose logs
```

6. Найдите бота через поиск корпоративных контактов (иконка человечка слева-сверху в
   мессенджере), напишите ему что-нибудь для проверки (у бота есть команда
   `/help`).
