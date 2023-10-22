# Проект Фудграм


### Описание

Кулинарная социальная сеть для ваших кулинарных свершений.
Делитесь своими рецептами и узнавайте новые.
Подписывайтесь на авторов рецептов.
Добавляйте рецепты в избранное. 
Автоматическое составление списка покупок.

### Технологии

* Python 3.10

* Django 3.2

* DRF

* Djoser

* Postgres

* Gunicorn

* nginx

* Docker

* Docker compose


#### Для локального запуска проекта выполнить команды:

- Скопировать в `/backend` файл `.env.example` в `.env` с соответствующими значениями;
- `sudo docker compose -f docker-compose.develop.yaml up -d --build`
- `sudo docker compose exec backend python manage.py migrate --noinput` - применение миграций 
- `sudo docker compose exec backend python manage.py collectstatic --no-input` - сбор статики


#### Для запуска проекта на сервере через github action необходимо сделать `push` на ветку `master`:


### Документация и админ-панель
#### Документация находится по ссылке. Здесь же Вы найдете примеры использования api:
`http://localhost/docs/`
#### Админ-панель доступна по адресу:
`http://localhost/admin/` 
#### Сам проект доступен по адресу
`http://localhost/`

#### При первом запуске БД можно наполнить фикстурами(при необходимости)
Находятся в data:
- `data/dump_ingredients.json`;
- `data/dump_tags.json`;
- Загрузка осуществляется при необходимости командой `python manage.py loaddata <path_to_json>`


### Развернутый проект можно посмотреть по ссылкам:

- http://foodgram.serveblog.net

- http://158.160.73.243/signin

### админка:
- email: bot@bot.ru
- login: admin
- pass: admin01


## Автор: Natalia Lyakhovitskaya https://github.com/momtheprogram
