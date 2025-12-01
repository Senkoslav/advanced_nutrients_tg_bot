# Инструкция по настройке бота Advanced Nutrients Russia

## 1. Получение ADMIN_CHAT_ID

### Вариант А: Личный чат с админом
1. Админ должен написать боту `/start`
2. Получить свой ID через бота @userinfobot
3. Указать этот ID в `.env` как `ADMIN_CHAT_ID=123456789`

### Вариант Б: Группа/канал (рекомендуется)
1. Создайте группу в Telegram
2. Добавьте вашего бота в группу как администратора
3. Добавьте бота @RawDataBot или @getidsbot в группу
4. Скопируйте ID группы (будет отрицательным, например `-1001234567890`)
5. Укажите в `.env`: `ADMIN_CHAT_ID=-1001234567890`
6. Удалите @RawDataBot из группы

## 2. Установка зависимостей

```bash
pip install -r requirements.txt
```

## 3. Настройка PostgreSQL

Убедитесь что PostgreSQL запущен и создана база данных:

```sql
CREATE DATABASE advanced_nutrients_db;
```

Или измените параметры в `.env` на свои.

## 4. Запуск бота

```bash
python bot.py
.\venv\Scripts\python.exe bot.py
```

## 5. Проверка работы

1. Напишите боту `/start`
2. Проверьте все кнопки меню
3. Попробуйте задать вопрос эксперту (должен прийти в админ-чат)
4. Подпишитесь на уведомления (проверьте запись в БД)

## Структура проекта

```
├── bot.py              # Точка входа
├── config.py           # Конфигурация
├── .env                # Переменные окружения
├── requirements.txt    # Зависимости
├── database/
│   ├── core.py        # Работа с БД
│   └── models.py      # Модели SQLAlchemy
├── handlers/
│   ├── common.py      # /start, О бренде
│   ├── expert.py      # Вопросы эксперту
│   └── subscription.py # Подписка на уведомления
├── keyboards/
│   └── inline.py      # Inline-клавиатуры
└── states/
    └── user_states.py # FSM состояния
```
