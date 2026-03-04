### Инструкция по разворачиванию
1. Выполнить команду (docker-compose up -d --build)
2. Накатить миграции [create_evnet_manager_tables.sql](migrations/create_evnet_manager_tables.sql)

### Список команд
1. Команда `docker-composer up -d --build` - поднять контейнеры
2. Команда `docker-compose down` - остановить контейнеры
3. Команда `docker log -f event_backend` - логик контейнера event_backend


### Список АПИ методов:
1. Реагистрация пользователя
2. Авторизация пользователя

