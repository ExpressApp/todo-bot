# todo-bot

[![codecov](https://codecov.io/gh/ExpressApp/todo-bot/branch/master/graph/badge.svg?token=PTRJR2ITHW)](https://codecov.io/gh/ExpressApp/todo-bot)

Бот создан на базе шаблона [async-box](https://github.com/ExpressApp/async-box).

## Описание

Бот, позволяющий составлять список дел на день, следить за их выполнением.


## Переменные окружения

* `BOT_CREDENTIALS`: Учётные данные бота. Состоят из блоков
  `cts_host@secret_key@bot_id`, разделённых запятыми (один бот может быть
  зарегистрирован на нескольких CTS. `cts_host` -- адрес админки, `secret_key` и
  `bot_id` можно получить после регистрации бота, кликнув на его имя. Инструкция по
  регистрации бота находится в [Руководстве
  администратора](https://express.ms/admin_guide.pdf) `->` Эксплуатация корпоративного
  сервера `->` Управление контактами `->` Чат-боты.
* `DB_CONNECTION`: DSN для БД PostgreSQL, например:
  `postgres://postgres_user:postgres_password@postgres:port/db_name`
* `REDIS_DSN`: DSN для хранилища Redis, например: `redis://redis:6379/0`
* `DEBUG` [`false`]: Включает вывод сообщений уровня `DEBUG` (по-умолчанию выводятся
    сообщения с уровня `INFO`).
* `SQL_DEBUG` [`false`]: Включает вывод запросов к БД PostgreSQL.


## Деплой

**Примечание**: Чтобы легко добавлять новых ботов на сервер, хранилища находятся в
отдельной docker-сети и используются несколькими ботами сразу (каждый обращается к своей
БД, но к единственному экземпляру PosgreSQL/Redis). При необходимости хранилища и бота
легко объединить в один docker-compose файл.


### Настройка хранилищ, используемых ботом

1. Создайте директорию для PosgreSQL+Redis.

```shell
mkdir -p /opt/express/bots/storages
```

2. В директории `/opt/express/bots/storages` создайте файл `docker-compose.yml` со
   следующим содержимым:

```yaml
version: "3.8"

services:
  postgres:
    image: postgres:13.2-alpine
    env_file: .env
    ports:
      - "5432:5432"
    restart: always
    networks:
      - express_bots_storages
    volumes:
      - /opt/express/bots/storages/postgresdata:/var/lib/postgresql/12/main
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "10"

  redis:
    image: redis:6.2-alpine
    env_file: .env
    ports:
      - "6379:6379"
    restart: always
    networks:
      - express_bots_storages
    volumes:
      - /opt/express/bots/storages/redisdata:/var/lib/postgresql/data
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "10"

networks:
  express_bots_storages:
    name: express_bots_storages
```

3. Заполните файл `.env` необходимыми данными (для генерации паролей используйте команду
   `openssl rand -hex 16`):

```bash
POSTGRES_USER="postgres"  # Общий пользователь PostgreSQL, у бота будет свой собственный
POSTGRES_PASSWORD="<GENERATE>"
```

4. Запустите контейнеры командой `docker-compose up -d`.
5. Убедитесь, что в логах хранилищ нет ошибок.

```bash
docker-compose logs
```


### Настройка бота

1. Создайте БД и пользователя для бота (для генерации паролей используйте команду
   `openssl rand -hex 16`):

```shell
docker exec -it storages_postgres_1 psql --user postgres
```

```sql
CREATE USER todo_bot_user PASSWORD "<GENERATE>";
CREATE DATABASE todo_bot_db;
GRANT ALL PRIVILEGES ON DATABASE todo_bot_db TO todo_bot_user;
```

2. Создайте бота в админке eXpress. Хост CTS (в строке браузера, когда вы в админке) и
   "Secret key" пригодятся для заполнения переменной окружения `BOT_CREDENTIALS`.

3. Создайте директорию для бота.

```shell
mkdir -p /opt/express/bots/todo-bot
```

4. В директории `/opt/express/bots/todo-bot` создайте файл
   `docker-compose.yml` со следующим содержимым:

```yaml
version: "3.8"

services:
  todo-bot:
    image: registry.example.com/bots/todo-bot:master
    container_name: todo-bot
    env_file: .env
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

networks:
  default:
    external:
      name: express_bots_storages
```

5. Заполните `.env` необходимыми данными:

```bash
BOT_CREDENTIALS="example.cts.domain@d87f0dce2280d04b41f08e3adb1ae81c@5ce31515-32ae-435a-b6f4-748d2ced921d"
# etc.
```

Описание переменных и примеры можно посмотреть в [соответствующем
разделе](#переменные-окружения).

6. Запустите бота командой:

```bash
docker-compose up -d
```

7. Найдите бота через поиск корпоративных контактов (иконка человечка слева-сверху в
   мессенджере), напишите ему что-нибудь для проверки (обычно у бота есть команда
   `/help`).

8. Убедитесь, что в логах бота нет ошибок.

```bash
docker-compose logs
```
