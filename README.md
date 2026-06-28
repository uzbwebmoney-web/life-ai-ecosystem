# Life AI Ecosystem

Персональная AI-экосистема в Telegram — **30 модулей** + cross-cutting возможности.

## Запуск

```bash
cd "C:\Users\Windows 11\life-ai-ecosystem"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python -m app.main
```

`.env`:
```
BOT_TOKEN=...
OPENAI_API_KEY=...   # AI, голос (Whisper), OCR (Vision)
```

## Реализовано

### 30 модулей
Полный каталог с подразделами — навигация по категориям.

### Cross-cutting
| Функция | Как |
|---------|-----|
| 📊 Панель | Статистика, финансы, профили |
| 🤖 AI-чат | `/ask`, кнопка в модулях, свободный текст |
| 🧠 Память AI | Авто + `/memory`, вкл/выкл в настройках |
| 🔍 Поиск по жизни | Записи + память |
| 🎤 Голос | Whisper — отправьте голосовое |
| 📷 OCR/Vision | Чеки, документы, ошибки авто |
| 👨‍👩‍👧 Семья | Профили, переключение |
| 📅 Календарь | События, `/event` через кнопку |
| 🔔 Push-напоминания | Фоновый worker, `/remind` |
| 🛡 Безопасность | Проверка ссылок |
| 🌿 Погода | Open-Meteo по запросу |
| 🧭 Intent-router | Авто-маршрутизация текста в модуль |

### Кредиты (ручной ввод)
Финансы → **Кредиты** или `/credit`:
1. Название (банк)
2. Сумма кредита
3. Платёж в месяц
4. Число месяца (1–31)

Бот напомнит автоматически в этот день каждый месяц.

### Команды
`/start` `/menu` `/ask` `/memory` `/remind` `/credit` `/lang`

### Языки
🇷🇺 Русский · 🇺🇿 O'zbek · 🇬🇧 English — `/lang` или **⚙️ Настройки → 🌐 Язык**

## Структура
- `app/core/modules/catalog.py` — 30 модулей
- `app/services/` — AI, media, weather, reminders
- `app/bot/handlers/` — hub, family, calendar, media, actions

## Принцип: без внешних API

Календарь, кредиты, напоминания, чеки и документы — **только ручной ввод в боте**.
Без подключения Google Calendar, почты, облаков (Dropbox, iCloud) и банковских push-уведомлений — у них нет публичного API для таких задач.

## Дальше

TTS-ответы голосом, vector RAG-память, углубление модулей — см. `docs/ROADMAP.md`.
