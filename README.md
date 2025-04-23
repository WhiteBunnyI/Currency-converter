# Currency-converter
Web server that converts the currency

---

## Запуск сервера

1) Сборка образа:
```
docker-compose build
```
2) Запуск контейнера:
```
docker-compose up -d
```
Либо собрать и сразу запустить контейнер:
```
docker-compose up -d --build
```
Остановить контейнер:
```
docker-compose down
```
Обновить курс валют:
```
docker-compose exec web flask import
```
Для того, чтобы попасть на сайт, запустите сервер и перейдите по адресу:
http://127.0.0.1:5000