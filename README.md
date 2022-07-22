# Бот с музыкой из ВК

[![CI](https://github.com/kirilllapushinskiy/music-bot/actions/workflows/ci.yml/badge.svg?branch=production)](https://github.com/kirilllapushinskiy/music-bot/actions/workflows/ci.yml)

👉 [Музыкальная возня](https://t.me/MusicVoznyaBot) – пример реализации.

[История изменений](docs/CHANGES.md)

#### Инструкция по установке:

> Установите переменные окружения в файл ```.env``` и выполните следующие команды:
>```shell
>docker-compose build
>MODE=<polling/webhook> docker-compose up -d
>```