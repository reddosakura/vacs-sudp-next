![logo](https://github.com/user-attachments/assets/a5c49f82-178a-4766-8f4c-7ba6a1ce94f5) 
СИСТЕМА УПРАВЛЕНИЯ ДОСТУПОМ ПОСЕТИТЕЛЕЙ
<br>Система контроля доступа контингента на территорию и видеонаблюдения

<h1>1. Разватывание API</h1>
Для полноценного функционирования системы требуется установить ядро системы. Для скачивания API требуется выполнить следующие команды:

```bash
git clone https://github.com/reddosakura/sudp-api-sync
cd sudp-api-sync
```

Запуск ядра системы производится данной командой:
```
docker compose up -d
```
Развертывание СУБД PostgreSQL и структуры базы данных произойдет автоматически

<h1>2. Разватывание системы</h1>
Для скачивания и установки системы требуется выполнить следующие команды:

```bash
git clone https://github.com/reddosakura/vacs-sudp-next
cd vacs-sudp-next
```
Далее треубется установить зависимости:
```bash
python3 -m pip install -r requirements.txt
```

После установки зависимостей запустить систему командой:
```bash
python3 -m flask run
```
