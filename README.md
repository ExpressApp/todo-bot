# todo-bot

[![codecov](https://codecov.io/gh/ExpressApp/todo-bot/branch/master/graph/badge.svg?token=PTRJR2ITHW)](https://codecov.io/gh/ExpressApp/todo-bot)

Бот создан на базе шаблона [async-box](https://github.com/ExpressApp/async-box).

## Описание

Бот, позволяющий составлять список дел на день, следить за их выполнением.

## Инструкция по развёртыванию ToDo bot

> :note: Если вы планируете развёртывать несколько ботов на сервере, используйте
> продвинутый вариант инструкции:
> [detailed-deploy.md](https://github.com/ExpressApp/todo-bot/blob/feature/easy-deploy/detailed-deploy.md).



1. Воспользуйтесь инструкцией [Руководство 
   администратора](https://express.ms/admin_guide.pdf) `-> Эксплуатация корпоративного 
   сервера -> Управление контактами -> Чат-боты`, чтобы создать бота в админке 
   eXpress. 
   Получите `secret_key` и `bot_id` кликнув на имя созданного бота. 
   Получите `cts_host` в строке браузера, когда вы в админке. 
   

2. Скачайте репозиторий на сервер:

```bash
git clone https://github.com/ExpressApp/todo-bot.git /opt/express/bots/todo-bot
cd /opt/express/bots/todo-bot
```

3. Отредактируйте `docker-compose.yml` подставив вместо `cts_host`, `secret_key` и `bot_id` реальные значения.


4. Запустите контейнеры командой:

```bash
docker-compose up -d
```

5. Убедитесь, что в логах нет ошибок.

```bash
docker-compose logs
```

6. Найдите бота через поиск корпоративных контактов (иконка человечка слева-сверху в
   мессенджере), напишите ему что-нибудь для проверки.
