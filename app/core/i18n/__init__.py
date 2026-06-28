from __future__ import annotations

SUPPORTED_LANGUAGES: tuple[str, ...] = ("ru", "uz", "en")

LANG_LABELS: dict[str, str] = {
    "ru": "🇷🇺 Русский",
    "uz": "🇺🇿 O'zbek",
    "en": "🇬🇧 English",
}

_STRINGS: dict[str, dict[str, str]] = {
    "ru": {
        "welcome": (
            "🧠 <b>Life AI Ecosystem</b>\n\n"
            "Помощник по жизни: здоровье, авто, финансы, право, дом и другое.\n\n"
            "<b>Как пользоваться:</b>\n"
            "1. Выберите тему (например ⚖️ Юридическая помощь или 🏥 Здоровье)\n"
            "2. Напишите вопрос — AI ответит <b>только по этой теме</b>\n"
            "3. Сохраняйте записи и напоминания внутри раздела\n\n"
            "🧠 Память AI · 🔍 Поиск · 📊 Панель · 🔔 Напоминания"
        ),
        "choose_language": "🌐 Выберите язык интерфейса:",
        "start_pick_language": "👋 <b>Добро пожаловать в Life AI!</b>\n\n🌐 Выберите язык:",
        "language_changed": "✅ Язык изменён на {label}",
        "main_menu": (
            "🧠 <b>Life AI</b>\n\n"
            "Выберите, чем заняться.\n\n"
            "💡 Можно <b>просто написать вопрос</b> — кнопка не обязательна."
        ),
        "btn_all_by_category": "📂 Все разделы",
        "btn_open_menu": "🚀 Открыть меню",
        "btn_help": "❓ Помощь",
        "btn_search_record": "🔍 Найти запись",
        "btn_dashboard": "📊 Панель управления",
        "btn_ai_assistant": "🤖 AI-ассистент",
        "btn_search": "🔍 Поиск по жизни",
        "btn_calendar": "📅 Календарь",
        "btn_family": "👨‍👩‍👧 Семья",
        "btn_voice": "🎤 Голосовой режим",
        "btn_all_modules": "📚 Все разделы",
        "btn_settings": "⚙️ Настройки",
        "btn_language": "🌐 Язык",
        "btn_back_menu": "🏠 Главная",
        "btn_back_categories": "⬅️ Категории",
        "btn_back_module": "⬅️ Назад",
        "btn_ask_ai": "💬 Задать вопрос",
        "btn_add_record": "➕ Сохранить заметку",
        "btn_add_record_full": "➕ Сохранить заметку",
        "btn_memory_on": "🧠 Память: ✅",
        "btn_memory_off": "🧠 Память: ❌",
        "btn_voice_on": "🎤 Голос: ✅",
        "btn_voice_off": "🎤 Голос: ❌",
        "btn_family_profiles": "👨‍👩‍👧 Семейные профили",
        "btn_add_profile": "➕ Добавить профиль",
        "btn_add_credit": "➕ Добавить кредит",
        "btn_cancel": "❌ Отмена",
        "settings_title": "⚙️ <b>Настройки</b>",
        "settings_memory": "🧠 Память AI: {status}",
        "settings_voice": "🎤 Голосовой режим: {status}",
        "settings_lang": "🌐 Язык: {label}",
        "settings_commands": "Команда /help — краткая инструкция.",
        "settings_tip": "💡 <b>Память AI</b> — бот запоминает важное из диалогов.\n🎤 <b>Голос</b> — ответы дублируются голосом.",
        "settings_extra": "Отправьте 🎤 голос или 📷 фото — распознавание автоматически.",
        "memory_on_toast": "Память включена",
        "memory_off_toast": "Память выключена",
        "voice_on_toast": "Голосовой режим включён — отправляйте голосовые",
        "voice_off_toast": "Голосовой режим выключен",
        "dashboard_title": "📊 <b>Единая панель управления</b>",
        "dashboard_body": (
            "👤 Профиль: <b>{profile}</b>\n"
            "👨‍👩‍👧 Семейных профилей: <b>{profiles}</b>\n"
            "💳 Активных кредитов: <b>{credits}</b>\n"
            "📝 Записей: <b>{records}</b>\n"
            "📅 Событий: <b>{events}</b>\n"
            "🔔 Напоминаний: <b>{reminders}</b>\n"
            "🧠 Память AI: <b>{memory}</b>\n\n"
            "💰 Доходы: <b>{income:.0f}</b> | Расходы: <b>{expense:.0f}</b>\n"
            "📈 Баланс: <b>{balance:.0f}</b>\n\n"
            "📦 Разделов: <b>{modules}</b>"
        ),
        "all_modules": "📚 <b>Категории</b> ({count})\n\nВыберите:",
        "pick_module": "📂 <b>{category}</b>\n\nЧто вас интересует?",
        "module_not_found": "Раздел не найден",
        "not_found": "Не найдено",
        "module_sections": "Разделы:",
        "module_more": "… и ещё {count}",
        "module_ask_here": "💬 <b>Напишите вопрос прямо сюда</b> — отвечу по этой теме.",
        "module_example_label": "Пример:",
        "module_or_pick": "Или выберите раздел или кнопку ниже.",
        "submodule_ask": "💬 <b>Задайте вопрос по теме «{sub}»</b> — ответ будет только по этому разделу.",
        "submodule_also": "Также можно:\n• ➕ сохранить запись\n• 🔍 найти через «Поиск по жизни»",
        "search_title": "🔍 <b>Поиск по жизни</b>",
        "search_hint": "Например:\n• <code>масло</code>\n• <code>анализ крови</code>\n• <code>страховка</code>\n\nИщу в записях и памяти AI.",
        "search_enter": "Введите текст для поиска.",
        "search_results": "🔍 Результаты по «<b>{query}</b>»",
        "search_records": "Записи:",
        "search_memory": "Память AI:",
        "search_nothing": "Ничего не найдено. Добавьте запись в нужном разделе.",
        "family_title": "👨‍👩‍👧 <b>Семейный режим</b>",
        "family_desc": "Профили для записей здоровья, календаря и напоминаний.",
        "family_active": "Активный профиль: <b>{name}</b>",
        "family_switched": "Профиль переключён",
        "family_not_found": "Профиль не найден",
        "family_add_name": "👤 Введите имя профиля (например: Мама, Сын, Жена):",
        "family_name_short": "Имя слишком короткое.",
        "family_add_relation": "Кто этот человек?",
        "family_rel_self": "Я",
        "family_rel_spouse": "Супруг(а)",
        "family_rel_child": "Ребёнок",
        "family_rel_parent": "Родитель",
        "family_rel_other": "Другое",
        "family_added": "✅ Профиль «{name}» добавлен.",
        "ai_thinking": "⏳ Думаю…",
        "ai_module_thinking": "{emoji} Думаю на тему «{module}»…",
        "ai_ask_module": "💬 <b>{module}</b> — напишите ваш вопрос:",
        "ai_assistant_title": "🤖 <b>AI-ассистент</b>",
        "ai_assistant_ask": "Задайте любой вопрос:",
        "record_new": "➕ <b>Новая запись</b> ({module})",
        "record_send": "Отправьте текст записи.",
        "record_send_finance": "Отправьте текст записи.\nПосле этого бот спросит сумму.",
        "record_amount": "💰 Сколько потратили? (число, или 0 — без суммы):",
        "record_amount_error": "Введите число, например 150000",
        "record_saved": "✅ Запись сохранена.",
        "memory_cmd": "🧠 Отправьте факт для сохранения в память AI:",
        "memory_saved": "✅ Сохранено в память AI.",
        "remind_format": (
            "🔔 Формат:\n"
            "<code>Заголовок | 25.06.2026 09:00</code>\n\n"
            "Или отправьте только заголовок — спросим дату отдельно."
        ),
        "remind_date_error": "Формат даты: ДД.ММ.ГГГГ ЧЧ:ММ (например 25.06.2026 09:00)",
        "remind_created": "✅ Напоминание: {title} — {when}",
        "remind_datetime": "📅 Введите дату и время: <code>25.06.2026 09:00</code>",
        "remind_default_title": "Напоминание",
        "free_text_pick_module": "<i>Для точного ответа выберите тему: Здоровье, Авто, Право и т.д.</i>",
        "weather_title": "🌿 <b>Экология / погода</b>",
        "voice_recognizing": "🎤 Распознаю…",
        "voice_failed": "⚠️ Не удалось распознать. Проверьте OPENAI_API_KEY.",
        "photo_analyzing": "📷 Анализирую фото (OCR/Vision)…",
        "photo_done": "📷 <b>Распознано</b>",
        "cat_0": "Здоровье и питание",
        "cat_1": "Деньги и бизнес",
        "cat_2": "Транспорт и путешествия",
        "cat_3": "Дом и покупки",
        "cat_4": "Обучение",
        "cat_5": "Право",
        "cat_6": "Планирование",
        "cat_7": "AI и данные",
        "lang_reply_ru": "русском",
        "lang_reply_uz": "узбекском",
        "lang_reply_en": "английском",
        "credits_my": "💳 <b>Мои кредиты</b>",
        "credits_title": "💳 <b>Кредит и ипотека</b>",
        "credits_empty": "Пока нет сохранённых кредитов.",
        "credits_empty_short": "Добавьте кредит вручную — бот будет напоминать о платеже каждый месяц.",
        "credits_hint": "Добавьте вручную:\n• название (банк/кредит)\n• сумма кредита\n• платёж в месяц\n• число месяца (1–31)",
        "credits_notify": "<i>Напоминание придёт автоматически в день оплаты каждый месяц.</i>",
        "credits_new": "💳 <b>Новый кредит</b>\n\nВведите название (банк или название кредита):",
        "credits_cancelled": "Добавление кредита отменено.",
        "credits_title_short": "Название слишком короткое.",
        "credits_total": "💰 Введите <b>общую сумму кредита</b> (число):",
        "credits_total_error": "Введите число, например 50000000",
        "credits_total_positive": "Сумма должна быть больше 0.",
        "credits_monthly": "📅 Введите <b>сумму платежа каждый месяц</b>:",
        "credits_monthly_error": "Введите число, например 1500000",
        "credits_day": "🗓 Введите <b>число месяца</b> для оплаты (1–31):\nНапример: <code>15</code> — напоминание каждое 15-е число.",
        "credits_day_error": "Введите число от 1 до 31.",
        "credits_day_range": "Число должно быть от 1 до 31.",
        "credits_saved": "✅ Кредит сохранён!\n\n{info}\n\n🔔 Напоминание будет приходить каждое <b>{day}-е число</b>.",
        "credits_deleted_all": "💳 Кредиты удалены. Добавьте новый при необходимости.",
        "credits_not_found": "Кредит не найден",
        "credits_removed": "Кредит удалён",
        "credits_line": (
            "• <b>{title}</b>\n"
            "  Сумма: {total}\n"
            "  Остаток: <b>{remaining}</b>\n"
            "  Платёж/мес: {monthly}\n"
            "  День оплаты: <b>{day}</b>-е число"
        ),
        "credits_reminder": (
            "💳 <b>Напоминание о платеже</b>\n\n"
            "🏦 {title}\n"
            "💰 Платёж: <b>{monthly}</b>\n"
            "📋 Остаток: <b>{remaining}</b>\n"
            "📅 Сегодня <b>{day}-е число</b> — не забудьте оплатить.\n\n"
            "Нажмите «Записать платёж» — пересчитаю остаток."
        ),
        "credits_btn_log_payment": "✅ Записать платёж",
        "credits_payment_prompt": "💳 <b>{title}</b>\n\nСколько оплатили? (например {monthly})",
        "credits_payment_saved": "✅ Записано: {paid}\nОстаток: <b>{remaining}</b>",
        "credits_paid_off": "🎉 Кредит «{title}» полностью погашен!",
        "default_loan_title": "Кредит",
        "doc_saved": "📄 Документ «{name}» сохранён.\nДля PDF отправьте скрин или фото страницы.",
        "link_check": "🛡 <b>Проверка ссылки</b>",
        "link_risk": "Риск: {risk}",
        "photo_title_default": "Фото",
        "health_module_intro": (
            "🩺 <b>Здоровье</b> — ваш медицинский помощник:\n\n"
            "• AI по симптомам, анализам и обследованиям\n"
            "• Лекарства и взаимодействия\n"
            "• Напоминания о приёме и визитах к врачу\n"
            "• Дневник давления, сахара, веса\n"
            "• Хранение мед. документов"
        ),
        "health_ai_hint": "💬 Напишите вопрос — AI ответит по этой теме.",
        "health_sub_consultant": "AI-консультант по симптомам. Опишите самочувствие.",
        "health_sub_symptoms": "Разбор симптомов: что может означать и когда к врачу.",
        "health_sub_tests": "Объяснение результатов анализов простым языком.",
        "health_sub_exams": "Объяснение результатов обследований (УЗИ, МРТ, рентген и др.).",
        "health_sub_medicines": "Информация о лекарствах, дозировках и взаимодействиях.",
        "health_sub_diary": "Дневник давления, сахара, веса и других показателей.",
        "health_sub_med_reminders": "Ежедневные напоминания о приёме лекарств.",
        "health_sub_visits": "Напоминания о визитах к врачу.",
        "health_sub_documents": "Хранение анализов, справок и мед. документов.",
        "health_metric_pressure": "Давление",
        "health_metric_sugar": "Сахар",
        "health_metric_weight": "Вес",
        "health_metric_other": "Показатель",
        "health_diary_title": "📋 <b>Дневник показателей</b>",
        "health_diary_empty": "Пока нет записей. Добавьте первое измерение.",
        "health_diary_recent": "<b>Последние записи:</b>",
        "health_add_pressure": "➕ Давление",
        "health_add_sugar": "➕ Сахар",
        "health_add_weight": "➕ Вес",
        "health_view_all": "📊 Вся история",
        "health_enter_pressure": "Введите давление в формате <code>120/80</code>:",
        "health_enter_sugar": "Введите уровень сахара (ммоль/л), например <code>5.6</code>:",
        "health_enter_weight": "Введите вес (кг), например <code>75</code>:",
        "health_enter_notes": "Комментарий (или <code>-</code> чтобы пропустить):",
        "health_metric_saved": "✅ Запись сохранена в дневник.",
        "health_invalid_pressure": "Формат: 120/80",
        "health_invalid_value": "Введите число.",
        "health_med_title": "💊 <b>Приём лекарств</b>",
        "health_med_empty": "Нет активных лекарств. Добавьте первое.",
        "health_med_hint_multi": "Можно добавить несколько препаратов. Нажмите на препарат — изменить или удалить.",
        "health_med_count": "Активных препаратов: <b>{count}</b>",
        "health_med_add": "➕ Добавить лекарство",
        "health_med_name": "Введите название лекарства:",
        "health_med_dosage": "Дозировка (например: 1 таблетка):",
        "health_med_times": "Время приёма через запятую:\n<code>08:00, 20:00</code>",
        "health_med_times_error": "Укажите время в формате HH:MM, например 08:00, 20:00",
        "health_med_saved": "✅ Лекарство добавлено. Напоминания будут приходить в указанное время.",
        "health_med_removed": "Лекарство удалено",
        "health_med_not_found": "Не найдено",
        "health_med_dose": "Дозировка",
        "health_med_reminder_title": "Пора принять лекарство",
        "health_med_edit_name": "✏️ Название",
        "health_med_edit_dose": "✏️ Дозировка",
        "health_med_edit_times": "✏️ Время",
        "health_med_delete": "🗑 Удалить",
        "health_med_back_list": "⬅️ К списку",
        "health_med_updated": "✅ Изменения сохранены",
        "health_med_edit_name_prompt": "Новое название препарата:",
        "health_med_edit_dose_prompt": "Новая дозировка:",
        "health_med_edit_times_prompt": "Новое время приёма:\n<code>08:00, 20:00</code>",
        "health_visit_title": "🩺 <b>Визиты к врачу</b>",
        "health_visit_empty": "Нет предстоящих визитов.",
        "health_visit_add": "➕ Добавить визит",
        "health_visit_name": "К кому визит / специалист (например: терапевт):",
        "health_visit_datetime": "Дата и время: <code>25.06.2026 10:00</code>",
        "health_visit_saved": "✅ Напоминание о визите создано.",
        "health_doc_title": "📁 <b>Мед. документы</b>",
        "health_doc_empty": "Документов пока нет.",
        "health_doc_hint": "Отправьте 📷 фото или текст анализа/справки — сохраним в вашу мед. карту.",
        "health_doc_add": "➕ Текстовая запись",
        "health_doc_saved": "✅ Документ сохранён.",
        "car_module_intro": (
            "🚗 <b>Автомобиль</b> — помощник водителя:\n\n"
            "• Расшифровка ошибок по фото панели\n"
            "• Анализ звуков и неисправностей\n"
            "• График ТО и напоминания (масло, фильтры, шины)\n"
            "• Страховка и техосмотр\n"
            "• Учёт расходов на авто"
        ),
        "car_ai_hint": "💬 Напишите вопрос или отправьте 📷/🎤",
        "car_sub_panel_photo": "Отправьте фото панели приборов — AI расшифрует ошибки и индикаторы.",
        "car_sub_sounds": "Опишите звук или отправьте 🎤 голосовое — AI подскажет возможные неисправности.",
        "car_sub_service": "График технического обслуживания — все запланированные работы.",
        "car_sub_reminders": "Напоминания о замене масла, фильтров и шин.",
        "car_sub_compliance": "Сроки страховки и техосмотра с напоминаниями.",
        "car_sub_expenses": "Топливо, ремонт, мойка и другие расходы.",
        "car_panel_hint": "📷 Отправьте <b>фото панели приборов</b> с горящими индикаторами.\n\nAI расшифрует ошибки и подскажет, насколько это срочно.",
        "car_sounds_hint": "Опишите звук текстом или отправьте 🎤 голосовое:\n<i>скрип при торможении, стук слева, гул на скорости…</i>",
        "car_service_title": "🔧 <b>График ТО</b>",
        "car_service_empty": "Нет запланированных работ. Добавьте первую.",
        "car_service_hint": "Ближайшие работы:",
        "car_service_add": "➕ Добавить в график",
        "car_reminders_title": "⏰ <b>Напоминания</b> (масло, фильтры, шины)",
        "car_reminders_empty": "Напоминаний пока нет.",
        "car_maint_oil": "🛢 Масло",
        "car_maint_filter": "🧰 Фильтры",
        "car_maint_tires": "🛞 Шины",
        "car_maint_service": "🔧 ТО",
        "car_maint_other": "📋 Другое",
        "car_maint_pick_type": "Выберите тип работы:",
        "car_enter_date": "Дата (когда напомнить):\n<code>15.07.2026</code>",
        "car_comp_enter_date": "Дата окончания:\n<code>31.12.2026</code>",
        "car_enter_notes": "Комментарий (пробег, СТО…) или <code>-</code>",
        "car_date_error": "Формат: ДД.ММ.ГГГГ",
        "car_maint_saved": "✅ Добавлено в график ТО",
        "car_comp_saved": "✅ Срок сохранён",
        "car_expense_saved": "✅ Расход записан",
        "car_deleted": "Удалено",
        "car_not_found": "Не найдено",
        "car_back_list": "⬅️ К графику",
        "car_maint_delete": "🗑 Удалить",
        "car_comp_title": "📋 <b>Страховка и техосмотр</b>",
        "car_comp_empty": "Добавьте сроки страховки или техосмотра.",
        "car_comp_insurance": "🛡 Страховка",
        "car_comp_inspection": "✅ Техосмотр",
        "car_comp_add_insurance": "➕ Страховка",
        "car_comp_add_inspection": "➕ Техосмотр",
        "car_expires": "Окончание",
        "car_expires_today": "истекает сегодня",
        "car_expires_tomorrow": "истекает завтра",
        "car_expires_in_days": "осталось {days} дн.",
        "car_maint_reminder_title": "Напоминание по авто",
        "car_comp_reminder_title": "Срок по авто",
        "car_due_today": "сегодня по плану",
        "car_expenses_title": "💰 <b>Расходы на автомобиль</b>",
        "car_expenses_empty": "Расходов пока нет.",
        "car_expenses_total": "Всего: <b>{total}</b> UZS",
        "car_expenses_add": "➕ Добавить расход",
        "car_expense_title_prompt": "Что оплатили? (топливо, ремонт, мойка…)",
        "car_expense_amount_prompt": "Сумма (UZS):",
        "fin_module_intro": (
            "💰 <b>Финансы</b> — личный финансовый помощник:\n\n"
            "• Учёт доходов и расходов\n"
            "• Финансовые цели и накопления\n"
            "• Планирование бюджета по категориям\n"
            "• Напоминания об оплате счетов\n"
            "• Анализ расходов\n"
            "• Кредит и ипотека"
        ),
        "fin_ai_hint": "💬 Задайте вопрос AI по финансам",
        "fin_sub_income": "Записывайте зарплату, подработки и другие поступления.",
        "fin_sub_expense": "Учитывайте расходы с категориями.",
        "fin_sub_goals": "Ставьте цели: телефон, отпуск, накопления.",
        "fin_sub_budget": "Лимиты по категориям на месяц.",
        "fin_sub_bills": "Коммуналка, интернет, подписки — напоминания в срок.",
        "fin_sub_analysis": "Разбивка расходов и баланс за месяц.",
        "fin_sub_loans": "Кредиты и ипотека — сумма, ежемесячный платёж и день оплаты с напоминаниями.",
        "fin_income_title": "📈 <b>Доходы</b>",
        "fin_expense_title": "📉 <b>Расходы</b>",
        "fin_total": "Итого: <b>{total}</b> UZS",
        "fin_empty": "Пока нет записей.",
        "fin_add_tx": "➕ Добавить",
        "fin_tx_title_prompt": "Описание (зарплата, продукты…):",
        "fin_tx_amount_prompt": "Сумма (UZS):",
        "fin_tx_saved": "✅ Запись сохранена",
        "fin_pick_category": "Выберите категорию расхода:",
        "fin_cat_food": "🍔 Еда",
        "fin_cat_transport": "🚗 Транспорт",
        "fin_cat_home": "🏠 Дом",
        "fin_cat_health": "🏥 Здоровье",
        "fin_cat_fun": "🎬 Развлечения",
        "fin_cat_shopping": "🛒 Покупки",
        "fin_cat_bills": "💡 Счета",
        "fin_cat_other": "📋 Другое",
        "fin_goals_title": "🎯 <b>Финансовые цели</b>",
        "fin_goals_empty": "Целей пока нет.",
        "fin_goal_add": "➕ Новая цель",
        "fin_goal_title_prompt": "Название цели (например: отпуск):",
        "fin_goal_target_prompt": "Целевая сумма (UZS):",
        "fin_goal_current_prompt": "Уже накоплено (UZS) или 0:",
        "fin_goal_saved": "✅ Цель добавлена",
        "fin_goal_updated": "✅ Прогресс обновлён",
        "fin_goal_update": "📊 Обновить прогресс",
        "fin_goal_delete": "🗑 Удалить",
        "fin_goal_update_prompt": "Сколько уже накоплено (UZS):",
        "fin_back_goals": "⬅️ К целям",
        "fin_goal_default": "Цель",
        "fin_budget_title": "📊 <b>Бюджет на месяц</b>",
        "fin_budget_month": "Месяц: <b>{month}</b>",
        "fin_budget_empty": "Лимиты не заданы. Выберите категорию ниже.",
        "fin_budget_hint": "Нажмите категорию — задать лимит на месяц.",
        "fin_budget_limit_prompt": "Лимит для «{category}» (UZS):",
        "fin_budget_saved": "✅ Лимит сохранён",
        "fin_bills_title": "💳 <b>Оплата счетов</b>",
        "fin_bills_empty": "Счетов нет. Добавьте первый.",
        "fin_bill_add": "➕ Добавить счёт",
        "fin_bill_title_prompt": "Название (коммуналка, интернет…):",
        "fin_bill_amount_prompt": "Сумма (UZS):",
        "fin_bill_date_prompt": "Дата оплаты:\n<code>05.07.2026</code>",
        "fin_bill_saved": "✅ Счёт добавлен — напомним в день оплаты",
        "fin_bill_delete": "🗑 Удалить",
        "fin_bill_default": "Счёт",
        "fin_back_bills": "⬅️ К счетам",
        "fin_back_loans": "⬅️ К кредитам",
        "fin_loan_delete": "🗑 Удалить",
        "fin_bill_reminder_title": "Напоминание об оплате",
        "fin_due_today": "сегодня нужно оплатить",
        "fin_bill_pay": "оплатить",
        "fin_analysis_title": "📊 <b>Анализ расходов</b>",
        "fin_analysis_summary": "{month}: доход <b>{income}</b> | расход <b>{expense}</b> | баланс <b>{balance}</b> UZS",
        "fin_analysis_by_cat": "<b>По категориям:</b>",
        "fin_not_found": "Не найдено",
        "fin_deleted": "Удалено",
        "biz_module_intro": (
            "💼 <b>Бизнес</b> — AI-помощник предпринимателя:\n\n"
            "• AI-консультант по запуску и развитию\n"
            "• Бизнес-планы и стратегия\n"
            "• Генерация рекламы и креативов\n"
            "• Анализ конкурентов\n"
            "• Черновики договоров\n"
            "• Ответы клиентам\n"
            "• Анализ продаж"
        ),
        "biz_ai_hint": "💬 Опишите задачу или нажмите «Спросить AI»",
        "biz_sub_consultant": "Консультации по нише, модели, каналам продаж и рискам.",
        "biz_sub_plans": "Структурированные бизнес-планы: рынок, продукт, финансы, этапы.",
        "biz_sub_ads": "Рекламные тексты, заголовки, посты и объявления под вашу аудиторию.",
        "biz_sub_competitors": "Разбор конкурентов: сильные стороны, цены, позиционирование.",
        "biz_sub_contracts": "Черновики договоров — проверьте у юриста перед подписанием.",
        "biz_sub_client_responses": "Профессиональные ответы клиентам: жалобы, вопросы, продажи.",
        "biz_sub_sales_analysis": "Анализ продаж по вашим данным: тренды, воронка, рекомендации.",
        "leg_module_intro": (
            "⚖️ <b>Юридическая помощь</b> — AI-помощник по правовым вопросам:\n\n"
            "• Ответы на юридические вопросы\n"
            "• Проверка документов (текст или фото)\n"
            "• Генерация заявлений и обращений\n"
            "• Объяснение законодательства\n"
            "• Чек-листы действий в разных ситуациях\n\n"
            "⚠️ Не замена юриста — общая информация и черновики."
        ),
        "leg_ai_hint": "💬 Опишите ситуацию или нажмите «Спросить AI»",
        "leg_sub_questions": "Ответы о правах, обязанностях, сроках и порядке действий.",
        "leg_sub_doc_check": "Проверка договоров и документов — отправьте текст или фото.",
        "leg_sub_applications": "Черновики заявлений в госорганы, суд, работодателю.",
        "leg_sub_legislation": "Простое объяснение законов: кому применяется, что означает.",
        "leg_sub_checklists": "Пошаговые действия: документы, сроки, куда обращаться.",
        "trv_module_intro": (
            "✈️ <b>Путешествия</b> — помощник путешественника:\n\n"
            "• Планирование маршрутов\n"
            "• Визовая информация\n"
            "• Бюджет поездки\n"
            "• Чек-лист вещей\n"
            "• Переводчик фраз\n"
            "• Конвертер валют (справочные курсы)"
        ),
        "trv_ai_hint": "💬 Опишите поездку или нажмите «Спросить AI»",
        "trv_sub_routes": "Маршруты по дням: города, транспорт, достопримечательности.",
        "trv_sub_visas": "Справочно о визах: нужна ли, документы, сроки — проверяйте на сайте консульства.",
        "trv_sub_budget": "Бюджет: перелёт, жильё, еда, транспорт, развлечения, резерв.",
        "trv_sub_packing": "Чек-лист вещей с учётом климата и длительности поездки.",
        "trv_sub_translator": "Перевод и полезные фразы для аэропорта, отеля, ресторана.",
        "trv_sub_currency": "Конвертер валют и советы по обмену. Курсы справочные.",
        "trv_fx_convert": "💱 Конвертировать",
        "trv_fx_amount_prompt": "Сумма для конвертации:",
        "trv_fx_from_prompt": "Из какой валюты:",
        "trv_fx_to_prompt": "В какую валюту:",
        "trv_fx_result": "💱 <b>{amount}</b> = <b>{result}</b>",
        "trv_fx_disclaimer": "Справочный курс, не для финансовых операций.",
        "trv_fx_error": "Не удалось конвертировать",
        "home_module_intro": (
            "🏠 <b>Дом</b> — помощник по быту:\n\n"
            "• Напоминания об оплате коммуналки\n"
            "• Учёт домашних расходов\n"
            "• План ремонта\n"
            "• Список покупок\n"
            "• Домашний инвентарь"
        ),
        "home_sub_utilities": "Электричество, газ, вода, интернет — напомним в день оплаты.",
        "home_sub_expenses": "Записывайте траты на дом и быт.",
        "home_sub_repair": "Задачи ремонта со статусами: план → в работе → готово.",
        "home_sub_shopping": "Список покупок — отмечайте купленное одним нажатием.",
        "home_sub_inventory": "Что где лежит: предмет, количество, место.",
        "home_utilities_title": "💡 <b>Коммунальные услуги</b>",
        "home_expenses_title": "💰 <b>Домашние расходы</b>",
        "home_repair_title": "🔨 <b>План ремонта</b>",
        "home_shopping_title": "🛒 <b>Список покупок</b>",
        "home_inventory_title": "📦 <b>Домашний инвентарь</b>",
        "home_empty": "Пока пусто.",
        "home_total": "Итого: <b>{total}</b> UZS",
        "home_not_found": "Не найдено",
        "home_deleted": "Удалено",
        "home_delete": "🗑 Удалить",
        "home_utility_add": "➕ Добавить счёт",
        "home_utility_title_prompt": "Услуга (свет, газ, интернет…):",
        "home_utility_amount_prompt": "Сумма (UZS):",
        "home_utility_date_prompt": "Дата оплаты:\n<code>05.07.2026</code>",
        "home_utility_saved": "✅ Счёт добавлен — напомним в день оплаты",
        "home_utility_default": "Коммуналка",
        "home_utility_reminder_title": "Оплата коммуналки",
        "home_due_today": "сегодня нужно оплатить",
        "home_back_utilities": "⬅️ К счетам",
        "home_expense_add": "➕ Добавить расход",
        "home_expense_title_prompt": "На что потратили:",
        "home_expense_amount_prompt": "Сумма (UZS):",
        "home_expense_saved": "✅ Расход сохранён",
        "home_expense_default": "Расход",
        "home_repair_add": "➕ Добавить задачу",
        "home_repair_title_prompt": "Что нужно сделать:",
        "home_repair_notes_prompt": "Заметки (или «-» чтобы пропустить):",
        "home_repair_saved": "✅ Задача добавлена",
        "home_repair_default": "Ремонт",
        "home_repair_planned": "запланировано",
        "home_repair_in_progress": "в работе",
        "home_repair_done": "готово",
        "home_repair_cycle": "🔄 Сменить статус",
        "home_repair_updated": "Статус обновлён",
        "home_back_repair": "⬅️ К ремонту",
        "home_shopping_add": "➕ Добавить",
        "home_shopping_title_prompt": "Что купить:",
        "home_shopping_saved": "✅ Добавлено в список",
        "home_inventory_add": "➕ Добавить предмет",
        "home_inventory_title_prompt": "Название предмета:",
        "home_inventory_location_prompt": "Где лежит (или «-»):",
        "home_inventory_qty_prompt": "Количество:",
        "home_inventory_saved": "✅ Добавлено в инвентарь",
        "home_inventory_default": "Предмет",
        "home_inv_no_location": "место не указано",
        "home_back_inventory": "⬅️ К инвентарю",
        "shop_module_intro": (
            "🛒 <b>Покупки</b> — AI-помощник при выборе товаров:\n\n"
            "• Сравнение товаров\n"
            "• Поиск выгодных предложений\n"
            "• Проверка характеристик\n"
            "• Советы по выбору"
        ),
        "shop_ai_hint": "💬 Опишите товар или задачу, либо нажмите «Спросить AI»",
        "shop_sub_compare": "Сравнение моделей по цене, функциям, плюсам и минусам.",
        "shop_sub_deals": "Как найти выгодные предложения и отличить реальную скидку.",
        "shop_sub_specs": "Разбор характеристик — что означают параметры в описании.",
        "shop_sub_advice": "Рекомендации под ваш бюджет и задачи.",
        "edu_module_intro": (
            "📚 <b>Образование</b> — AI-репетитор:\n\n"
            "• Объяснение учебных тем\n"
            "• Подготовка к экзаменам\n"
            "• Изучение языков\n"
            "• Генерация конспектов\n"
            "• Проверка домашних заданий"
        ),
        "edu_ai_hint": "💬 Задайте вопрос или нажмите «Спросить AI»",
        "edu_sub_topics": "Любая тема простым языком: определения, примеры, аналогии.",
        "edu_sub_exams": "План подготовки, ключевые вопросы, повторение перед экзаменом.",
        "edu_sub_languages": "Грамматика, слова, диалоги и исправление ошибок.",
        "edu_sub_notes": "Структурированные конспекты по теме или лекции.",
        "edu_sub_homework": "Проверка с объяснением ошибок — не просто готовый ответ.",
        "nut_module_intro": (
            "🥗 <b>Питание</b> — помощник по здоровому питанию:\n\n"
            "• Подбор рациона\n"
            "• Расчёт калорий\n"
            "• Рецепты\n"
            "• Список продуктов\n"
            "• Учёт воды"
        ),
        "nut_ai_hint": "💬 Опишите цель или нажмите «Спросить AI»",
        "nut_sub_diet": "Сбалансированный рацион под ваши цели и предпочтения.",
        "nut_sub_calories": "Калорийность блюд и дневная норма — AI или калькулятор.",
        "nut_sub_recipes": "Рецепты с ингредиентами и примерной калорийностью.",
        "nut_sub_grocery": "Список продуктов для магазина — отмечайте купленное.",
        "nut_sub_water": "Сколько воды выпили сегодня — быстрые кнопки +250/+500 мл.",
        "nut_grocery_title": "🛒 <b>Список продуктов</b>",
        "nut_water_title": "💧 <b>Учёт воды</b>",
        "nut_empty": "Пока пусто.",
        "nut_not_found": "Не найдено",
        "nut_grocery_add": "➕ Добавить",
        "nut_grocery_title_prompt": "Что купить:",
        "nut_grocery_saved": "✅ Добавлено в список",
        "nut_water_summary": "Сегодня: <b>{total}</b> / {goal} мл ({pct}%)",
        "nut_water_hint": "Нажмите кнопку, чтобы добавить воду.",
        "nut_water_custom": "➕ Другой объём",
        "nut_water_ml_prompt": "Сколько мл выпили:",
        "nut_water_added": "✅ Добавлено",
        "nut_cal_calc": "🧮 Рассчитать норму",
        "nut_cal_weight_prompt": "Вес (кг):",
        "nut_cal_height_prompt": "Рост (см):",
        "nut_cal_age_prompt": "Возраст:",
        "nut_cal_sex_prompt": "Пол:",
        "nut_cal_male": "Мужской",
        "nut_cal_female": "Женский",
        "nut_cal_activity_prompt": "Уровень активности:",
        "nut_act_sedentary": "Минимальная",
        "nut_act_light": "Лёгкая",
        "nut_act_moderate": "Средняя",
        "nut_act_active": "Высокая",
        "nut_act_very": "Очень высокая",
        "nut_cal_result": "📊 Ваша дневная норма: <b>{kcal}</b> ккал\n\n<i>Ориентир по формуле Mifflin-St Jeor</i>",
        "org_module_intro": (
            "📅 <b>Органайзер</b> — всё в одном месте:\n\n"
            "• Задачи с дедлайнами\n"
            "• Календарь событий\n"
            "• Напоминания\n"
            "• Дни рождения\n"
            "• Встречи\n"
            "• Заметки"
        ),
        "org_tasks_title": "✅ <b>Задачи</b>",
        "org_calendar_title": "📅 <b>Календарь</b>",
        "org_reminders_title": "🔔 <b>Напоминания</b>",
        "org_birthdays_title": "🎂 <b>Дни рождения</b>",
        "org_meetings_title": "🤝 <b>Встречи</b>",
        "org_notes_title": "📝 <b>Заметки</b>",
        "org_empty": "Пока пусто.",
        "org_not_found": "Не найдено",
        "org_add": "➕ Добавить",
        "org_task_add": "➕ Новая задача",
        "org_task_title_prompt": "Название задачи:",
        "org_task_due_prompt": "Срок (или «-» без срока):\n<code>25.06.2026 18:00</code>",
        "org_task_saved": "✅ Задача добавлена",
        "org_task_default": "Задача",
        "org_note_add": "➕ Новая заметка",
        "org_note_title_prompt": "Заголовок заметки:",
        "org_note_body_prompt": "Текст (или «-»):",
        "org_note_saved": "✅ Заметка сохранена",
        "org_note_default": "Заметка",
        "org_meet_add": "➕ Встреча",
        "org_bday_add": "➕ День рождения",
        "org_event_title_prompt": "Название встречи:",
        "org_bday_title_prompt": "Имя (день рождения):",
        "org_event_date_prompt": "Дата и время:\n<code>25.06.2026 18:00</code>",
        "org_event_saved": "✅ Событие добавлено",
        "org_event_default": "Событие",
        "org_rem_add": "➕ Напоминание",
        "org_rem_title_prompt": "Текст напоминания:",
        "org_rem_date_prompt": "Когда напомнить:\n<code>25.06.2026 09:00</code>",
        "org_rem_saved": "✅ Напоминание: {title} — {when}",
        "org_rem_default": "Напоминание",
        "org_date_error": "Формат: ДД.ММ.ГГГГ ЧЧ:ММ",
        "ast_module_intro": (
            "🤖 <b>AI-ассистент</b> — универсальный помощник:\n\n"
            "• Ответы на любые вопросы\n"
            "• Переводы текстов\n"
            "• Работа с PDF и документами\n"
            "• Анализ фотографий\n"
            "• Создание текстов\n"
            "• Генерация картинок (DALL-E)\n"
            "• Помощь в программировании"
        ),
        "ast_ai_hint": "Напишите сообщение или нажмите «Спросить AI».",
        "ast_sub_questions": "Ответы на любые вопросы — факты, советы, объяснения.",
        "ast_sub_translate": "Перевод между языками с сохранением смысла и стиля.",
        "ast_sub_documents": "PDF и документы: краткое содержание, ключевые пункты, вопросы по тексту.",
        "ast_sub_photo": "Отправьте фото — AI распознает объекты, текст и контекст.",
        "ast_sub_writing": "Статьи, посты, письма, резюме — создание и редактирование текстов.",
        "ast_sub_images": "Опишите картинку текстом — AI сгенерирует изображение.",
        "ast_sub_code": "Код, отладка, алгоритмы, архитектура — помощь программисту.",
        "ast_send_photo": "📷 Отправьте фото для анализа.",
        "ast_send_image_prompt": "✏️ Опишите картинку одним сообщением.",
        "ast_send_document": "📎 Отправьте PDF или документ, затем задайте вопрос по нему.",
        "ast_image_generating": "🎨 Генерирую изображение…",
        "ast_image_failed": "⚠️ Не удалось создать картинку. Проверьте OPENAI_API_KEY или попробуйте другой запрос.",
        "ast_image_done": "🎨 {prompt}",
        "ast_doc_saved": "📎 Документ «{name}» сохранён.",
        "ast_doc_caption_note": "Задайте вопрос по документу текстом — AI поможет.",
        "vlt_module_intro": (
            "🔐 <b>Личное хранилище</b> — ваши данные в одном месте:\n\n"
            "• Документы\n"
            "• Паспортные данные (по желанию)\n"
            "• Полисы\n"
            "• Гарантийные талоны\n"
            "• Чеки\n"
            "• Важные заметки\n\n"
            "<i>Данные хранятся только у вас в боте.</i>"
        ),
        "vlt_documents_title": "📄 <b>Документы</b>",
        "vlt_passport_title": "🛂 <b>Паспортные данные</b>",
        "vlt_policies_title": "📋 <b>Полисы</b>",
        "vlt_warranty_title": "🧾 <b>Гарантийные талоны</b>",
        "vlt_receipts_title": "🧾 <b>Чеки</b>",
        "vlt_notes_title": "📝 <b>Важные заметки</b>",
        "vlt_empty": "Пока пусто.",
        "vlt_add": "➕ Добавить",
        "vlt_not_found": "Не найдено",
        "vlt_deleted": "Удалено",
        "vlt_saved": "✅ Сохранено",
        "vlt_default_title": "Запись",
        "vlt_title_prompt": "Название записи:",
        "vlt_body_prompt": "Описание или детали (или «-»):",
        "vlt_amount_prompt": "Сумма чека (или «-»):",
        "vlt_amount_error": "Введите число или «-»",
        "vlt_passport_hint": "⚠️ Хранение паспортных данных — только по вашему желанию. Не делитесь ботом с посторонними.",
        "vlt_passport_title_prompt": "Название (например «Загранпаспорт»):",
        "vlt_passport_body_prompt": "Данные паспорта (серия, номер, срок — или «-»):",
        "vlt_file_hint": "📎 Отправьте фото или файл — сохранится автоматически.\n👆 Нажмите 📎 в списке, чтобы открыть файл.",
        "btn_notifications": "🔔 Уведомления",
        "btn_ecosystem": "🌐 Экосистема",
        "btn_add_reminder": "➕ Напоминание",
        "eco_btn_memory": "🧠 AI-память",
        "eco_features_intro": (
            "🌐 <b>Функции экосистемы</b> — всё в одном месте:\n\n"
            "🔔 <b>Единый центр уведомлений</b> — лекарства, встречи, платежи, ТО, дни рождения\n"
            "🧠 <b>AI-память</b> — {memory} (в настройках)\n"
            "🔍 <b>Поиск по данным</b> — «Когда менял масло?», «Анализ за март»\n"
            "🎤 <b>Голосовой режим</b> — {voice} (отправьте 🎤 сообщение)\n"
            "📷 <b>Фото</b> — чеки, документы, анализы, ошибки авто\n"
            "🌐 <b>Языки</b> — русский, узбекский, английский"
        ),
        "eco_notifications_title": "🔔 <b>Единый центр уведомлений</b>",
        "eco_notifications_empty": "Ближайших событий нет. Добавьте напоминание ниже.",
        "eco_src_reminder": "Напоминание",
        "eco_src_organizer": "Органайзер",
        "eco_src_health": "Здоровье",
        "eco_src_medicine": "Лекарства",
        "eco_src_meeting": "Встреча",
        "eco_src_birthday": "День рождения",
        "eco_src_calendar": "Календарь",
        "eco_src_car_service": "ТО автомобиля",
        "eco_src_insurance": "Страховка",
        "eco_src_payment": "Платёж",
        "eco_src_utilities": "Коммуналка",
        "eco_src_credit": "Кредит",
        "eco_search_events": "События:",
        "eco_search_reminders": "Напоминания:",
        "eco_search_ai_title": "Ответ AI",
        "eco_search_ai_hint": "Ответь на вопрос пользователя по его сохранённым данным из контекста памяти. Если данных мало — скажи честно.",
        "eco_voice_mode_hint": "🎤 Голосовой режим включён — можно продолжать общаться голосом.",
        "gen_ai_hint": "Напишите вопрос или нажмите «Спросить AI».",
        "ntf_module_intro": (
            "🔔 <b>Уведомления</b>\n\n"
            "Единый центр: лекарства, ТО, коммуналка, кредиты — из разделов.\n"
            "Здесь добавляйте фильмы, события, доставки, подписки, визы и своё."
        ),
        "ntf_sub_hint": "Добавьте напоминание или перейдите в раздел для настройки.",
        "ntf_add": "➕ Добавить",
        "ntf_open_module": "↗️ Открыть раздел",
        "ntf_empty": "Пока пусто.",
        "ntf_title_prompt": "Название (Netflix, виза США…):",
        "ntf_title_short": "Слишком короткое название.",
        "ntf_due_prompt": "Дата окончания (ДД.ММ.ГГГГ):",
        "ntf_due_error": "Не удалось разобрать дату.",
        "ntf_amount_prompt": "Сумма подписки (или «-» без суммы):",
        "ntf_amount_error": "Введите число или «-».",
        "ntf_saved": "✅ Сохранено. Напомню в нужное время.",
        "ntf_add_only_data": "Добавление доступно для подписок и виз.",
        "eco_src_subscription": "Подписка",
        "eco_src_visa": "Виза",
        "help_text": (
            "❓ <b>Как пользоваться Life AI</b>\n\n"
            "1️⃣ <b>Главная</b> — /menu или 🏠 «Главная»\n"
            "2️⃣ <b>Выберите тему</b> — Здоровье, Финансы, Авто и др.\n"
            "3️⃣ <b>Задайте вопрос</b> — просто напишите текст (кнопка не обязательна)\n"
            "4️⃣ <b>Сохранить заметку</b> — кнопка ➕ в разделе\n"
            "5️⃣ <b>Найти запись</b> — ⚙️ Настройки → 🔍 Поиск"
        ),
        "mod_hint_health": "Симптомы, анализы, лекарства, визиты к врачу и мед. документы.",
        "mod_example_health": "«что значит повышенный гемоглобин»",
        "mod_hint_car": "ТО, масло, ошибки на панели, страховка и расходы на авто.",
        "mod_example_car": "«когда менять масло на 100 000 км»",
        "mod_hint_finance": "Доходы, расходы, бюджет, цели и оплата счетов.",
        "mod_example_finance": "«как составить семейный бюджет»",
        "mod_hint_business": "Бизнес-планы, реклама, договоры, клиенты и продажи.",
        "mod_example_business": "«план открытия кофейни»",
        "mod_hint_legal": "Юридические вопросы, документы, заявления и законы.",
        "mod_example_legal": "«какие документы нужны для аренды квартиры»",
        "mod_hint_travel": "Маршруты, визы, бюджет поездки и чек-лист вещей.",
        "mod_example_travel": "«маршрут на 5 дней в Стамбул»",
        "mod_hint_home": "Коммуналка, ремонт, покупки для дома и инвентарь.",
        "mod_example_home": "«чек-лист перед ремонтом ванной»",
        "mod_hint_shopping": "Сравнение товаров, характеристики и советы по выбору.",
        "mod_example_shopping": "«что лучше — iPhone или Samsung для фото»",
        "mod_hint_education": "Объяснение тем, экзамены, языки и домашние задания.",
        "mod_example_education": "«объясни теорему Пифагора простыми словами»",
        "mod_hint_nutrition": "Рацион, калории, рецепты и список продуктов.",
        "mod_example_nutrition": "«меню на 1800 ккал без глютена»",
        "mod_hint_fitness": "Планы тренировок и отслеживание прогресса.",
        "mod_example_fitness": "«программа на 3 дня для дома без тренажёров»",
        "mod_hint_organizer": "Задачи, календарь, напоминания, встречи и заметки.",
        "mod_example_organizer": "«напомни оплатить интернет 1 числа»",
        "mod_hint_ai_assistant": "Любые вопросы, переводы, тексты, фото и документы.",
        "mod_example_ai_assistant": "«переведи на английский: доброе утро»",
        "mod_hint_vault": "Документы, паспорт, полисы, гарантии и чеки.",
        "mod_example_vault": "«куда сохранить скан паспорта»",
        "onb_welcome": (
            "👋 <b>Добро пожаловать в Life AI!</b>\n\n"
            "<b>Как пользоваться:</b>\n"
            "1️⃣ Выберите тему (Здоровье, Финансы, Авто…)\n"
            "2️⃣ Напишите вопрос текстом — AI ответит по теме\n"
            "3️⃣ «Сохранить заметку» — записать анализ, расход, напоминание\n\n"
            "🔍 Поиск и ⚙️ Настройки — внизу главного экрана.\n"
            "❓ Справка: /help"
        ),
        "onb_start_btn": "🚀 Начать",
        "onb_done": "✅ Готово! Можно пользоваться ботом.",
        "export_done": "📦 Экспорт ваших данных (JSON).",
        "cmd_expense_format": "Формат: /expense Название | 50000",
        "cmd_expense_saved": "✅ Расход «{title}» — {amount} UZS",
        "cmd_oil_hint": "🚗 Раздел «Авто → ТО» открыт. Напишите, когда меняли масло, или добавьте через меню.",
        "vlt_delete_confirm": "🗑 Удалить эту запись? Это действие нельзя отменить.",
        "vlt_file_expired": "⚠️ Файл недоступен (Telegram хранит файлы ограниченное время). Загрузите снова.",
        "vlt_confirm_yes": "✅ Да, удалить",
    },
    "uz": {
        "welcome": (
            "🧠 <b>Life AI Ecosystem</b>\n\n"
            "Hayotingizda shaxsiy yordamchi: salomatlik, avto, moliya, huquq va boshqalar.\n\n"
            "<b>Qanday foydalanish:</b>\n"
            "1. Mavzuni tanlang (masalan ⚖️ Yuridik yordam yoki 🏥 Salomatlik)\n"
            "2. Savol yozing — AI <b>faqat shu mavzuda</b> javob beradi\n"
            "3. Yozuvlar va eslatmalarni shu bo'limda saqlang\n\n"
            "🧠 AI xotira · 🔍 Qidiruv · 📊 Panel · 🔔 Eslatmalar"
        ),
        "choose_language": "🌐 Interfeys tilini tanlang:",
        "start_pick_language": "👋 <b>Life AI ga xush kelibsiz!</b>\n\n🌐 Tilni tanlang:",
        "language_changed": "✅ Til o'zgartirildi: {label}",
        "main_menu": (
            "🧠 <b>Life AI</b>\n\n"
            "Nima qilishni tanlang.\n\n"
            "💡 <b>Savol yozing</b> — tugma shart emas."
        ),
        "btn_all_by_category": "📂 Barcha bo'limlar",
        "btn_open_menu": "🚀 Menyuni ochish",
        "btn_help": "❓ Yordam",
        "btn_search_record": "🔍 Yozuvni topish",
        "btn_dashboard": "📊 Boshqaruv paneli",
        "btn_ai_assistant": "🤖 AI yordamchi",
        "btn_search": "🔍 Hayot bo'yicha qidiruv",
        "btn_calendar": "📅 Taqvim",
        "btn_family": "👨‍👩‍👧 Oila",
        "btn_voice": "🎤 Ovozli rejim",
        "btn_all_modules": "📚 Barcha bo'limlar",
        "btn_settings": "⚙️ Sozlamalar",
        "btn_language": "🌐 Til",
        "btn_back_menu": "🏠 Bosh sahifa",
        "btn_back_categories": "⬅️ Kategoriyalar",
        "btn_back_module": "⬅️ Orqaga",
        "btn_ask_ai": "💬 Savol berish",
        "btn_add_record": "➕ Eslatma saqlash",
        "btn_add_record_full": "➕ Eslatma saqlash",
        "btn_memory_on": "🧠 Xotira: ✅",
        "btn_memory_off": "🧠 Xotira: ❌",
        "btn_voice_on": "🎤 Ovoz: ✅",
        "btn_voice_off": "🎤 Ovoz: ❌",
        "btn_family_profiles": "👨‍👩‍👧 Oilaviy profillar",
        "btn_add_profile": "➕ Profil qo'shish",
        "btn_add_credit": "➕ Kredit qo'shish",
        "btn_cancel": "❌ Bekor qilish",
        "settings_title": "⚙️ <b>Sozlamalar</b>",
        "settings_memory": "🧠 AI xotira: {status}",
        "settings_voice": "🎤 Ovozli rejim: {status}",
        "settings_lang": "🌐 Til: {label}",
        "settings_commands": "/help — qisqa yo'riqnoma.",
        "settings_tip": "💡 <b>AI xotira</b> — muhim narsalarni eslab qoladi.\n🎤 <b>Ovoz</b> — javoblar ovozda ham keladi.",
        "settings_extra": "🎤 ovoz yoki 📷 rasm yuboring — avtomatik taniladi.",
        "memory_on_toast": "Xotira yoqildi",
        "memory_off_toast": "Xotira o'chirildi",
        "voice_on_toast": "Ovozli rejim yoqildi — ovozli xabar yuboring",
        "voice_off_toast": "Ovozli rejim o'chirildi",
        "dashboard_title": "📊 <b>Boshqaruv paneli</b>",
        "dashboard_body": (
            "👤 Profil: <b>{profile}</b>\n"
            "👨‍👩‍👧 Oilaviy profillar: <b>{profiles}</b>\n"
            "💳 Faol kreditlar: <b>{credits}</b>\n"
            "📝 Yozuvlar: <b>{records}</b>\n"
            "📅 Tadbirlar: <b>{events}</b>\n"
            "🔔 Eslatmalar: <b>{reminders}</b>\n"
            "🧠 AI xotira: <b>{memory}</b>\n\n"
            "💰 Daromad: <b>{income:.0f}</b> | Xarajat: <b>{expense:.0f}</b>\n"
            "📈 Balans: <b>{balance:.0f}</b>\n\n"
            "📦 Bo'limlar: <b>{modules}</b>"
        ),
        "all_modules": "📚 <b>Kategoriyalar</b> ({count})\n\nTanlang:",
        "pick_module": "📂 <b>{category}</b>\n\nNima qiziq?",
        "module_not_found": "Bo'lim topilmadi",
        "not_found": "Topilmadi",
        "module_sections": "Bo'limlar:",
        "module_more": "… yana {count} ta",
        "module_ask_here": "💬 <b>Savolni shu yerga yozing</b> — shu mavzuda javob beraman.",
        "module_example_label": "Misol:",
        "module_or_pick": "Yoki bo'lim yoki tugmani tanlang.",
        "submodule_ask": "💬 <b>«{sub}» mavzusida savol bering</b> — javob faqat shu bo'lim bo'yicha.",
        "submodule_also": "Shuningdek:\n• ➕ yozuv saqlash\n• 🔍 «Hayot bo'yicha qidiruv» orqali topish",
        "search_title": "🔍 <b>Hayot bo'yicha qidiruv</b>",
        "search_hint": "Masalan:\n• <code>yog'</code>\n• <code>qon tahlili</code>\n• <code>sug'urta</code>\n\nYozuvlar va AI xotirada qidiraman.",
        "search_enter": "Qidiruv matnini kiriting.",
        "search_results": "🔍 «<b>{query}</b>» bo'yicha natijalar",
        "search_records": "Yozuvlar:",
        "search_memory": "AI xotira:",
        "search_nothing": "Hech narsa topilmadi. Kerakli bo'limda yozuv qo'shing.",
        "family_title": "👨‍👩‍👧 <b>Oilaviy rejim</b>",
        "family_desc": "Salomatlik, taqvim va eslatmalar uchun profillar.",
        "family_active": "Faol profil: <b>{name}</b>",
        "family_switched": "Profil almashtirildi",
        "family_not_found": "Profil topilmadi",
        "family_add_name": "👤 Profil ismini kiriting (masalan: Ona, O'g'il, Xotin):",
        "family_name_short": "Ism juda qisqa.",
        "family_add_relation": "Bu kimsa?",
        "family_rel_self": "Men",
        "family_rel_spouse": "Turmush o'rtoq",
        "family_rel_child": "Farzand",
        "family_rel_parent": "Ota-ona",
        "family_rel_other": "Boshqa",
        "family_added": "✅ «{name}» profili qo'shildi.",
        "ai_thinking": "⏳ O'ylayapman…",
        "ai_module_thinking": "{emoji} «{module}» mavzusida o'ylayapman…",
        "ai_ask_module": "💬 <b>{module}</b> — savolingizni yozing:",
        "ai_assistant_title": "🤖 <b>AI yordamchi</b>",
        "ai_assistant_ask": "Har qanday savol bering:",
        "record_new": "➕ <b>Yangi yozuv</b> ({module})",
        "record_send": "Yozuv matnini yuboring.",
        "record_send_finance": "Yozuv matnini yuboring.\nKeyin summa so'raladi.",
        "record_amount": "💰 Qancha sarfladingiz? (raqam, yoki 0 — sumsiz):",
        "record_amount_error": "Raqam kiriting, masalan 150000",
        "record_saved": "✅ Yozuv saqlandi.",
        "memory_cmd": "🧠 AI xotirasiga saqlash uchun fakt yuboring:",
        "memory_saved": "✅ AI xotirasiga saqlandi.",
        "remind_format": (
            "🔔 Format:\n"
            "<code>Sarlavha | 25.06.2026 09:00</code>\n\n"
            "Yoki faqat sarlavha — sanani alohida so'raymiz."
        ),
        "remind_date_error": "Sana: KK.OO.YYYY SS:MM (masalan 25.06.2026 09:00)",
        "remind_created": "✅ Eslatma: {title} — {when}",
        "remind_datetime": "📅 Sana va vaqt: <code>25.06.2026 09:00</code>",
        "remind_default_title": "Eslatma",
        "free_text_pick_module": "<i>Aniq javob uchun mavzuni tanlang: Salomatlik, Avto, Huquq va hokazo.</i>",
        "weather_title": "🌿 <b>Ekologiya / ob-havo</b>",
        "voice_recognizing": "🎤 Taniyapman…",
        "voice_failed": "⚠️ Tanib bo'lmadi. OPENAI_API_KEY ni tekshiring.",
        "photo_analyzing": "📷 Rasm tahlil qilinmoqda (OCR/Vision)…",
        "photo_done": "📷 <b>Tanildi</b>",
        "cat_0": "Salomatlik va ovqatlanish",
        "cat_1": "Pul va biznes",
        "cat_2": "Transport va sayohat",
        "cat_3": "Uy va xaridlar",
        "cat_4": "Ta'lim",
        "cat_5": "Huquq",
        "cat_6": "Rejalashtirish",
        "cat_7": "AI va ma'lumotlar",
        "lang_reply_ru": "rus",
        "lang_reply_uz": "o'zbek",
        "lang_reply_en": "ingliz",
        "credits_my": "💳 <b>Mening kreditlarim</b>",
        "credits_title": "💳 <b>Kredit va ipoteka</b>",
        "credits_empty": "Saqlangan kreditlar yo'q.",
        "credits_empty_short": "Kreditni qo'lda qo'shing — bot har oy to'lov haqida eslatadi.",
        "credits_hint": "Qo'lda qo'shing:\n• nomi (bank/kredit)\n• kredit summasi\n• oylik to'lov\n• oy kuni (1–31)",
        "credits_notify": "<i>To'lov kuni har oy avtomatik eslatma keladi.</i>",
        "credits_new": "💳 <b>Yangi kredit</b>\n\nNomini kiriting (bank yoki kredit nomi):",
        "credits_cancelled": "Kredit qo'shish bekor qilindi.",
        "credits_title_short": "Nom juda qisqa.",
        "credits_total": "💰 <b>Umumiy kredit summasini</b> kiriting (raqam):",
        "credits_total_error": "Raqam kiriting, masalan 50000000",
        "credits_total_positive": "Summa 0 dan katta bo'lishi kerak.",
        "credits_monthly": "📅 <b>Har oylik to'lov summasini</b> kiriting:",
        "credits_monthly_error": "Raqam kiriting, masalan 1500000",
        "credits_day": "🗓 To'lov uchun <b>oy kuni</b> (1–31):\nMasalan: <code>15</code> — har oy 15-kuni eslatma.",
        "credits_day_error": "1 dan 31 gacha raqam kiriting.",
        "credits_day_range": "Raqam 1–31 oralig'ida bo'lishi kerak.",
        "credits_saved": "✅ Kredit saqlandi!\n\n{info}\n\n🔔 Eslatma har oy <b>{day}-kuni</b> keladi.",
        "credits_deleted_all": "💳 Kreditlar o'chirildi. Kerak bo'lsa yangisini qo'shing.",
        "credits_not_found": "Kredit topilmadi",
        "credits_removed": "Kredit o'chirildi",
        "credits_line": (
            "• <b>{title}</b>\n"
            "  Summa: {total}\n"
            "  Qoldiq: <b>{remaining}</b>\n"
            "  Oylik to'lov: {monthly}\n"
            "  To'lov kuni: oyning <b>{day}</b>-kuni"
        ),
        "credits_reminder": (
            "💳 <b>To'lov eslatmasi</b>\n\n"
            "🏦 {title}\n"
            "💰 To'lov: <b>{monthly}</b>\n"
            "📋 Qoldiq: <b>{remaining}</b>\n"
            "📅 Bugun oyning <b>{day}</b>-kuni — to'lovni unutmang.\n\n"
            "«To'lovni yozish» — qoldiqni qayta hisoblayman."
        ),
        "credits_btn_log_payment": "✅ To'lovni yozish",
        "credits_payment_prompt": "💳 <b>{title}</b>\n\nQancha to'ladingiz? (masalan {monthly})",
        "credits_payment_saved": "✅ Yozildi: {paid}\nQoldiq: <b>{remaining}</b>",
        "credits_paid_off": "🎉 «{title}» krediti to'liq yopildi!",
        "default_loan_title": "Kredit",
        "doc_saved": "📄 «{name}» hujjati saqlandi.\nPDF uchun sahifa rasmini yuboring.",
        "link_check": "🛡 <b>Havola tekshiruvi</b>",
        "link_risk": "Xavf: {risk}",
        "photo_title_default": "Rasm",
        "health_module_intro": (
            "🩺 <b>Salomatlik</b> — tibbiy yordamchingiz:\n\n"
            "• Alomatlar, tahlillar va tekshiruvlar bo'yicha AI\n"
            "• Dori-darmonlar va o'zaro ta'sir\n"
            "• Qabul va shifokor tashriflari eslatmalari\n"
            "• Bosim, qon shakar, vazn jurnali\n"
            "• Tibbiy hujjatlar saqlash"
        ),
        "health_ai_hint": "💬 Savol yozing — AI shu mavzuda javob beradi.",
        "health_sub_consultant": "Alomatlar bo'yicha AI maslahatchi.",
        "health_sub_symptoms": "Alomatlar: nima anglash mumkin va qachon shifokorga.",
        "health_sub_tests": "Tahlil natijalarini sodda tilda tushuntirish.",
        "health_sub_exams": "Tekshiruv natijalarini tushuntirish (UZI, MRT va boshqalar).",
        "health_sub_medicines": "Dori-darmonlar, dozalar va o'zaro ta'sir.",
        "health_sub_diary": "Bosim, qon shakar, vazn va boshqa ko'rsatkichlar jurnali.",
        "health_sub_med_reminders": "Dori qabul qilish bo'yicha kunlik eslatmalar.",
        "health_sub_visits": "Shifokor tashriflari eslatmalari.",
        "health_sub_documents": "Tahlillar, ma'lumotnomalar va tibbiy hujjatlar.",
        "health_metric_pressure": "Bosim",
        "health_metric_sugar": "Qon shakari",
        "health_metric_weight": "Vazn",
        "health_metric_other": "Ko'rsatkich",
        "health_diary_title": "📋 <b>Ko'rsatkichlar jurnali</b>",
        "health_diary_empty": "Yozuvlar yo'q. Birinchi o'lchovni qo'shing.",
        "health_diary_recent": "<b>So'nggi yozuvlar:</b>",
        "health_add_pressure": "➕ Bosim",
        "health_add_sugar": "➕ Qon shakari",
        "health_add_weight": "➕ Vazn",
        "health_view_all": "📊 Barcha tarix",
        "health_enter_pressure": "Bosimni kiriting: <code>120/80</code>",
        "health_enter_sugar": "Qon shakarini kiriting (mmol/l), masalan <code>5.6</code>:",
        "health_enter_weight": "Vaznni kiriting (kg), masalan <code>75</code>:",
        "health_enter_notes": "Izoh (yoki <code>-</code> o'tkazish uchun):",
        "health_metric_saved": "✅ Jurnalga saqlandi.",
        "health_invalid_pressure": "Format: 120/80",
        "health_invalid_value": "Raqam kiriting.",
        "health_med_title": "💊 <b>Dori qabul qilish</b>",
        "health_med_empty": "Faol dorilar yo'q.",
        "health_med_hint_multi": "Bir nechta dori qo'shish mumkin. O'zgartirish yoki o'chirish uchun doriga bosing.",
        "health_med_count": "Faol dorilar: <b>{count}</b>",
        "health_med_add": "➕ Dori qo'shish",
        "health_med_name": "Dori nomini kiriting:",
        "health_med_dosage": "Doza (masalan: 1 tabletka):",
        "health_med_times": "Qabul vaqti vergul bilan:\n<code>08:00, 20:00</code>",
        "health_med_times_error": "Vaqt HH:MM formatida, masalan 08:00, 20:00",
        "health_med_saved": "✅ Dori qo'shildi. Eslatmalar belgilangan vaqtda keladi.",
        "health_med_removed": "Dori o'chirildi",
        "health_med_not_found": "Topilmadi",
        "health_med_dose": "Doza",
        "health_med_reminder_title": "Dori qabul qilish vaqti",
        "health_med_edit_name": "✏️ Nomi",
        "health_med_edit_dose": "✏️ Doza",
        "health_med_edit_times": "✏️ Vaqt",
        "health_med_delete": "🗑 O'chirish",
        "health_med_back_list": "⬅️ Ro'yxatga",
        "health_med_updated": "✅ O'zgarishlar saqlandi",
        "health_med_edit_name_prompt": "Yangi dori nomi:",
        "health_med_edit_dose_prompt": "Yangi doza:",
        "health_med_edit_times_prompt": "Yangi qabul vaqti:\n<code>08:00, 20:00</code>",
        "health_visit_title": "🩺 <b>Shifokor tashriflari</b>",
        "health_visit_empty": "Kelgusi tashriflar yo'q.",
        "health_visit_add": "➕ Tashrif qo'shish",
        "health_visit_name": "Mutaxassis (masalan: terapevt):",
        "health_visit_datetime": "Sana va vaqt: <code>25.06.2026 10:00</code>",
        "health_visit_saved": "✅ Tashrif eslatmasi yaratildi.",
        "health_doc_title": "📁 <b>Tibbiy hujjatlar</b>",
        "health_doc_empty": "Hujjatlar yo'q.",
        "health_doc_hint": "📷 rasm yoki tahlil matnini yuboring — tibbiy kartaga saqlaymiz.",
        "health_doc_add": "➕ Matnli yozuv",
        "health_doc_saved": "✅ Hujjat saqlandi.",
        "car_module_intro": (
            "🚗 <b>Avtomobil</b> — haydovchi yordamchisi:\n\n"
            "• Panel rasmi bo'yicha xatolarni tushuntirish\n"
            "• Ovozlar va nosozliklar tahlili\n"
            "• TO jadvali va eslatmalar (yog', filtr, shina)\n"
            "• Sug'urta va texko'rik\n"
            "• Avto xarajatlari"
        ),
        "car_ai_hint": "💬 Savol yozing yoki 📷/🎤 yuboring",
        "car_sub_panel_photo": "Panel rasmini yuboring — AI xatolarni tushuntiradi.",
        "car_sub_sounds": "Ovozni yozing yoki 🎤 yuboring — AI sabablarni aytadi.",
        "car_sub_service": "Texnik xizmat jadvali.",
        "car_sub_reminders": "Yog', filtr va shina almashtirish eslatmalari.",
        "car_sub_compliance": "Sug'urta va texko'rik muddatlari.",
        "car_sub_expenses": "Yoqilg'i, ta'mir, yuvish va boshqa xarajatlar.",
        "car_panel_hint": "📷 <b>Panel rasmini</b> yuboring.\n\nAI xatolarni tushuntiradi.",
        "car_sounds_hint": "Ovozni matn yoki 🎤 ovozli xabar bilan tasvirlang.",
        "car_service_title": "🔧 <b>TO jadvali</b>",
        "car_service_empty": "Rejalar yo'q. Birinchisini qo'shing.",
        "car_service_hint": "Yaqinlashayotgan ishlar:",
        "car_service_add": "➕ Jadvalga qo'shish",
        "car_reminders_title": "⏰ <b>Eslatmalar</b> (yog', filtr, shina)",
        "car_reminders_empty": "Eslatmalar yo'q.",
        "car_maint_oil": "🛢 Yog'",
        "car_maint_filter": "🧰 Filtrlar",
        "car_maint_tires": "🛞 Shinalar",
        "car_maint_service": "🔧 TO",
        "car_maint_other": "📋 Boshqa",
        "car_maint_pick_type": "Ish turini tanlang:",
        "car_enter_date": "Sana:\n<code>15.07.2026</code>",
        "car_comp_enter_date": "Tugash sanasi:\n<code>31.12.2026</code>",
        "car_enter_notes": "Izoh yoki <code>-</code>",
        "car_date_error": "Format: KK.OO.YYYY",
        "car_maint_saved": "✅ TO jadvaliga qo'shildi",
        "car_comp_saved": "✅ Muddat saqlandi",
        "car_expense_saved": "✅ Xarajat yozildi",
        "car_deleted": "O'chirildi",
        "car_not_found": "Topilmadi",
        "car_back_list": "⬅️ Jadvalga",
        "car_maint_delete": "🗑 O'chirish",
        "car_comp_title": "📋 <b>Sug'urta va texko'rik</b>",
        "car_comp_empty": "Muddatlarni qo'shing.",
        "car_comp_insurance": "🛡 Sug'urta",
        "car_comp_inspection": "✅ Texko'rik",
        "car_comp_add_insurance": "➕ Sug'urta",
        "car_comp_add_inspection": "➕ Texko'rik",
        "car_expires": "Tugash",
        "car_expires_today": "bugun tugaydi",
        "car_expires_tomorrow": "ertaga tugaydi",
        "car_expires_in_days": "{days} kun qoldi",
        "car_maint_reminder_title": "Avto eslatmasi",
        "car_comp_reminder_title": "Avto muddati",
        "car_due_today": "bugun reja bo'yicha",
        "car_expenses_title": "💰 <b>Avto xarajatlari</b>",
        "car_expenses_empty": "Xarajatlar yo'q.",
        "car_expenses_total": "Jami: <b>{total}</b> UZS",
        "car_expenses_add": "➕ Xarajat qo'shish",
        "car_expense_title_prompt": "Nima to'ladingiz?",
        "car_expense_amount_prompt": "Summa (UZS):",
        "fin_module_intro": (
            "💰 <b>Moliya</b> — shaxsiy moliyaviy yordamchi:\n\n"
            "• Daromad va xarajatlarni hisobga olish\n"
            "• Moliyaviy maqsadlar va jamg'arma\n"
            "• Kategoriyalar bo'yicha byudjet\n"
            "• Hisob to'lovlari eslatmalari\n"
            "• Xarajatlar tahlili\n"
            "• Kreditlar"
        ),
        "fin_ai_hint": "💬 Moliya bo'yicha AI ga savol bering",
        "fin_sub_income": "Ish haqi, qo'shimcha daromad va boshqa tushumlarni yozing.",
        "fin_sub_expense": "Xarajatlarni kategoriyalar bilan hisobga oling.",
        "fin_sub_goals": "Maqsadlar qo'ying: telefon, ta'til, jamg'arma.",
        "fin_sub_budget": "Oy bo'yicha kategoriya limitlari.",
        "fin_sub_bills": "Kommunal, internet, obunalar — vaqtida eslatma.",
        "fin_sub_analysis": "Xarajatlar taqsimoti va oylik balans.",
        "fin_sub_loans": "Kredit va ipoteka — summa, oylik to'lov va eslatmalar.",
        "fin_income_title": "📈 <b>Daromadlar</b>",
        "fin_expense_title": "📉 <b>Xarajatlar</b>",
        "fin_total": "Jami: <b>{total}</b> UZS",
        "fin_empty": "Hozircha yozuvlar yo'q.",
        "fin_add_tx": "➕ Qo'shish",
        "fin_tx_title_prompt": "Tavsif (ish haqi, oziq-ovqat…):",
        "fin_tx_amount_prompt": "Summa (UZS):",
        "fin_tx_saved": "✅ Yozuv saqlandi",
        "fin_pick_category": "Xarajat kategoriyasini tanlang:",
        "fin_cat_food": "🍔 Ovqat",
        "fin_cat_transport": "🚗 Transport",
        "fin_cat_home": "🏠 Uy",
        "fin_cat_health": "🏥 Sog'liq",
        "fin_cat_fun": "🎬 Ko'ngilochar",
        "fin_cat_shopping": "🛒 Xaridlar",
        "fin_cat_bills": "💡 Hisoblar",
        "fin_cat_other": "📋 Boshqa",
        "fin_goals_title": "🎯 <b>Moliyaviy maqsadlar</b>",
        "fin_goals_empty": "Hozircha maqsadlar yo'q.",
        "fin_goal_add": "➕ Yangi maqsad",
        "fin_goal_title_prompt": "Maqsad nomi (masalan: ta'til):",
        "fin_goal_target_prompt": "Maqsadli summa (UZS):",
        "fin_goal_current_prompt": "Allaqachon yig'ilgan (UZS) yoki 0:",
        "fin_goal_saved": "✅ Maqsad qo'shildi",
        "fin_goal_updated": "✅ Jarayon yangilandi",
        "fin_goal_update": "📊 Jarayonni yangilash",
        "fin_goal_delete": "🗑 O'chirish",
        "fin_goal_update_prompt": "Qancha yig'ilgan (UZS):",
        "fin_back_goals": "⬅️ Maqsadlarga",
        "fin_goal_default": "Maqsad",
        "fin_budget_title": "📊 <b>Oylik byudjet</b>",
        "fin_budget_month": "Oy: <b>{month}</b>",
        "fin_budget_empty": "Limitlar belgilanmagan. Quyidan kategoriya tanlang.",
        "fin_budget_hint": "Kategoriyani bosing — oy uchun limit belgilang.",
        "fin_budget_limit_prompt": "«{category}» uchun limit (UZS):",
        "fin_budget_saved": "✅ Limit saqlandi",
        "fin_bills_title": "💳 <b>Hisob to'lovlari</b>",
        "fin_bills_empty": "Hisoblar yo'q. Birinchisini qo'shing.",
        "fin_bill_add": "➕ Hisob qo'shish",
        "fin_bill_title_prompt": "Nomi (kommunal, internet…):",
        "fin_bill_amount_prompt": "Summa (UZS):",
        "fin_bill_date_prompt": "To'lov sanasi:\n<code>05.07.2026</code>",
        "fin_bill_saved": "✅ Hisob qo'shildi — to'lov kunida eslatamiz",
        "fin_bill_delete": "🗑 O'chirish",
        "fin_bill_default": "Hisob",
        "fin_back_bills": "⬅️ Hisoblarga",
        "fin_back_loans": "⬅️ Kreditlarga",
        "fin_loan_delete": "🗑 O'chirish",
        "fin_bill_reminder_title": "To'lov eslatmasi",
        "fin_due_today": "bugun to'lash kerak",
        "fin_bill_pay": "to'lash",
        "fin_analysis_title": "📊 <b>Xarajatlar tahlili</b>",
        "fin_analysis_summary": "{month}: daromad <b>{income}</b> | xarajat <b>{expense}</b> | balans <b>{balance}</b> UZS",
        "fin_analysis_by_cat": "<b>Kategoriyalar bo'yicha:</b>",
        "fin_not_found": "Topilmadi",
        "fin_deleted": "O'chirildi",
        "biz_module_intro": (
            "💼 <b>Biznes</b> — tadbirkor uchun AI yordamchi:\n\n"
            "• Ishga tushirish va rivojlantirish bo'yicha AI maslahatchi\n"
            "• Biznes-rejalar va strategiya\n"
            "• Reklama va kreativlar yaratish\n"
            "• Raqobatchilar tahlili\n"
            "• Shartnoma qoralamalari\n"
            "• Mijozlarga javoblar\n"
            "• Savdo tahlili"
        ),
        "biz_ai_hint": "💬 Vazifani yozing yoki «AI ga so'rash» tugmasini bosing",
        "biz_sub_consultant": "Nisha, model, savdo kanallari va xavflar bo'yicha maslahatlar.",
        "biz_sub_plans": "Tuzilgan biznes-rejalar: bozor, mahsulot, moliya, bosqichlar.",
        "biz_sub_ads": "Reklama matnlari, sarlavhalar, postlar va e'lonlar.",
        "biz_sub_competitors": "Raqobatchilar tahlili: kuchli tomonlar, narxlar, pozitsiya.",
        "biz_sub_contracts": "Shartnoma qoralamalari — imzolashdan oldin yurist tekshirsin.",
        "biz_sub_client_responses": "Mijozlarga professional javoblar: shikoyatlar, savollar, savdo.",
        "biz_sub_sales_analysis": "Savdo tahlili: trendlar, voronka, tavsiyalar.",
        "leg_module_intro": (
            "⚖️ <b>Yuridik yordam</b> — huquqiy savollar bo'yicha AI yordamchi:\n\n"
            "• Yuridik savollarga javoblar\n"
            "• Hujjatlarni tekshirish (matn yoki foto)\n"
            "• Ariza va murojaatlar yaratish\n"
            "• Qonunlar tushuntirishi\n"
            "• Turli vaziyatlarda harakatlar ro'yxati\n\n"
            "⚠️ Yurist o'rnini bosmaydi — umumiy ma'lumot va qoralamalar."
        ),
        "leg_ai_hint": "💬 Vaziyatni yozing yoki «AI ga so'rash» tugmasini bosing",
        "leg_sub_questions": "Huquq va majburiyatlar, muddatlar va tartib haqida javoblar.",
        "leg_sub_doc_check": "Shartnoma va hujjatlarni tekshirish — matn yoki foto yuboring.",
        "leg_sub_applications": "Davlat organlari, sud, ish beruvchiga ariza qoralamalari.",
        "leg_sub_legislation": "Qonunlarni sodda tilda tushuntirish.",
        "leg_sub_checklists": "Qadam-baqadam harakatlar: hujjatlar, muddatlar, qayerga murojaat.",
        "trv_module_intro": (
            "✈️ <b>Sayohat</b> — sayohatchi yordamchisi:\n\n"
            "• Marshrut rejalash\n"
            "• Viza ma'lumoti\n"
            "• Sayohat byudjeti\n"
            "• Narsalar ro'yxati\n"
            "• Tarjimon\n"
            "• Valyuta konvertori (ma'lumot kurslari)"
        ),
        "trv_ai_hint": "💬 Sayohatni yozing yoki «AI ga so'rash» tugmasini bosing",
        "trv_sub_routes": "Kunlar bo'yicha marshrut: shaharlar, transport, diqqatga sazovor joylar.",
        "trv_sub_visas": "Viza haqida ma'lumot: kerakmi, hujjatlar, muddatlar — konsullik saytini tekshiring.",
        "trv_sub_budget": "Byudjet: parvoz, turar joy, ovqat, transport, dam olish, zaxira.",
        "trv_sub_packing": "Iqlim va muddatga qarab narsalar ro'yxati.",
        "trv_sub_translator": "Aeroport, mehmonxona, restoran uchun tarjima va foydali iboralar.",
        "trv_sub_currency": "Valyuta konvertori va almashtirish maslahatlari. Kurslar ma'lumot uchun.",
        "trv_fx_convert": "💱 Konvertatsiya",
        "trv_fx_amount_prompt": "Konvertatsiya summasi:",
        "trv_fx_from_prompt": "Qaysi valyutadan:",
        "trv_fx_to_prompt": "Qaysi valyutaga:",
        "trv_fx_result": "💱 <b>{amount}</b> = <b>{result}</b>",
        "trv_fx_disclaimer": "Ma'lumot kursi, moliyaviy operatsiyalar uchun emas.",
        "trv_fx_error": "Konvertatsiya amalga oshmadi",
        "home_module_intro": (
            "🏠 <b>Uy</b> — uy-ro'zg'or yordamchisi:\n\n"
            "• Kommunal to'lov eslatmalari\n"
            "• Uy xarajatlari\n"
            "• Ta'mirlash rejasi\n"
            "• Xaridlar ro'yxati\n"
            "• Uy inventari"
        ),
        "home_sub_utilities": "Elektr, gaz, suv, internet — to'lov kunida eslatamiz.",
        "home_sub_expenses": "Uy va ro'zg'or xarajatlarini yozing.",
        "home_sub_repair": "Ta'mirlash vazifalari: reja → jarayonda → tayyor.",
        "home_sub_shopping": "Xaridlar ro'yxati — sotib olinganini belgilang.",
        "home_sub_inventory": "Nima qayerda: predmet, miqdor, joy.",
        "home_utilities_title": "💡 <b>Kommunal to'lovlar</b>",
        "home_expenses_title": "💰 <b>Uy xarajatlari</b>",
        "home_repair_title": "🔨 <b>Ta'mirlash rejasi</b>",
        "home_shopping_title": "🛒 <b>Xaridlar ro'yxati</b>",
        "home_inventory_title": "📦 <b>Uy inventari</b>",
        "home_empty": "Hozircha bo'sh.",
        "home_total": "Jami: <b>{total}</b> UZS",
        "home_not_found": "Topilmadi",
        "home_deleted": "O'chirildi",
        "home_delete": "🗑 O'chirish",
        "home_utility_add": "➕ Hisob qo'shish",
        "home_utility_title_prompt": "Xizmat (elektr, gaz, internet…):",
        "home_utility_amount_prompt": "Summa (UZS):",
        "home_utility_date_prompt": "To'lov sanasi:\n<code>05.07.2026</code>",
        "home_utility_saved": "✅ Hisob qo'shildi — to'lov kunida eslatamiz",
        "home_utility_default": "Kommunal",
        "home_utility_reminder_title": "Kommunal to'lov",
        "home_due_today": "bugun to'lash kerak",
        "home_back_utilities": "⬅️ Hisoblarga",
        "home_expense_add": "➕ Xarajat qo'shish",
        "home_expense_title_prompt": "Nimaga sarflandi:",
        "home_expense_amount_prompt": "Summa (UZS):",
        "home_expense_saved": "✅ Xarajat saqlandi",
        "home_expense_default": "Xarajat",
        "home_repair_add": "➕ Vazifa qo'shish",
        "home_repair_title_prompt": "Nima qilish kerak:",
        "home_repair_notes_prompt": "Eslatmalar (yoki «-» o'tkazib yuborish):",
        "home_repair_saved": "✅ Vazifa qo'shildi",
        "home_repair_default": "Ta'mirlash",
        "home_repair_planned": "rejalashtirilgan",
        "home_repair_in_progress": "jarayonda",
        "home_repair_done": "tayyor",
        "home_repair_cycle": "🔄 Holatni o'zgartirish",
        "home_repair_updated": "Holat yangilandi",
        "home_back_repair": "⬅️ Ta'mirlashga",
        "home_shopping_add": "➕ Qo'shish",
        "home_shopping_title_prompt": "Nima sotib olish:",
        "home_shopping_saved": "✅ Ro'yxatga qo'shildi",
        "home_inventory_add": "➕ Predmet qo'shish",
        "home_inventory_title_prompt": "Predmet nomi:",
        "home_inventory_location_prompt": "Qayerda turadi (yoki «-»):",
        "home_inventory_qty_prompt": "Miqdor:",
        "home_inventory_saved": "✅ Inventarga qo'shildi",
        "home_inventory_default": "Predmet",
        "home_inv_no_location": "joy ko'rsatilmagan",
        "home_back_inventory": "⬅️ Inventarga",
        "shop_module_intro": (
            "🛒 <b>Xaridlar</b> — mahsulot tanlashda AI yordamchi:\n\n"
            "• Mahsulotlarni solishtirish\n"
            "• Foydali takliflarni topish\n"
            "• Xususiyatlarni tekshirish\n"
            "• Tanlov bo'yicha maslahatlar"
        ),
        "shop_ai_hint": "💬 Mahsulot yoki vazifani yozing yoki «AI ga so'rash» tugmasini bosing",
        "shop_sub_compare": "Modellarni narx, funksiya, afzallik va kamchilik bo'yicha solishtirish.",
        "shop_sub_deals": "Foydali takliflarni qanday topish va haqiqiy chegirmani ajratish.",
        "shop_sub_specs": "Xususiyatlar tushuntirishi — parametrlar nimani anglatadi.",
        "shop_sub_advice": "Byudjet va vazifalaringizga mos tavsiyalar.",
        "edu_module_intro": (
            "📚 <b>Ta'lim</b> — AI repetitor:\n\n"
            "• O'quv mavzularini tushuntirish\n"
            "• Imtihonlarga tayyorgarlik\n"
            "• Tillarni o'rganish\n"
            "• Konspekt yaratish\n"
            "• Uy vazifasini tekshirish"
        ),
        "edu_ai_hint": "💬 Savol bering yoki «AI ga so'rash» tugmasini bosing",
        "edu_sub_topics": "Har qanday mavzu sodda tilda: ta'riflar, misollar, o'xshatishlar.",
        "edu_sub_exams": "Tayyorgarlik rejasi, asosiy savollar, imtihon oldidan takrorlash.",
        "edu_sub_languages": "Grammatika, so'zlar, dialoglar va xatolarni tuzatish.",
        "edu_sub_notes": "Mavzu yoki ma'ruza bo'yicha tuzilgan konspektlar.",
        "edu_sub_homework": "Xatolarni tushuntirish bilan tekshirish — tayyor javob emas.",
        "nut_module_intro": (
            "🥗 <b>Ovqatlanish</b> — sog'lom ovqatlanish yordamchisi:\n\n"
            "• Ratsion tanlash\n"
            "• Kaloriya hisoblash\n"
            "• Retseptlar\n"
            "• Mahsulotlar ro'yxati\n"
            "• Suv hisobi"
        ),
        "nut_ai_hint": "💬 Maqsadingizni yozing yoki «AI ga so'rash» tugmasini bosing",
        "nut_sub_diet": "Maqsad va afzalliklaringizga mos muvozanatli ratsion.",
        "nut_sub_calories": "Taom kaloriyasi va kunlik norma — AI yoki kalkulyator.",
        "nut_sub_recipes": "Ingredientlar va taxminiy kaloriya bilan retseptlar.",
        "nut_sub_grocery": "Do'kon uchun mahsulotlar ro'yxati — sotib olinganini belgilang.",
        "nut_sub_water": "Bugun qancha suv ichdingiz — +250/+500 ml tugmalari.",
        "nut_grocery_title": "🛒 <b>Mahsulotlar ro'yxati</b>",
        "nut_water_title": "💧 <b>Suv hisobi</b>",
        "nut_empty": "Hozircha bo'sh.",
        "nut_not_found": "Topilmadi",
        "nut_grocery_add": "➕ Qo'shish",
        "nut_grocery_title_prompt": "Nima sotib olish:",
        "nut_grocery_saved": "✅ Ro'yxatga qo'shildi",
        "nut_water_summary": "Bugun: <b>{total}</b> / {goal} ml ({pct}%)",
        "nut_water_hint": "Suv qo'shish uchun tugmani bosing.",
        "nut_water_custom": "➕ Boshqa hajm",
        "nut_water_ml_prompt": "Necha ml ichdingiz:",
        "nut_water_added": "✅ Qo'shildi",
        "nut_cal_calc": "🧮 Normani hisoblash",
        "nut_cal_weight_prompt": "Vazn (kg):",
        "nut_cal_height_prompt": "Bo'y (sm):",
        "nut_cal_age_prompt": "Yosh:",
        "nut_cal_sex_prompt": "Jins:",
        "nut_cal_male": "Erkak",
        "nut_cal_female": "Ayol",
        "nut_cal_activity_prompt": "Faollik darajasi:",
        "nut_act_sedentary": "Minimal",
        "nut_act_light": "Yengil",
        "nut_act_moderate": "O'rtacha",
        "nut_act_active": "Yuqori",
        "nut_act_very": "Juda yuqori",
        "nut_cal_result": "📊 Kunlik normangiz: <b>{kcal}</b> kkal\n\n<i>Mifflin-St Jeor formulasi bo'yicha</i>",
        "org_module_intro": (
            "📅 <b>Tashkilotchi</b> — hammasi bir joyda:\n\n"
            "• Muddatli vazifalar\n"
            "• Tadbirlar taqvimi\n"
            "• Eslatmalar\n"
            "• Tug'ilgan kunlar\n"
            "• Uchrashuvlar\n"
            "• Qaydlar"
        ),
        "org_tasks_title": "✅ <b>Vazifalar</b>",
        "org_calendar_title": "📅 <b>Taqvim</b>",
        "org_reminders_title": "🔔 <b>Eslatmalar</b>",
        "org_birthdays_title": "🎂 <b>Tug'ilgan kunlar</b>",
        "org_meetings_title": "🤝 <b>Uchrashuvlar</b>",
        "org_notes_title": "📝 <b>Qaydlar</b>",
        "org_empty": "Hozircha bo'sh.",
        "org_not_found": "Topilmadi",
        "org_add": "➕ Qo'shish",
        "org_task_add": "➕ Yangi vazifa",
        "org_task_title_prompt": "Vazifa nomi:",
        "org_task_due_prompt": "Muddat (yoki «-» muddatsiz):\n<code>25.06.2026 18:00</code>",
        "org_task_saved": "✅ Vazifa qo'shildi",
        "org_task_default": "Vazifa",
        "org_note_add": "➕ Yangi qayd",
        "org_note_title_prompt": "Qayd sarlavhasi:",
        "org_note_body_prompt": "Matn (yoki «-»):",
        "org_note_saved": "✅ Qayd saqlandi",
        "org_note_default": "Qayd",
        "org_meet_add": "➕ Uchrashuv",
        "org_bday_add": "➕ Tug'ilgan kun",
        "org_event_title_prompt": "Uchrashuv nomi:",
        "org_bday_title_prompt": "Ism (tug'ilgan kun):",
        "org_event_date_prompt": "Sana va vaqt:\n<code>25.06.2026 18:00</code>",
        "org_event_saved": "✅ Tadbir qo'shildi",
        "org_event_default": "Tadbir",
        "org_rem_add": "➕ Eslatma",
        "org_rem_title_prompt": "Eslatma matni:",
        "org_rem_date_prompt": "Qachon eslatish:\n<code>25.06.2026 09:00</code>",
        "org_rem_saved": "✅ Eslatma: {title} — {when}",
        "org_rem_default": "Eslatma",
        "org_date_error": "Format: KK.OO.YYYY SS:MM",
        "ast_module_intro": (
            "🤖 <b>AI yordamchi</b> — hammasi bir joyda:\n\n"
            "• Har qanday savollarga javob\n"
            "• Matn tarjimasi\n"
            "• PDF va hujjatlar\n"
            "• Foto tahlil\n"
            "• Matn yaratish\n"
            "• Rasm generatsiyasi (DALL-E)\n"
            "• Dasturlash yordami"
        ),
        "ast_ai_hint": "Xabar yozing yoki «AI dan so'rash» tugmasini bosing.",
        "ast_sub_questions": "Har qanday savollar — faktlar, maslahatlar, tushuntirishlar.",
        "ast_sub_translate": "Tillarni tarjima qilish — ma'no va uslub saqlanadi.",
        "ast_sub_documents": "PDF va hujjatlar: qisqacha mazmun, asosiy punktlar.",
        "ast_sub_photo": "Foto yuboring — AI obyekt, matn va kontekstni tahlil qiladi.",
        "ast_sub_writing": "Maqola, post, xat, rezyume — matn yaratish va tahrirlash.",
        "ast_sub_images": "Rasmni matn bilan tasvirlang — AI generatsiya qiladi.",
        "ast_sub_code": "Kod, debug, algoritmlar, arxitektura — dasturchi yordami.",
        "ast_send_photo": "📷 Tahlil uchun foto yuboring.",
        "ast_send_image_prompt": "✏️ Rasmni bir xabar bilan tasvirlang.",
        "ast_send_document": "📎 PDF yoki hujjat yuboring, keyin savol bering.",
        "ast_image_generating": "🎨 Rasm yaratilmoqda…",
        "ast_image_failed": "⚠️ Rasm yaratib bo'lmadi. OPENAI_API_KEY yoki so'rovni tekshiring.",
        "ast_image_done": "🎨 {prompt}",
        "ast_doc_saved": "📎 «{name}» hujjati saqlandi.",
        "ast_doc_caption_note": "Hujjat bo'yicha savol yozing — AI yordam beradi.",
        "vlt_module_intro": (
            "🔐 <b>Shaxsiy ombor</b> — ma'lumotlaringiz bir joyda:\n\n"
            "• Hujjatlar\n"
            "• Pasport ma'lumotlari (ixtiyoriy)\n"
            "• Polislar\n"
            "• Kafolat talonlari\n"
            "• Cheklar\n"
            "• Muhim qaydlar\n\n"
            "<i>Ma'lumotlar faqat botda saqlanadi.</i>"
        ),
        "vlt_documents_title": "📄 <b>Hujjatlar</b>",
        "vlt_passport_title": "🛂 <b>Pasport ma'lumotlari</b>",
        "vlt_policies_title": "📋 <b>Polislar</b>",
        "vlt_warranty_title": "🧾 <b>Kafolat talonlari</b>",
        "vlt_receipts_title": "🧾 <b>Cheklar</b>",
        "vlt_notes_title": "📝 <b>Muhim qaydlar</b>",
        "vlt_empty": "Hozircha bo'sh.",
        "vlt_add": "➕ Qo'shish",
        "vlt_not_found": "Topilmadi",
        "vlt_deleted": "O'chirildi",
        "vlt_saved": "✅ Saqlandi",
        "vlt_default_title": "Yozuv",
        "vlt_title_prompt": "Yozuv nomi:",
        "vlt_body_prompt": "Tavsif yoki tafsilotlar (yoki «-»):",
        "vlt_amount_prompt": "Chek summasi (yoki «-»):",
        "vlt_amount_error": "Raqam yoki «-» kiriting",
        "vlt_passport_hint": "⚠️ Pasport ma'lumotlarini saqlash — faqat sizning xohishingiz bilan. Botni begonalar bilan ulashmang.",
        "vlt_passport_title_prompt": "Nomi (masalan «Xorijiy pasport»):",
        "vlt_passport_body_prompt": "Pasport ma'lumotlari (seriya, raqam, muddat — yoki «-»):",
        "vlt_file_hint": "📎 Foto yoki fayl yuboring — saqlanadi.\n👆 Ro'yxatdagi 📎 tugmasini bosing.",
        "btn_notifications": "🔔 Bildirishnomalar",
        "btn_ecosystem": "🌐 Ekotizim",
        "btn_add_reminder": "➕ Eslatma",
        "eco_btn_memory": "🧠 AI xotira",
        "eco_features_intro": (
            "🌐 <b>Ekotizim funksiyalari</b> — hammasi bir joyda:\n\n"
            "🔔 <b>Bildirishnomalar markazi</b> — dori, uchrashuv, to'lov, TO, tug'ilgan kunlar\n"
            "🧠 <b>AI xotira</b> — {memory}\n"
            "🔍 <b>Qidiruv</b> — «Qachon yog' almashtirdim?»\n"
            "🎤 <b>Ovozli rejim</b> — {voice}\n"
            "📷 <b>Foto</b> — cheklar, hujjatlar, tahlillar\n"
            "🌐 <b>Tillar</b> — rus, o'zbek, ingliz"
        ),
        "eco_notifications_title": "🔔 <b>Bildirishnomalar markazi</b>",
        "eco_notifications_empty": "Yaqin voqealar yo'q. Quyida eslatma qo'shing.",
        "eco_src_reminder": "Eslatma",
        "eco_src_organizer": "Tashkilotchi",
        "eco_src_health": "Salomatlik",
        "eco_src_medicine": "Dori-darmon",
        "eco_src_meeting": "Uchrashuv",
        "eco_src_birthday": "Tug'ilgan kun",
        "eco_src_calendar": "Taqvim",
        "eco_src_car_service": "Avto TO",
        "eco_src_insurance": "Sug'urta",
        "eco_src_payment": "To'lov",
        "eco_src_utilities": "Kommunal",
        "eco_src_credit": "Kredit",
        "eco_search_events": "Tadbirlar:",
        "eco_search_reminders": "Eslatmalar:",
        "eco_search_ai_title": "AI javobi",
        "eco_search_ai_hint": "Foydalanuvchi savoliga saqlangan ma'lumotlar asosida javob bering.",
        "eco_voice_mode_hint": "🎤 Ovozli rejim yoqilgan — ovoz bilan davom eting.",
        "gen_ai_hint": "Savol yozing yoki «AI dan so'rash» tugmasini bosing.",
        "ntf_module_intro": (
            "🔔 <b>Bildirishnomalar</b>\n\n"
            "Dori, TO, kommunal, kredit — bo'limlardan.\n"
            "Bu yerda film, tadbir, yetkazish, obuna, viza va boshqalarni qo'shing."
        ),
        "ntf_sub_hint": "Eslatma qo'shing yoki kerakli bo'limga o'ting.",
        "ntf_add": "➕ Qo'shish",
        "ntf_open_module": "↗️ Bo'limga o'tish",
        "ntf_empty": "Hozircha bo'sh.",
        "ntf_title_prompt": "Nomi (Netflix, viza…):",
        "ntf_title_short": "Nom juda qisqa.",
        "ntf_due_prompt": "Tugash sanasi (KK.OO.YYYY):",
        "ntf_due_error": "Sanani tushunib bo'lmadi.",
        "ntf_amount_prompt": "Obuna summasi (yoki «-»):",
        "ntf_amount_error": "Raqam yoki «-» kiriting.",
        "ntf_saved": "✅ Saqlandi. Vaqtida eslataman.",
        "ntf_add_only_data": "Faqat obuna va viza uchun qo'shish.",
        "eco_src_subscription": "Obuna",
        "eco_src_visa": "Viza",
        "eco_src_visa": "Viza",
        "help_text": (
            "❓ <b>Life AI dan qanday foydalanish</b>\n\n"
            "1️⃣ <b>Bosh sahifa</b> — /menu yoki 🏠 «Bosh sahifa»\n"
            "2️⃣ <b>Mavzuni tanlang</b> — Salomatlik, Moliya, Avto…\n"
            "3️⃣ <b>Savol bering</b> — matn yozing (tugma shart emas)\n"
            "4️⃣ <b>Eslatma saqlash</b> — ➕ tugmasi\n"
            "5️⃣ <b>Topish</b> — ⚙️ Sozlamalar → 🔍 Qidiruv"
        ),
        "mod_hint_health": "Alomatlar, tahlillar, dorilar, shifokor tashriflari.",
        "mod_example_health": "«gemoglobin yuqori bo'lsa nima degani»",
        "mod_hint_car": "TO, yog', panel xatolari, sug'urta va xarajatlar.",
        "mod_example_car": "«100 ming km da yog'ni qachon almashtirish»",
        "mod_hint_finance": "Daromad, xarajat, byudjet va maqsadlar.",
        "mod_example_finance": "«oilaviy byudjet qanday tuzish»",
        "mod_hint_business": "Biznes-rejalar, reklama, shartnomalar va savdo.",
        "mod_example_business": "«qahvaxona ochish rejasi»",
        "mod_hint_legal": "Huquqiy savollar, hujjatlar va arizalar.",
        "mod_example_legal": "«ijara uchun qanday hujjatlar kerak»",
        "mod_hint_travel": "Marshrutlar, vizalar va sayohat byudjeti.",
        "mod_example_travel": "«Istanbulga 5 kunlik marshrut»",
        "mod_hint_home": "Kommunal, ta'mirlash va uy xaridlari.",
        "mod_example_home": "«hammom ta'miridan oldin ro'yxat»",
        "mod_hint_shopping": "Mahsulotlarni solishtirish va tanlov maslahati.",
        "mod_example_shopping": "«foto uchun iPhone yoki Samsung»",
        "mod_hint_education": "Mavzular, imtihonlar va uy vazifasi.",
        "mod_example_education": "«Pifagor teoremasini oddiy qilib tushuntir»",
        "mod_hint_nutrition": "Ratsion, kaloriya va retseptlar.",
        "mod_example_nutrition": "«1800 kkal glutensiz menyu»",
        "mod_hint_fitness": "Mashq rejasi va progress.",
        "mod_example_fitness": "«uyda 3 kunlik dastur»",
        "mod_hint_organizer": "Vazifalar, taqvim va eslatmalar.",
        "mod_example_organizer": "«internet to'lovini 1-sanada eslat»",
        "mod_hint_ai_assistant": "Har qanday savol, tarjima va matnlar.",
        "mod_example_ai_assistant": "«inglizchaga tarjima: xayrli tong»",
        "mod_hint_vault": "Hujjatlar, pasport, polislar va cheklar.",
        "mod_example_vault": "«pasport skanini qayerga saqlash»",
        "onb_welcome": (
            "👋 <b>Life AI ga xush kelibsiz!</b>\n\n"
            "<b>Qanday foydalanish:</b>\n"
            "1️⃣ Mavzuni tanlang (Salomatlik, Moliya, Avto…)\n"
            "2️⃣ Savol yozing — AI javob beradi\n"
            "3️⃣ «Eslatma saqlash» — tahlil, xarajat, eslatma\n\n"
            "🔍 Qidiruv va ⚙️ Sozlamalar — bosh ekranda.\n"
            "❓ /help"
        ),
        "onb_start_btn": "🚀 Boshlash",
        "onb_done": "✅ Tayyor! Foydalanish mumkin.",
        "export_done": "📦 Ma'lumotlaringiz eksporti (JSON).",
        "cmd_expense_format": "Format: /expense Nomi | 50000",
        "cmd_expense_saved": "✅ Xarajat «{title}» — {amount} UZS",
        "cmd_oil_hint": "🚗 «Avto → TO» bo'limi ochildi. Yog' almashtirish sanasini yozing yoki menyudan qo'shing.",
        "vlt_delete_confirm": "🗑 Bu yozuvni o'chirish?",
        "vlt_file_expired": "⚠️ Fayl mavjud emas (Telegram vaqtinchalik saqlaydi). Qayta yuklang.",
        "vlt_confirm_yes": "✅ Ha, o'chirish",
    },
    "en": {
        "welcome": (
            "🧠 <b>Life AI Ecosystem</b>\n\n"
            "Your personal life assistant — health, car, finance, legal, and more.\n\n"
            "<b>How to use:</b>\n"
            "1. Pick a topic (e.g. ⚖️ Legal help or 🏥 Health)\n"
            "2. Ask a question — AI answers <b>only in that topic</b>\n"
            "3. Save notes and reminders in that section\n\n"
            "🧠 AI memory · 🔍 Search · 📊 Dashboard · 🔔 Reminders"
        ),
        "choose_language": "🌐 Choose interface language:",
        "start_pick_language": "👋 <b>Welcome to Life AI!</b>\n\n🌐 Choose your language:",
        "language_changed": "✅ Language changed to {label}",
        "main_menu": (
            "🧠 <b>Life AI</b>\n\n"
            "What would you like to do?\n\n"
            "💡 <b>Type your question</b> — no button required."
        ),
        "btn_all_by_category": "📂 All sections",
        "btn_open_menu": "🚀 Open menu",
        "btn_help": "❓ Help",
        "btn_search_record": "🔍 Find record",
        "btn_dashboard": "📊 Dashboard",
        "btn_ai_assistant": "🤖 AI assistant",
        "btn_search": "🔍 Life search",
        "btn_calendar": "📅 Calendar",
        "btn_family": "👨‍👩‍👧 Family",
        "btn_voice": "🎤 Voice mode",
        "btn_all_modules": "📚 All sections",
        "btn_settings": "⚙️ Settings",
        "btn_language": "🌐 Language",
        "btn_back_menu": "🏠 Home",
        "btn_back_categories": "⬅️ Categories",
        "btn_back_module": "⬅️ Back",
        "btn_ask_ai": "💬 Ask a question",
        "btn_add_record": "➕ Save a note",
        "btn_add_record_full": "➕ Save a note",
        "btn_memory_on": "🧠 Memory: ✅",
        "btn_memory_off": "🧠 Memory: ❌",
        "btn_voice_on": "🎤 Voice: ✅",
        "btn_voice_off": "🎤 Voice: ❌",
        "btn_family_profiles": "👨‍👩‍👧 Family profiles",
        "btn_add_profile": "➕ Add profile",
        "btn_add_credit": "➕ Add loan",
        "btn_cancel": "❌ Cancel",
        "settings_title": "⚙️ <b>Settings</b>",
        "settings_memory": "🧠 AI memory: {status}",
        "settings_voice": "🎤 Voice mode: {status}",
        "settings_lang": "🌐 Language: {label}",
        "settings_commands": "/help — quick guide.",
        "settings_tip": "💡 <b>AI memory</b> — remembers important facts.\n🎤 <b>Voice</b> — replies are also sent as voice.",
        "settings_extra": "Send 🎤 voice or 📷 photo — recognition is automatic.",
        "memory_on_toast": "Memory enabled",
        "memory_off_toast": "Memory disabled",
        "voice_on_toast": "Voice mode on — send voice messages",
        "voice_off_toast": "Voice mode off",
        "dashboard_title": "📊 <b>Dashboard</b>",
        "dashboard_body": (
            "👤 Profile: <b>{profile}</b>\n"
            "👨‍👩‍👧 Family profiles: <b>{profiles}</b>\n"
            "💳 Active loans: <b>{credits}</b>\n"
            "📝 Records: <b>{records}</b>\n"
            "📅 Events: <b>{events}</b>\n"
            "🔔 Reminders: <b>{reminders}</b>\n"
            "🧠 AI memory: <b>{memory}</b>\n\n"
            "💰 Income: <b>{income:.0f}</b> | Expenses: <b>{expense:.0f}</b>\n"
            "📈 Balance: <b>{balance:.0f}</b>\n\n"
            "📦 Sections: <b>{modules}</b>"
        ),
        "all_modules": "📚 <b>Categories</b> ({count})\n\nPick one:",
        "pick_module": "📂 <b>{category}</b>\n\nWhat interests you?",
        "module_not_found": "Section not found",
        "not_found": "Not found",
        "module_sections": "Sections:",
        "module_more": "… and {count} more",
        "module_ask_here": "💬 <b>Type your question here</b> — answers stay on this topic.",
        "module_example_label": "Example:",
        "module_or_pick": "Or pick a section or button below.",
        "submodule_ask": "💬 <b>Ask about «{sub}»</b> — answers stay in this section only.",
        "submodule_also": "You can also:\n• ➕ save a record\n• 🔍 search via «Life search»",
        "search_title": "🔍 <b>Life search</b>",
        "search_hint": "Examples:\n• <code>oil change</code>\n• <code>blood test</code>\n• <code>insurance</code>\n\nSearching records and AI memory.",
        "search_enter": "Enter search text.",
        "search_results": "🔍 Results for «<b>{query}</b>»",
        "search_records": "Records:",
        "search_memory": "AI memory:",
        "search_nothing": "Nothing found. Add a record in the right section.",
        "family_title": "👨‍👩‍👧 <b>Family mode</b>",
        "family_desc": "Profiles for health records, calendar, and reminders.",
        "family_active": "Active profile: <b>{name}</b>",
        "family_switched": "Profile switched",
        "family_not_found": "Profile not found",
        "family_add_name": "👤 Enter profile name (e.g. Mom, Son, Wife):",
        "family_name_short": "Name is too short.",
        "family_add_relation": "Who is this person?",
        "family_rel_self": "Me",
        "family_rel_spouse": "Spouse",
        "family_rel_child": "Child",
        "family_rel_parent": "Parent",
        "family_rel_other": "Other",
        "family_added": "✅ Profile «{name}» added.",
        "ai_thinking": "⏳ Thinking…",
        "ai_module_thinking": "{emoji} Thinking about «{module}»…",
        "ai_ask_module": "💬 <b>{module}</b> — type your question:",
        "ai_assistant_title": "🤖 <b>AI assistant</b>",
        "ai_assistant_ask": "Ask anything:",
        "record_new": "➕ <b>New record</b> ({module})",
        "record_send": "Send record text.",
        "record_send_finance": "Send record text.\nYou will be asked for the amount next.",
        "record_amount": "💰 How much did you spend? (number, or 0 — no amount):",
        "record_amount_error": "Enter a number, e.g. 150000",
        "record_saved": "✅ Record saved.",
        "memory_cmd": "🧠 Send a fact to save to AI memory:",
        "memory_saved": "✅ Saved to AI memory.",
        "remind_format": (
            "🔔 Format:\n"
            "<code>Title | 25.06.2026 09:00</code>\n\n"
            "Or send title only — we'll ask for date."
        ),
        "remind_date_error": "Date format: DD.MM.YYYY HH:MM (e.g. 25.06.2026 09:00)",
        "remind_created": "✅ Reminder: {title} — {when}",
        "remind_datetime": "📅 Enter date and time: <code>25.06.2026 09:00</code>",
        "remind_default_title": "Reminder",
        "free_text_pick_module": "<i>For a focused answer, pick a topic: Health, Car, Legal, etc.</i>",
        "weather_title": "🌿 <b>Ecology / weather</b>",
        "voice_recognizing": "🎤 Recognizing…",
        "voice_failed": "⚠️ Could not recognize. Check OPENAI_API_KEY.",
        "photo_analyzing": "📷 Analyzing photo (OCR/Vision)…",
        "photo_done": "📷 <b>Recognized</b>",
        "cat_0": "Health & nutrition",
        "cat_1": "Money & business",
        "cat_2": "Transport & travel",
        "cat_3": "Home & shopping",
        "cat_4": "Education",
        "cat_5": "Legal",
        "cat_6": "Planning",
        "cat_7": "AI & data",
        "lang_reply_ru": "Russian",
        "lang_reply_uz": "Uzbek",
        "lang_reply_en": "English",
        "credits_my": "💳 <b>My loans</b>",
        "credits_title": "💳 <b>Loans & mortgage</b>",
        "credits_empty": "No saved loans yet.",
        "credits_empty_short": "Add a loan manually — the bot will remind you each month.",
        "credits_hint": "Add manually:\n• name (bank/loan)\n• total amount\n• monthly payment\n• day of month (1–31)",
        "credits_notify": "<i>Reminder comes automatically on payment day each month.</i>",
        "credits_new": "💳 <b>New loan</b>\n\nEnter name (bank or loan title):",
        "credits_cancelled": "Loan creation cancelled.",
        "credits_title_short": "Name is too short.",
        "credits_total": "💰 Enter <b>total loan amount</b> (number):",
        "credits_total_error": "Enter a number, e.g. 50000000",
        "credits_total_positive": "Amount must be greater than 0.",
        "credits_monthly": "📅 Enter <b>monthly payment amount</b>:",
        "credits_monthly_error": "Enter a number, e.g. 1500000",
        "credits_day": "🗓 Enter <b>day of month</b> for payment (1–31):\ne.g. <code>15</code> — reminder on the 15th each month.",
        "credits_day_error": "Enter a number from 1 to 31.",
        "credits_day_range": "Number must be between 1 and 31.",
        "credits_saved": "✅ Loan saved!\n\n{info}\n\n🔔 Reminder on the <b>{day}th</b> each month.",
        "credits_deleted_all": "💳 Loans removed. Add a new one if needed.",
        "credits_not_found": "Loan not found",
        "credits_removed": "Loan removed",
        "credits_line": (
            "• <b>{title}</b>\n"
            "  Total: {total}\n"
            "  Remaining: <b>{remaining}</b>\n"
            "  Monthly: {monthly}\n"
            "  Payment day: <b>{day}</b> of each month"
        ),
        "credits_reminder": (
            "💳 <b>Payment reminder</b>\n\n"
            "🏦 {title}\n"
            "💰 Payment: <b>{monthly}</b>\n"
            "📋 Remaining: <b>{remaining}</b>\n"
            "📅 Today is the <b>{day}th</b> — don't forget to pay.\n\n"
            "Tap «Log payment» to update the balance."
        ),
        "credits_btn_log_payment": "✅ Log payment",
        "credits_payment_prompt": "💳 <b>{title}</b>\n\nHow much did you pay? (e.g. {monthly})",
        "credits_payment_saved": "✅ Logged: {paid}\nRemaining: <b>{remaining}</b>",
        "credits_paid_off": "🎉 Loan «{title}» is fully paid off!",
        "default_loan_title": "Loan",
        "doc_saved": "📄 Document «{name}» saved.\nFor PDF, send a screenshot or photo of the page.",
        "link_check": "🛡 <b>Link check</b>",
        "link_risk": "Risk: {risk}",
        "photo_title_default": "Photo",
        "health_module_intro": (
            "🩺 <b>Health</b> — your medical assistant:\n\n"
            "• AI for symptoms, lab tests & examinations\n"
            "• Medications & interactions\n"
            "• Med intake & doctor visit reminders\n"
            "• BP, sugar, weight diary\n"
            "• Medical document storage"
        ),
        "health_ai_hint": "💬 Type your question — AI answers in this topic.",
        "health_sub_consultant": "AI consultant for symptoms.",
        "health_sub_symptoms": "Symptom review: possible causes and when to see a doctor.",
        "health_sub_tests": "Plain-language lab test explanations.",
        "health_sub_exams": "Examination results (ultrasound, MRI, X-ray, etc.).",
        "health_sub_medicines": "Drug info, dosing, and interactions.",
        "health_sub_diary": "Diary for blood pressure, sugar, weight & more.",
        "health_sub_med_reminders": "Daily medication intake reminders.",
        "health_sub_visits": "Doctor visit reminders.",
        "health_sub_documents": "Store lab results, certificates & medical docs.",
        "health_metric_pressure": "Blood pressure",
        "health_metric_sugar": "Blood sugar",
        "health_metric_weight": "Weight",
        "health_metric_other": "Metric",
        "health_diary_title": "📋 <b>Health diary</b>",
        "health_diary_empty": "No entries yet. Add your first measurement.",
        "health_diary_recent": "<b>Recent entries:</b>",
        "health_add_pressure": "➕ Blood pressure",
        "health_add_sugar": "➕ Blood sugar",
        "health_add_weight": "➕ Weight",
        "health_view_all": "📊 Full history",
        "health_enter_pressure": "Enter BP as <code>120/80</code>:",
        "health_enter_sugar": "Enter blood sugar (mmol/L), e.g. <code>5.6</code>:",
        "health_enter_weight": "Enter weight (kg), e.g. <code>75</code>:",
        "health_enter_notes": "Notes (or <code>-</code> to skip):",
        "health_metric_saved": "✅ Saved to diary.",
        "health_invalid_pressure": "Format: 120/80",
        "health_invalid_value": "Enter a number.",
        "health_med_title": "💊 <b>Medications</b>",
        "health_med_empty": "No active medications.",
        "health_med_hint_multi": "You can add multiple medications. Tap one to edit or delete.",
        "health_med_count": "Active medications: <b>{count}</b>",
        "health_med_add": "➕ Add medication",
        "health_med_name": "Medication name:",
        "health_med_dosage": "Dosage (e.g. 1 tablet):",
        "health_med_times": "Intake times, comma-separated:\n<code>08:00, 20:00</code>",
        "health_med_times_error": "Use HH:MM format, e.g. 08:00, 20:00",
        "health_med_saved": "✅ Medication added. Reminders at scheduled times.",
        "health_med_removed": "Medication removed",
        "health_med_not_found": "Not found",
        "health_med_dose": "Dosage",
        "health_med_reminder_title": "Time to take your medication",
        "health_med_edit_name": "✏️ Name",
        "health_med_edit_dose": "✏️ Dosage",
        "health_med_edit_times": "✏️ Time",
        "health_med_delete": "🗑 Delete",
        "health_med_back_list": "⬅️ Back to list",
        "health_med_updated": "✅ Changes saved",
        "health_med_edit_name_prompt": "New medication name:",
        "health_med_edit_dose_prompt": "New dosage:",
        "health_med_edit_times_prompt": "New intake times:\n<code>08:00, 20:00</code>",
        "health_visit_title": "🩺 <b>Doctor visits</b>",
        "health_visit_empty": "No upcoming visits.",
        "health_visit_add": "➕ Add visit",
        "health_visit_name": "Doctor / specialist (e.g. therapist):",
        "health_visit_datetime": "Date & time: <code>25.06.2026 10:00</code>",
        "health_visit_saved": "✅ Visit reminder created.",
        "health_doc_title": "📁 <b>Medical documents</b>",
        "health_doc_empty": "No documents yet.",
        "health_doc_hint": "Send 📷 photo or text of lab results — we'll save to your medical record.",
        "health_doc_add": "➕ Text record",
        "health_doc_saved": "✅ Document saved.",
        "car_module_intro": (
            "🚗 <b>Car</b> — your driving assistant:\n\n"
            "• Dashboard error decoding from photos\n"
            "• Sound analysis & possible faults\n"
            "• Service schedule & reminders (oil, filters, tires)\n"
            "• Insurance & inspection\n"
            "• Car expense tracking"
        ),
        "car_ai_hint": "💬 Type a question or send 📷/🎤",
        "car_sub_panel_photo": "Send a dashboard photo — AI decodes warnings.",
        "car_sub_sounds": "Describe the sound or send 🎤 voice — AI suggests causes.",
        "car_sub_service": "Maintenance schedule.",
        "car_sub_reminders": "Oil, filter and tire change reminders.",
        "car_sub_compliance": "Insurance and inspection expiry dates.",
        "car_sub_expenses": "Fuel, repairs, car wash and more.",
        "car_panel_hint": "📷 Send a <b>dashboard photo</b> with warning lights.\n\nAI will decode errors and urgency.",
        "car_sounds_hint": "Describe the sound in text or 🎤 voice:\n<i>squeal when braking, knock from left, hum at speed…</i>",
        "car_service_title": "🔧 <b>Service schedule</b>",
        "car_service_empty": "No scheduled work. Add the first item.",
        "car_service_hint": "Upcoming:",
        "car_service_add": "➕ Add to schedule",
        "car_reminders_title": "⏰ <b>Reminders</b> (oil, filters, tires)",
        "car_reminders_empty": "No reminders yet.",
        "car_maint_oil": "🛢 Oil",
        "car_maint_filter": "🧰 Filters",
        "car_maint_tires": "🛞 Tires",
        "car_maint_service": "🔧 Service",
        "car_maint_other": "📋 Other",
        "car_maint_pick_type": "Select work type:",
        "car_enter_date": "Reminder date:\n<code>15.07.2026</code>",
        "car_comp_enter_date": "Expiry date:\n<code>31.12.2026</code>",
        "car_enter_notes": "Notes (mileage, shop…) or <code>-</code>",
        "car_date_error": "Format: DD.MM.YYYY",
        "car_maint_saved": "✅ Added to service schedule",
        "car_comp_saved": "✅ Date saved",
        "car_expense_saved": "✅ Expense recorded",
        "car_deleted": "Removed",
        "car_not_found": "Not found",
        "car_back_list": "⬅️ Back to schedule",
        "car_maint_delete": "🗑 Delete",
        "car_comp_title": "📋 <b>Insurance & inspection</b>",
        "car_comp_empty": "Add insurance or inspection dates.",
        "car_comp_insurance": "🛡 Insurance",
        "car_comp_inspection": "✅ Inspection",
        "car_comp_add_insurance": "➕ Insurance",
        "car_comp_add_inspection": "➕ Inspection",
        "car_expires": "Expires",
        "car_expires_today": "expires today",
        "car_expires_tomorrow": "expires tomorrow",
        "car_expires_in_days": "{days} days left",
        "car_maint_reminder_title": "Car maintenance reminder",
        "car_comp_reminder_title": "Car deadline",
        "car_due_today": "scheduled for today",
        "car_expenses_title": "💰 <b>Car expenses</b>",
        "car_expenses_empty": "No expenses yet.",
        "car_expenses_total": "Total: <b>{total}</b> UZS",
        "car_expenses_add": "➕ Add expense",
        "car_expense_title_prompt": "What did you pay for? (fuel, repair, wash…)",
        "car_expense_amount_prompt": "Amount (UZS):",
        "fin_module_intro": (
            "💰 <b>Finance</b> — personal money assistant:\n\n"
            "• Track income and expenses\n"
            "• Financial goals and savings\n"
            "• Monthly budget by category\n"
            "• Bill payment reminders\n"
            "• Expense analysis\n"
            "• Loans"
        ),
        "fin_ai_hint": "💬 Ask AI about your finances",
        "fin_sub_income": "Record salary, side income, and other inflows.",
        "fin_sub_expense": "Track spending with categories.",
        "fin_sub_goals": "Set goals: phone, vacation, savings.",
        "fin_sub_budget": "Monthly limits per category.",
        "fin_sub_bills": "Utilities, internet, subscriptions — timely reminders.",
        "fin_sub_analysis": "Expense breakdown and monthly balance.",
        "fin_sub_loans": "Loans and mortgage — amount, monthly payment, and reminders.",
        "fin_income_title": "📈 <b>Income</b>",
        "fin_expense_title": "📉 <b>Expenses</b>",
        "fin_total": "Total: <b>{total}</b> UZS",
        "fin_empty": "No entries yet.",
        "fin_add_tx": "➕ Add",
        "fin_tx_title_prompt": "Description (salary, groceries…):",
        "fin_tx_amount_prompt": "Amount (UZS):",
        "fin_tx_saved": "✅ Entry saved",
        "fin_pick_category": "Pick an expense category:",
        "fin_cat_food": "🍔 Food",
        "fin_cat_transport": "🚗 Transport",
        "fin_cat_home": "🏠 Home",
        "fin_cat_health": "🏥 Health",
        "fin_cat_fun": "🎬 Fun",
        "fin_cat_shopping": "🛒 Shopping",
        "fin_cat_bills": "💡 Bills",
        "fin_cat_other": "📋 Other",
        "fin_goals_title": "🎯 <b>Financial goals</b>",
        "fin_goals_empty": "No goals yet.",
        "fin_goal_add": "➕ New goal",
        "fin_goal_title_prompt": "Goal name (e.g. vacation):",
        "fin_goal_target_prompt": "Target amount (UZS):",
        "fin_goal_current_prompt": "Already saved (UZS) or 0:",
        "fin_goal_saved": "✅ Goal added",
        "fin_goal_updated": "✅ Progress updated",
        "fin_goal_update": "📊 Update progress",
        "fin_goal_delete": "🗑 Delete",
        "fin_goal_update_prompt": "How much saved so far (UZS):",
        "fin_back_goals": "⬅️ Back to goals",
        "fin_goal_default": "Goal",
        "fin_budget_title": "📊 <b>Monthly budget</b>",
        "fin_budget_month": "Month: <b>{month}</b>",
        "fin_budget_empty": "No limits set. Pick a category below.",
        "fin_budget_hint": "Tap a category to set a monthly limit.",
        "fin_budget_limit_prompt": "Limit for «{category}» (UZS):",
        "fin_budget_saved": "✅ Limit saved",
        "fin_bills_title": "💳 <b>Bill payments</b>",
        "fin_bills_empty": "No bills yet. Add the first one.",
        "fin_bill_add": "➕ Add bill",
        "fin_bill_title_prompt": "Name (utilities, internet…):",
        "fin_bill_amount_prompt": "Amount (UZS):",
        "fin_bill_date_prompt": "Due date:\n<code>05.07.2026</code>",
        "fin_bill_saved": "✅ Bill added — we'll remind you on the due date",
        "fin_bill_delete": "🗑 Delete",
        "fin_bill_default": "Bill",
        "fin_back_bills": "⬅️ Back to bills",
        "fin_back_loans": "⬅️ Back to loans",
        "fin_loan_delete": "🗑 Delete",
        "fin_bill_reminder_title": "Bill payment reminder",
        "fin_due_today": "due today",
        "fin_bill_pay": "pay",
        "fin_analysis_title": "📊 <b>Expense analysis</b>",
        "fin_analysis_summary": "{month}: income <b>{income}</b> | expense <b>{expense}</b> | balance <b>{balance}</b> UZS",
        "fin_analysis_by_cat": "<b>By category:</b>",
        "fin_not_found": "Not found",
        "fin_deleted": "Deleted",
        "biz_module_intro": (
            "💼 <b>Business</b> — AI assistant for entrepreneurs:\n\n"
            "• AI consultant for launch and growth\n"
            "• Business plans and strategy\n"
            "• Ad and creative generation\n"
            "• Competitor analysis\n"
            "• Contract drafts\n"
            "• Client responses\n"
            "• Sales analysis"
        ),
        "biz_ai_hint": "💬 Describe your task or tap «Ask AI»",
        "biz_sub_consultant": "Advice on niche, model, sales channels, and risks.",
        "biz_sub_plans": "Structured business plans: market, product, finances, milestones.",
        "biz_sub_ads": "Ad copy, headlines, posts, and campaigns for your audience.",
        "biz_sub_competitors": "Competitor breakdown: strengths, pricing, positioning.",
        "biz_sub_contracts": "Contract drafts — have a lawyer review before signing.",
        "biz_sub_client_responses": "Professional client replies: complaints, questions, sales.",
        "biz_sub_sales_analysis": "Sales analysis from your data: trends, funnel, recommendations.",
        "leg_module_intro": (
            "⚖️ <b>Legal help</b> — AI assistant for legal questions:\n\n"
            "• Answers to legal questions\n"
            "• Document review (text or photo)\n"
            "• Application and letter drafts\n"
            "• Legislation explained in plain language\n"
            "• Action checklists for different situations\n\n"
            "⚠️ Not a lawyer — general information and drafts only."
        ),
        "leg_ai_hint": "💬 Describe your situation or tap «Ask AI»",
        "leg_sub_questions": "Answers about rights, obligations, deadlines, and procedures.",
        "leg_sub_doc_check": "Review contracts and documents — send text or a photo.",
        "leg_sub_applications": "Draft applications to authorities, courts, employers.",
        "leg_sub_legislation": "Plain-language explanation of laws and who they apply to.",
        "leg_sub_checklists": "Step-by-step actions: documents, deadlines, where to go.",
        "trv_module_intro": (
            "✈️ <b>Travel</b> — your trip assistant:\n\n"
            "• Route planning\n"
            "• Visa information\n"
            "• Trip budget\n"
            "• Packing checklist\n"
            "• Phrase translator\n"
            "• Currency converter (reference rates)"
        ),
        "trv_ai_hint": "💬 Describe your trip or tap «Ask AI»",
        "trv_sub_routes": "Day-by-day routes: cities, transport, sights.",
        "trv_sub_visas": "Visa info: required or not, documents, timelines — check consulate website.",
        "trv_sub_budget": "Budget: flights, lodging, food, transport, fun, buffer.",
        "trv_sub_packing": "Packing list tailored to climate and trip length.",
        "trv_sub_translator": "Translations and useful phrases for airport, hotel, restaurant.",
        "trv_sub_currency": "Currency converter and exchange tips. Rates are reference only.",
        "trv_fx_convert": "💱 Convert",
        "trv_fx_amount_prompt": "Amount to convert:",
        "trv_fx_from_prompt": "From currency:",
        "trv_fx_to_prompt": "To currency:",
        "trv_fx_result": "💱 <b>{amount}</b> = <b>{result}</b>",
        "trv_fx_disclaimer": "Reference rate only — not for financial transactions.",
        "trv_fx_error": "Conversion failed",
        "home_module_intro": (
            "🏠 <b>Home</b> — household assistant:\n\n"
            "• Utility bill payment reminders\n"
            "• Home expense tracking\n"
            "• Renovation plan\n"
            "• Shopping list\n"
            "• Home inventory"
        ),
        "home_sub_utilities": "Electricity, gas, water, internet — reminders on due date.",
        "home_sub_expenses": "Track home and household spending.",
        "home_sub_repair": "Repair tasks: planned → in progress → done.",
        "home_sub_shopping": "Shopping list — mark items bought with one tap.",
        "home_sub_inventory": "What is where: item, quantity, location.",
        "home_utilities_title": "💡 <b>Utility bills</b>",
        "home_expenses_title": "💰 <b>Home expenses</b>",
        "home_repair_title": "🔨 <b>Renovation plan</b>",
        "home_shopping_title": "🛒 <b>Shopping list</b>",
        "home_inventory_title": "📦 <b>Home inventory</b>",
        "home_empty": "Nothing yet.",
        "home_total": "Total: <b>{total}</b> UZS",
        "home_not_found": "Not found",
        "home_deleted": "Deleted",
        "home_delete": "🗑 Delete",
        "home_utility_add": "➕ Add bill",
        "home_utility_title_prompt": "Service (electricity, gas, internet…):",
        "home_utility_amount_prompt": "Amount (UZS):",
        "home_utility_date_prompt": "Due date:\n<code>05.07.2026</code>",
        "home_utility_saved": "✅ Bill added — we'll remind you on the due date",
        "home_utility_default": "Utilities",
        "home_utility_reminder_title": "Utility payment",
        "home_due_today": "due today",
        "home_back_utilities": "⬅️ Back to bills",
        "home_expense_add": "➕ Add expense",
        "home_expense_title_prompt": "What did you spend on:",
        "home_expense_amount_prompt": "Amount (UZS):",
        "home_expense_saved": "✅ Expense saved",
        "home_expense_default": "Expense",
        "home_repair_add": "➕ Add task",
        "home_repair_title_prompt": "What needs to be done:",
        "home_repair_notes_prompt": "Notes (or «-» to skip):",
        "home_repair_saved": "✅ Task added",
        "home_repair_default": "Repair",
        "home_repair_planned": "planned",
        "home_repair_in_progress": "in progress",
        "home_repair_done": "done",
        "home_repair_cycle": "🔄 Change status",
        "home_repair_updated": "Status updated",
        "home_back_repair": "⬅️ Back to repair",
        "home_shopping_add": "➕ Add item",
        "home_shopping_title_prompt": "What to buy:",
        "home_shopping_saved": "✅ Added to list",
        "home_inventory_add": "➕ Add item",
        "home_inventory_title_prompt": "Item name:",
        "home_inventory_location_prompt": "Where it is (or «-»):",
        "home_inventory_qty_prompt": "Quantity:",
        "home_inventory_saved": "✅ Added to inventory",
        "home_inventory_default": "Item",
        "home_inv_no_location": "location not set",
        "home_back_inventory": "⬅️ Back to inventory",
        "shop_module_intro": (
            "🛒 <b>Shopping</b> — AI assistant for buying decisions:\n\n"
            "• Product comparison\n"
            "• Finding good deals\n"
            "• Spec check\n"
            "• Buying advice"
        ),
        "shop_ai_hint": "💬 Describe the product or task, or tap «Ask AI»",
        "shop_sub_compare": "Compare models by price, features, pros and cons.",
        "shop_sub_deals": "How to find good deals and spot real discounts.",
        "shop_sub_specs": "Spec breakdown — what parameters in listings actually mean.",
        "shop_sub_advice": "Recommendations for your budget and needs.",
        "edu_module_intro": (
            "📚 <b>Education</b> — AI tutor:\n\n"
            "• Topic explanations\n"
            "• Exam preparation\n"
            "• Language learning\n"
            "• Note generation\n"
            "• Homework check"
        ),
        "edu_ai_hint": "💬 Ask a question or tap «Ask AI»",
        "edu_sub_topics": "Any topic in plain language: definitions, examples, analogies.",
        "edu_sub_exams": "Study plan, key questions, review before the exam.",
        "edu_sub_languages": "Grammar, vocabulary, dialogues, and error correction.",
        "edu_sub_notes": "Structured notes by topic or lecture.",
        "edu_sub_homework": "Check with error explanations — not just the final answer.",
        "nut_module_intro": (
            "🥗 <b>Nutrition</b> — healthy eating assistant:\n\n"
            "• Meal planning\n"
            "• Calorie calculator\n"
            "• Recipes\n"
            "• Grocery list\n"
            "• Water tracking"
        ),
        "nut_ai_hint": "💬 Describe your goal or tap «Ask AI»",
        "nut_sub_diet": "Balanced meal plan for your goals and preferences.",
        "nut_sub_calories": "Meal calories and daily intake — AI or calculator.",
        "nut_sub_recipes": "Recipes with ingredients and approximate calories.",
        "nut_sub_grocery": "Grocery list — mark items as bought.",
        "nut_sub_water": "Today's water intake — quick +250/+500 ml buttons.",
        "nut_grocery_title": "🛒 <b>Grocery list</b>",
        "nut_water_title": "💧 <b>Water tracking</b>",
        "nut_empty": "Nothing yet.",
        "nut_not_found": "Not found",
        "nut_grocery_add": "➕ Add item",
        "nut_grocery_title_prompt": "What to buy:",
        "nut_grocery_saved": "✅ Added to list",
        "nut_water_summary": "Today: <b>{total}</b> / {goal} ml ({pct}%)",
        "nut_water_hint": "Tap a button to log water.",
        "nut_water_custom": "➕ Custom amount",
        "nut_water_ml_prompt": "How many ml:",
        "nut_water_added": "✅ Added",
        "nut_cal_calc": "🧮 Calculate daily intake",
        "nut_cal_weight_prompt": "Weight (kg):",
        "nut_cal_height_prompt": "Height (cm):",
        "nut_cal_age_prompt": "Age:",
        "nut_cal_sex_prompt": "Sex:",
        "nut_cal_male": "Male",
        "nut_cal_female": "Female",
        "nut_cal_activity_prompt": "Activity level:",
        "nut_act_sedentary": "Sedentary",
        "nut_act_light": "Light",
        "nut_act_moderate": "Moderate",
        "nut_act_active": "Active",
        "nut_act_very": "Very active",
        "nut_cal_result": "📊 Your daily intake: <b>{kcal}</b> kcal\n\n<i>Estimate via Mifflin-St Jeor</i>",
        "org_module_intro": (
            "📅 <b>Organizer</b> — everything in one place:\n\n"
            "• Tasks with deadlines\n"
            "• Event calendar\n"
            "• Reminders\n"
            "• Birthdays\n"
            "• Meetings\n"
            "• Notes"
        ),
        "org_tasks_title": "✅ <b>Tasks</b>",
        "org_calendar_title": "📅 <b>Calendar</b>",
        "org_reminders_title": "🔔 <b>Reminders</b>",
        "org_birthdays_title": "🎂 <b>Birthdays</b>",
        "org_meetings_title": "🤝 <b>Meetings</b>",
        "org_notes_title": "📝 <b>Notes</b>",
        "org_empty": "Nothing here yet.",
        "org_not_found": "Not found",
        "org_add": "➕ Add",
        "org_task_add": "➕ New task",
        "org_task_title_prompt": "Task title:",
        "org_task_due_prompt": "Due date (or «-» for none):\n<code>25.06.2026 18:00</code>",
        "org_task_saved": "✅ Task added",
        "org_task_default": "Task",
        "org_note_add": "➕ New note",
        "org_note_title_prompt": "Note title:",
        "org_note_body_prompt": "Text (or «-»):",
        "org_note_saved": "✅ Note saved",
        "org_note_default": "Note",
        "org_meet_add": "➕ Meeting",
        "org_bday_add": "➕ Birthday",
        "org_event_title_prompt": "Meeting title:",
        "org_bday_title_prompt": "Name (birthday):",
        "org_event_date_prompt": "Date and time:\n<code>25.06.2026 18:00</code>",
        "org_event_saved": "✅ Event added",
        "org_event_default": "Event",
        "org_rem_add": "➕ Reminder",
        "org_rem_title_prompt": "Reminder text:",
        "org_rem_date_prompt": "When to remind:\n<code>25.06.2026 09:00</code>",
        "org_rem_saved": "✅ Reminder: {title} — {when}",
        "org_rem_default": "Reminder",
        "org_date_error": "Format: DD.MM.YYYY HH:MM",
        "ast_module_intro": (
            "🤖 <b>AI assistant</b> — all-in-one helper:\n\n"
            "• Answers to any questions\n"
            "• Text translations\n"
            "• PDF and documents\n"
            "• Photo analysis\n"
            "• Text writing\n"
            "• Image generation (DALL-E)\n"
            "• Programming help"
        ),
        "ast_ai_hint": "Send a message or tap «Ask AI».",
        "ast_sub_questions": "Any questions — facts, advice, explanations.",
        "ast_sub_translate": "Translate between languages while keeping meaning and tone.",
        "ast_sub_documents": "PDF and docs: summaries, key points, Q&A on content.",
        "ast_sub_photo": "Send a photo — AI detects objects, text, and context.",
        "ast_sub_writing": "Articles, posts, emails, resumes — writing and editing.",
        "ast_sub_images": "Describe an image in text — AI generates it.",
        "ast_sub_code": "Code, debugging, algorithms, architecture — dev help.",
        "ast_send_photo": "📷 Send a photo for analysis.",
        "ast_send_image_prompt": "✏️ Describe the image in one message.",
        "ast_send_document": "📎 Send a PDF or document, then ask a question about it.",
        "ast_image_generating": "🎨 Generating image…",
        "ast_image_failed": "⚠️ Could not create image. Check OPENAI_API_KEY or try another prompt.",
        "ast_image_done": "🎨 {prompt}",
        "ast_doc_saved": "📎 Document «{name}» saved.",
        "ast_doc_caption_note": "Ask a question about the document in text — AI will help.",
        "vlt_module_intro": (
            "🔐 <b>Personal vault</b> — your data in one place:\n\n"
            "• Documents\n"
            "• Passport data (optional)\n"
            "• Policies\n"
            "• Warranty cards\n"
            "• Receipts\n"
            "• Important notes\n\n"
            "<i>Data is stored only in your bot.</i>"
        ),
        "vlt_documents_title": "📄 <b>Documents</b>",
        "vlt_passport_title": "🛂 <b>Passport data</b>",
        "vlt_policies_title": "📋 <b>Policies</b>",
        "vlt_warranty_title": "🧾 <b>Warranty cards</b>",
        "vlt_receipts_title": "🧾 <b>Receipts</b>",
        "vlt_notes_title": "📝 <b>Important notes</b>",
        "vlt_empty": "Nothing here yet.",
        "vlt_add": "➕ Add",
        "vlt_not_found": "Not found",
        "vlt_deleted": "Deleted",
        "vlt_saved": "✅ Saved",
        "vlt_default_title": "Entry",
        "vlt_title_prompt": "Entry title:",
        "vlt_body_prompt": "Description or details (or «-»):",
        "vlt_amount_prompt": "Receipt amount (or «-»):",
        "vlt_amount_error": "Enter a number or «-»",
        "vlt_passport_hint": "⚠️ Storing passport data is optional — only if you choose. Do not share the bot with others.",
        "vlt_passport_title_prompt": "Title (e.g. «Foreign passport»):",
        "vlt_passport_body_prompt": "Passport details (series, number, expiry — or «-»):",
        "vlt_file_hint": "📎 Send a photo or file — it saves automatically.\n👆 Tap 📎 in the list to open the file.",
        "btn_notifications": "🔔 Notifications",
        "btn_ecosystem": "🌐 Ecosystem",
        "btn_add_reminder": "➕ Reminder",
        "eco_btn_memory": "🧠 AI memory",
        "eco_features_intro": (
            "🌐 <b>Ecosystem features</b> — everything in one place:\n\n"
            "🔔 <b>Notification center</b> — meds, meetings, payments, car service, birthdays\n"
            "🧠 <b>AI memory</b> — {memory}\n"
            "🔍 <b>Life search</b> — «When did I change oil?»\n"
            "🎤 <b>Voice mode</b> — {voice}\n"
            "📷 <b>Photos</b> — receipts, docs, lab results, car errors\n"
            "🌐 <b>Languages</b> — Russian, Uzbek, English"
        ),
        "eco_notifications_title": "🔔 <b>Notification center</b>",
        "eco_notifications_empty": "No upcoming events. Add a reminder below.",
        "eco_src_reminder": "Reminder",
        "eco_src_organizer": "Organizer",
        "eco_src_health": "Health",
        "eco_src_medicine": "Medicine",
        "eco_src_meeting": "Meeting",
        "eco_src_birthday": "Birthday",
        "eco_src_calendar": "Calendar",
        "eco_src_car_service": "Car service",
        "eco_src_insurance": "Insurance",
        "eco_src_payment": "Payment",
        "eco_src_utilities": "Utilities",
        "eco_src_credit": "Credit",
        "eco_search_events": "Events:",
        "eco_search_reminders": "Reminders:",
        "eco_search_ai_title": "AI answer",
        "eco_search_ai_hint": "Answer the user's question using their saved data from context.",
        "eco_voice_mode_hint": "🎤 Voice mode is on — you can keep talking by voice.",
        "gen_ai_hint": "Type a question or tap «Ask AI».",
        "ntf_module_intro": (
            "🔔 <b>Notifications</b>\n\n"
            "Meds, car service, utilities, loans — from their sections.\n"
            "Add movies, events, deliveries, subscriptions, visas & custom here."
        ),
        "ntf_sub_hint": "Add a reminder or open the relevant section.",
        "ntf_add": "➕ Add",
        "ntf_open_module": "↗️ Open section",
        "ntf_empty": "Nothing here yet.",
        "ntf_title_prompt": "Title (Netflix, US visa…):",
        "ntf_title_short": "Title too short.",
        "ntf_due_prompt": "Due date (DD.MM.YYYY):",
        "ntf_due_error": "Could not parse date.",
        "ntf_amount_prompt": "Subscription amount (or «-»):",
        "ntf_amount_error": "Enter a number or «-».",
        "ntf_saved": "✅ Saved. I'll remind you on time.",
        "ntf_add_only_data": "Adding is available for subscriptions and visas only.",
        "eco_src_subscription": "Subscription",
        "eco_src_visa": "Visa",
        "eco_src_visa": "Visa",
        "help_text": (
            "❓ <b>How to use Life AI</b>\n\n"
            "1️⃣ <b>Home</b> — /menu or 🏠 «Home»\n"
            "2️⃣ <b>Pick a topic</b> — Health, Finance, Car…\n"
            "3️⃣ <b>Ask a question</b> — just type (no button needed)\n"
            "4️⃣ <b>Save a note</b> — ➕ button\n"
            "5️⃣ <b>Find records</b> — ⚙️ Settings → 🔍 Search"
        ),
        "mod_hint_health": "Symptoms, lab tests, medications, doctor visits.",
        "mod_example_health": "«what does high hemoglobin mean»",
        "mod_hint_car": "Service, oil, dashboard warnings, insurance.",
        "mod_example_car": "«when to change oil at 100k km»",
        "mod_hint_finance": "Income, expenses, budget, and goals.",
        "mod_example_finance": "«how to plan a family budget»",
        "mod_hint_business": "Business plans, ads, contracts, and sales.",
        "mod_example_business": "«plan for opening a café»",
        "mod_hint_legal": "Legal questions, documents, and applications.",
        "mod_example_legal": "«documents needed to rent an apartment»",
        "mod_hint_travel": "Routes, visas, trip budget, packing lists.",
        "mod_example_travel": "«5-day Istanbul itinerary»",
        "mod_hint_home": "Utilities, repairs, shopping, inventory.",
        "mod_example_home": "«checklist before bathroom renovation»",
        "mod_hint_shopping": "Product comparison and buying advice.",
        "mod_example_shopping": "«iPhone vs Samsung for photos»",
        "mod_hint_education": "Topics, exams, languages, homework.",
        "mod_example_education": "«explain Pythagorean theorem simply»",
        "mod_hint_nutrition": "Meal plans, calories, and recipes.",
        "mod_example_nutrition": "«1800 kcal gluten-free menu»",
        "mod_hint_fitness": "Workout plans and progress tracking.",
        "mod_example_fitness": "«3-day home workout without equipment»",
        "mod_hint_organizer": "Tasks, calendar, reminders, meetings.",
        "mod_example_organizer": "«remind me to pay internet on the 1st»",
        "mod_hint_ai_assistant": "Any questions, translations, text, photos.",
        "mod_example_ai_assistant": "«translate to English: good morning»",
        "mod_hint_vault": "Documents, passport, policies, receipts.",
        "mod_example_vault": "«where to store passport scan»",
        "onb_welcome": (
            "👋 <b>Welcome to Life AI!</b>\n\n"
            "<b>How to use:</b>\n"
            "1️⃣ Pick a topic (Health, Finance, Car…)\n"
            "2️⃣ Type a question — AI answers on topic\n"
            "3️⃣ «Save a note» — test results, expenses, reminders\n\n"
            "🔍 Search and ⚙️ Settings — on the home screen.\n"
            "❓ /help"
        ),
        "onb_start_btn": "🚀 Start",
        "onb_done": "✅ Ready! You can use the bot.",
        "export_done": "📦 Your data export (JSON).",
        "cmd_expense_format": "Format: /expense Title | 50000",
        "cmd_expense_saved": "✅ Expense «{title}» — {amount} UZS",
        "cmd_oil_hint": "🚗 Car → Service is open. Tell me when you changed the oil, or add it via the menu.",
        "vlt_delete_confirm": "🗑 Delete this entry?",
        "vlt_file_expired": "⚠️ File unavailable (Telegram stores files for a limited time). Upload again.",
        "vlt_confirm_yes": "✅ Yes, delete",
    },
}


from app.core.i18n.extra_strings import EXTRA_EN, EXTRA_RU, EXTRA_UZ

_STRINGS["ru"].update(EXTRA_RU)
_STRINGS["uz"].update(EXTRA_UZ)
_STRINGS["en"].update(EXTRA_EN)


def normalize_lang(lang: str | None) -> str:
    if not lang:
        return "ru"
    code = lang.lower().split("-")[0]
    return code if code in SUPPORTED_LANGUAGES else "ru"


def t(lang: str | None, key: str, **kwargs: object) -> str:
    code = normalize_lang(lang)
    text = _STRINGS.get(code, _STRINGS["ru"]).get(key) or _STRINGS["ru"].get(key) or key
    return text.format(**kwargs) if kwargs else text


def category_title(lang: str | None, idx: int) -> str:
    return t(lang, f"cat_{idx}")


def ai_reply_language(lang: str | None) -> str:
    code = normalize_lang(lang)
    return t(code, f"lang_reply_{code}")
