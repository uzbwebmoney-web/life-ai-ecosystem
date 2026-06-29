EXTRA_RU: dict[str, str] = {
    "dash_greeting_morning": "Доброе утро, {name} 👋",
    "dash_greeting_day": "Добрый день, {name} 👋",
    "dash_greeting_evening": "Добрый вечер, {name} 👋",
    "dash_greeting_night": "Доброй ночи, {name} 👋",
    "dash_friend": "друг",
    "dash_today": "Сегодня",
    "dash_today_empty": "На сегодня всё спокойно ✨",
    "dash_timeline": "Ближайшие 7 дней",
    "dash_what_todo": "Что хотите сделать?",
    "dash_time_now": "сейчас",
    "dash_time_in_min": "через {n} мин",
    "dash_time_in_hours": "через {n} ч",
    "dash_time_tomorrow": "завтра",
    "dash_time_in_days": "через {n} дн",
    "dash_credit_today": "Сегодня оплата: {title}",
    "dash_credit_tomorrow": "Завтра оплата: {title}",
    "dash_morning_title": "☀️ Доброе утро!",
    "dash_daily_tip": "Напишите вопрос или отправьте 📷 — бот поймёт сам.",
    "btn_scan": "📷 Сканер",
    "btn_sos": "🚨 SOS",
    "btn_all_modules_short": "📂 Все разделы",
    "btn_household": "👨‍👩‍👧 Семейный доступ",
    "btn_household_join": "➕ Ввести код приглашения",
    "household_join_prompt": "Введите код приглашения от владельца семьи:",
    "all_modules_pick": "📂 <b>Все разделы</b>\n\nВыберите:",
    "scan_prompt": "📷 <b>Универсальный сканер</b>\n\nОтправьте фото: чек, анализ, договор, рецепт, ошибку авто, холодильник…\nAI сам определит тип и сохранит в архив.",
    "scan_saved": "✅ Сохранено в {folder}",
    "remember_saved": "✅ Запомнил: {text}",
    "family_rel_pet": "🐶 Питомец",
    "household_info": "👨‍👩‍👧 <b>Семейный доступ</b>\n\nКод приглашения: <code>{code}</code>\n\nДругой человек: /join {code}\n\nУчастники видят общие напоминания и календарь владельца.",
    "household_join_usage": "Формат: /join КОД",
    "household_join_ok": "✅ Вы подключены к семейному аккаунту.",
    "household_join_not_found": "Код не найден.",
    "household_join_already": "Вы уже в семье или создали свою.",
    "household_copy_code": "Код: {code}",
    "act_done": "✅",
    "act_add_car": "🚗 Добавить авто в профиль",
    "act_car_service": "🔧 Напоминание о ТО",
    "act_car_insurance": "🛡 Страховка",
    "act_med_course": "💊 Курс лечения",
    "act_med_remind": "⏰ Напоминания о лекарстве",
    "act_travel_plan": "✈️ План поездки",
    "act_travel_passport": "🛂 Проверить паспорт",
    "act_save_memory": "🧠 Сохранить в память",
    "act_save_expense": "💰 Записать расход",
    "act_hint_car_profile": "🚗 Напишите модель авто — сохраню в профиль.\nПример: «BYD Song Plus 2025»",
    "act_hint_car_service": "🔧 Раздел «Авто → ТО» открыт. Добавьте дату замены масла.",
    "act_hint_car_insurance": "🛡 Раздел «Авто → Страховка» открыт.",
    "act_hint_med_course": "💊 Раздел «Здоровье → Лекарства» открыт.",
    "act_hint_med_remind": "⏰ Раздел «Здоровье → Приём лекарств» открыт.",
    "act_hint_travel_plan": "✈️ Раздел «Путешествия» открыт.",
    "act_hint_travel_passport": "🛂 Раздел «Сейф → Паспорт» открыт.",
    "act_hint_save_expense": "💰 Раздел «Финансы → Расходы» открыт.",
    "act_hint_save_memory": "🧠 Напишите «Запомни: …» — сохраню навсегда.",
    "sos_menu": "🚨 <b>SOS — срочная помощь</b>\n\nВыберите ситуацию:",
    "sos_btn_first_aid": "🩹 Первая помощь",
    "sos_btn_phones": "📞 Телефоны",
    "sos_btn_accident": "🚗 ДТП",
    "sos_btn_passport": "🛂 Потеря паспорта",
    "sos_btn_poison": "☠️ Отравление",
    "sos_btn_burn": "🔥 Ожог",
    "sos_first_aid": (
        "🩹 <b>Первая помощь</b>\n\n"
        "1. Оцените сознание и дыхание\n"
        "2. Вызовите 103 (скорая)\n"
        "3. Не двигайте при травме позвоночника\n"
        "4. При кровотечении — давящая повязка\n\n"
        "⚠️ Это справка, не замена врача."
    ),
    "sos_phones": "📞 <b>Телефоны (Узбекистан)</b>\n\n103 — скорая\n102 — полиция\n1015 — пожарная\n104 — газ",
    "sos_accident": "🚗 <b>ДТП</b>\n\n1. Включите аварийку\n2. Вызовите 102\n3. Сфотографируйте место\n4. Не подписывайте непонятные бумаги\n5. Сообщите страховой",
    "sos_passport": "🛂 <b>Потеря паспорта</b>\n\n1. Заявление в полицию\n2. Обратитесь в консульство / MVD\n3. Сохраните справку о потере\n4. Проверьте срок загранпаспорта заранее",
    "sos_poison": "☠️ <b>Отравление</b>\n\n1. Вызовите 103\n2. Не вызывайте рвоту без указания врача\n3. Сохраните упаковку / остатки\n4. Пейте воду только если в сознании",
    "sos_burn": "🔥 <b>Ожог</b>\n\n1. Охладите водой 15–20 мин\n2. Не лопайте пузыри\n3. Не мажьте маслом\n4. При большой площади — 103",
    "weather_unavailable": "Погода временно недоступна.",
    "weather_now": "🌤 Сейчас: {temp}°C, влажность {humidity}%, ветер {wind} м/с",
    "weather_today_range": "📈 Сегодня: {tmin}°…{tmax}°C",
    "weather_uv": "☀️ UV-индекс: {uv}",
    "profile_facts_header": "Известные факты о пользователе:",
    "household_members_title": "Участники",
    "scan_btn_expense": "💰 Записать расход",
    "scan_amount_detected": "Сумма с чека: {amount} UZS",
    "alert_reminder": "📋 <b>Напоминание</b>\n\n{title}\n📅 {when}{extra}",
    "alert_reminder_movie": "🎬 <b>Скоро начало!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_event": "🎉 <b>Скоро событие!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_ticket": "✈️ <b>Не забудьте про поездку!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_delivery": "📦 <b>Ожидается доставка</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_appointment": "📆 <b>Напоминание о записи</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_custom": "🔔 <b>Напоминание</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_subscription": "📺 <b>Подписка</b>\n\n{title}\n📅 {when}{extra}",
    "alert_reminder_visa": "🛂 <b>Виза / документ</b>\n\n{title}\n📅 {when}{extra}",
    "reminder_generic_title": "Напоминание",
    "credits_remaining_short": "ост. {remaining}",
    "ntf_add_movie": "🎬 Фильм / шоу",
    "ntf_add_event": "🎉 Событие",
    "ntf_add_ticket": "✈️ Рейс / билет",
    "ntf_add_delivery": "📦 Доставка",
    "ntf_add_appointment": "📆 Запись",
    "ntf_add_custom": "🔔 Своё",
    "ntf_add_subscription": "📺 Подписка",
    "ntf_add_visa": "🛂 Виза",
    "ntf_manage_alerts": "📋 Мои напоминания",
    "ntf_list_intro": "📋 <b>Мои напоминания</b>\n\nФильмы, события, подписки, визы и другое.",
    "ntf_title_movie": "Название фильма, сериала или шоу:",
    "ntf_title_event": "Название события (концерт, матч, встреча…):",
    "ntf_title_ticket": "Рейс, поезд или мероприятие (куда едете):",
    "ntf_title_delivery": "Что доставляют (магазин, посылка…):",
    "ntf_title_appointment": "Куда записаны (врач, салон, сервис…):",
    "ntf_title_custom": "Название напоминания:",
    "ntf_title_subscription": "Название подписки (Netflix, Spotify…):",
    "ntf_title_visa": "Название (виза США, загранпаспорт…):",
    "ntf_datetime_prompt": "Дата и время:\n<code>25.06.2026 19:30</code>",
    "ntf_notes_prompt": "Детали (кинотеатр, место, ссылка — или «-»):",
    "eco_src_movie": "Кино / шоу",
    "eco_src_event": "Событие",
    "eco_src_ticket": "Поездка",
    "eco_src_delivery": "Доставка",
    "eco_src_appointment": "Запись",
    "eco_src_custom": "Напоминание",
    "btn_subscription": "💎 Подписка",
    "sub_btn_menu": "💎 Подписка и лимиты",
    "sub_btn_usage": "📊 Мои лимиты",
    "sub_btn_plans": "💳 Тарифы",
    "sub_btn_packages": "📦 Пакеты AI-запросов",
    "sub_btn_referral": "🎁 Пригласить друга",
    "sub_btn_buy": "Оформить",
    "sub_btn_back": "↩️ Назад",
    "sub_menu_intro": (
        "💎 <b>Подписка и лимиты</b>\n\n"
        "Все разделы бота доступны всем — платите только за объём.\n"
        "Цены в сумах (курс ЦБ ~12 017 so'm / $1).\n\n"
        "🎁 Первые {days} дней — Premium бесплатно."
    ),
    "sub_plans_title": "💳 <b>Тарифы</b>",
    "sub_plans_hint": "Нажмите тариф для подробностей или «Оформить».",
    "sub_packages_title": "📦 <b>Пакеты AI-запросов</b>",
    "sub_packages_hint": "Разовая покупка — запросы не сгорают.",
    "sub_package_line": "• {name}: <b>{requests}</b> зап. — <b>{price}</b>",
    "sub_usage_title": "📊 <b>Ваши лимиты</b>",
    "sub_current_plan": "Тариф: {plan}",
    "sub_trial_until": "🎁 Premium trial до {date}",
    "sub_paid_until": "Оплачен до {date}",
    "sub_ai_daily": "AI сегодня: {used} / {limit}",
    "sub_ai_monthly": "AI в месяц: {used} / {limit}",
    "sub_ai_bonus": "Бонусные запросы: {bonus}",
    "sub_storage_limit": "Хранилище: до {limit} МБ",
    "sub_vault_lock_on": "🔐 Защищённый сейф: пароль на хранилище",
    "sub_vault_lock_off": "🔐 Сейф: без пароля (защита — от Student)",
    "sub_memory_limit": "Память AI: до {limit} фактов",
    "sub_memory_unlimited": "Память AI: без ограничений",
    "sub_referral_info": (
        "🎁 <b>Пригласите друга</b>\n\n"
        "Вы и друг — по <b>{bonus}</b> AI-запросов.\n\n"
        "Ссылка:\n{link}\n\nКод: <code>{code}</code>"
    ),
    "sub_referral_applied": "🎁 Реферальный бонус начислен!",
    "sub_trial_welcome": "🎁 Premium {days} дней + {bonus} AI-запросов. /subscription — тарифы.",
    "sub_buy_plan": "💳 <b>{plan}</b>\n<b>{price}</b> / мес\n\nОплата: {contact}\nУкажите тариф и @username.",
    "sub_buy_package": "📦 <b>{name}</b> — {requests} зап.\n<b>{price}</b>\n\nОплата: {contact}",
    "sub_payment_default": "администратору бота",
    "pay_instructions": (
        "💳 <b>Оплата заявки #{order_id}</b>\n\n"
        "Товар: {product}\n"
        "Сумма: <b>{amount}</b>\n\n"
        "Переведите <b>точную сумму</b> на карту:\n"
        "<code>{card}</code>{holder_line}\n\n"
        "После перевода отправьте <b>скриншот чека</b> (фото) в этот чат."
    ),
    "pay_card_holder": "Получатель: {holder}",
    "pay_card_not_set": "карта не настроена",
    "pay_card_not_configured": "Оплата временно недоступна. Напишите администратору.",
    "pay_product_invalid": "Этот тариф нельзя оформить.",
    "pay_cancelled": "❌ Заявка отменена.",
    "pay_order_not_found": "Заявка не найдена или уже обработана.",
    "pay_receipt_received": "✅ Чек получен (заявка #{order_id}). Ожидайте подтверждения администратора.",
    "pay_approved": "✅ Оплата подтверждена!\n\n{product} активирован.",
    "pay_rejected": "❌ Оплата не подтверждена. Если перевод был — напишите администратору.",
    "pay_admin_notify": "💰 <b>Новая заявка на оплату #{order_id}</b>",
    "admin_notify_new_user": (
        "👤 <b>Новый пользователь</b>\n"
        "Telegram: <code>{telegram_id}</code> | {username}\n"
        "Язык бота: <b>{bot_lang}</b> | язык Telegram: {telegram_lang}\n"
        "Часовой пояс: {utc_offset}\n"
        "План: {plan_id}"
    ),
    "admin_notify_ai_request": (
        "🤖 <b>AI запрос</b>\n"
        "event: {event}\n"
        "user_id: <code>{telegram_id}</code>\n"
        "username: {username}\n"
        "lang: {user_lang}\n"
        "model: {model}\n"
        "tokens: in {prompt_tokens} / out {completion_tokens}\n"
        "message: {preview}"
    ),
    "pay_admin_order": (
        "📋 <b>Заявка #{order_id}</b>\n"
        "Пользователь: {user} (<code>{telegram_id}</code>)\n"
        "Товар: {product}\n"
        "Сумма: <b>{amount}</b>\n"
        "Чек: {submitted}\n"
        "Статус: {status}"
    ),
    "pay_admin_list_title": "💰 <b>Заявки на оплату</b>",
    "pay_admin_empty": "Нет заявок, ожидающих подтверждения.",
    "pay_admin_receipt": "Скриншот чека",
    "pay_admin_approve": "✅ Подтвердить",
    "pay_admin_reject": "❌ Отклонить",
    "pay_admin_done_approved": "✅ Подтверждено, тариф активирован.",
    "pay_admin_done_rejected": "❌ Заявка #{order_id} отклонена.",
    "pay_admin_approved_toast": "Подтверждено",
    "pay_admin_rejected_toast": "Отклонено",
    "pay_admin_pending_count": "⏳ Заявок на оплату: <b>{count}</b>",
    "pay_order_already_processed": "Заявка уже обработана.",
    "pay_method_choose": (
        "💳 <b>Способ оплаты</b>\n\n"
        "{product}\n"
        "Карта: <b>{uzs}</b>\n"
        "Telegram Stars: <b>{stars}</b>\n\n"
        "Выберите способ:"
    ),
    "pay_method_card": "💳 Перевод на карту",
    "pay_method_stars": "⭐ Telegram Stars",
    "pay_stars_invoice_desc": "{product} — Life AI Ecosystem",
    "pay_admin_stars_notify": (
        "⭐ <b>Оплата Stars</b>\n"
        "Пользователь: {user} (<code>{telegram_id}</code>)\n"
        "Товар: {product}\n"
        "Сумма: <b>{stars}</b>"
    ),
    "plan_price_free": "Бесплатно",
    "plan_price_monthly": "<b>{price}</b> / мес (~${usd})",
    "plan_free_name": "Free",
    "plan_free_desc": "GPT-4o Mini, сейф для документов, лимиты на AI и фото.",
    "plan_basic_name": "Basic",
    "plan_basic_desc": "GPT-5.4 Mini, голос, защищённый сейф с паролем, 40 картинок/мес.",
    "plan_premium_name": "Premium",
    "plan_premium_desc": "GPT-5.5, семья до 5, защищённый сейф, 120 картинок/мес.",
    "plan_pro_name": "Pro",
    "plan_pro_desc": "Максимум AI, семья до 10, защищённый сейф, 400 картинок/мес.",
    "plan_student_name": "Student",
    "plan_student_desc": "Учёба, GPT-5.4 Mini, защищённый сейф с паролем, 10 картинок/мес.",
    "plan_family_name": "Семейная",
    "plan_family_desc": "До 5 человек в одном аккаунте.",
    "plan_pkg_img50": "🎨 +50 изображений",
    "plan_pkg_gpt54_500": "🧠 +500 запросов GPT-5.4 Mini",
    "plan_pkg_gpt55_50": "🚀 +50 запросов GPT-5.5",
    "plan_pkg_cloud20": "☁️ +20 ГБ облака",
    "plan_limit_gpt4o_daily": "GPT-4o Mini: {n}/день",
    "plan_limit_gpt4o_unlimited": "GPT-4o Mini: ✅",
    "plan_limit_gpt54": "GPT-5.4 Mini: {n}/мес",
    "plan_limit_gpt54_none": "GPT-5.4 Mini: ❌",
    "plan_limit_gpt55": "GPT-5.5: {n}/мес",
    "plan_limit_gpt55_none": "GPT-5.5: ❌",
    "plan_limit_image_none": "GPT-Image-1: ❌",
    "plan_limit_pdf": "PDF/DOCX: {n}/мес",
    "plan_limit_pdf_none": "PDF/DOCX: ❌",
    "plan_feature_family": "Семья",
    "sub_gpt4o_unlimited": "GPT-4o Mini: без лимита",
    "sub_gpt54_monthly": "GPT-5.4 Mini: {used} / {limit}",
    "sub_gpt55_monthly": "GPT-5.5: {used} / {limit}",
    "quota_advanced_model": "🧠 GPT-5.4 Mini недоступна на вашем тарифе. /subscription",
    "quota_advanced_model_monthly": "⚠️ Лимит GPT-5.4 Mini {used}/{limit}. /subscription",
    "quota_pro_model": "🚀 GPT-5.5 недоступна на вашем тарифе. /subscription",
    "quota_pro_model_monthly": "⚠️ Лимит GPT-5.5 {used}/{limit}. /subscription",
    "plan_features_title": "<b>Что включено:</b>",
    "plan_feature_model": "AI-модель",
    "plan_model_none": "GPT-4o mini",
    "plan_model_limited": "GPT-4o mini + {cap} сложных/мес на {model}",
    "plan_model_full": "{model} для AI-задач",
    "plan_model_router": "Роутер: {top} / {advanced} / {base}",
    "plan_model_router_short": "GPT-5.5 / GPT-5.4 mini / GPT-4o mini",
    "plan_limit_photo_unlimited": "Анализ фото: безлимит",
    "plan_limit_photo_monthly": "Анализ фото: {n}/мес",
    "plan_limit_ai_unlimited": "AI: безлимит*",
    "plan_limit_memory": "Память: {n} записей",
    "plan_limit_memory_unlimited": "Память: безлимит",
    "plan_limit_image_gen": "Генерация изображений: {n}/мес",
    "plan_feature_household": "Семейный доступ: до {n} человек",
    "plan_feature_priority_max": "Максимальный приоритет",
    "plan_feature_student_modules": "Только: учёба, AI, PDF, конспекты",
    "plan_feature_memory": "AI-память",
    "sub_ai_model": "Модель: {model}",
    "sub_photo_monthly": "Анализ фото: {used} / {limit}",
    "sub_image_gen_monthly": "Генерация изображений: {used} / {limit}",
    "sub_packages_ai_title": "🤖 AI-запросы:",
    "sub_packages_addon_title": "📦 Разовые пакеты:",
    "sub_addon_line": "• {name} — <b>{price}</b>",
    "quota_photo_monthly": "⚠️ Лимит анализа фото {used}/{limit}. /subscription",
    "quota_image_gen_monthly": (
        "⚠️ Лимит картинок на этот месяц исчерпан ({used} из {limit}).\n\n"
        "Генерация изображений включена в ваш тариф, но количество созданий в месяц ограничено. "
        "Лимит обновится в начале следующего месяца, либо можно перейти на тариф с большим лимитом.\n\n"
        "Подробнее: /subscription"
    ),
    "quota_image_gen_detail": (
        "🎨 <b>Создание картинок недоступно на тарифе Free</b>\n\n"
        "Вы отправили запрос на генерацию изображения (например, «нарисуй…», «создай картинку…»). "
        "На бесплатном тарифе доступны текстовые ответы AI и другие разделы бота, "
        "но <b>генерация изображений по описанию не включена</b> — это отдельная функция: "
        "она использует модель GPT-Image и списывает AI-кредиты за каждую картинку."
    ),
    "quota_image_gen_monthly_detail": (
        "⚠️ <b>Лимит картинок на этот месяц исчерпан</b> ({used} из {limit}).\n\n"
        "Генерация изображений включена в ваш тариф, но количество созданий в месяц ограничено. "
        "Лимит обновится в начале следующего месяца, либо перейдите на тариф с большим лимитом."
    ),
    "quota_image_gen_plans_title": "💳 <b>Тарифы с генерацией изображений</b>",
    "quota_image_gen_plan_line": "{emoji} {name} — <b>{images}</b> карт./мес · {price}",
    "quota_image_gen": (
        "🎨 <b>Создание картинок недоступно на тарифе Free</b>\n\n"
        "Вы отправили запрос на генерацию изображения (например, «нарисуй…», «создай картинку…»). "
        "На бесплатном тарифе доступны текстовые ответы AI и другие разделы бота, "
        "но <b>генерация изображений по описанию не включена</b> — это отдельная функция: "
        "она использует модель GPT-Image и списывает AI-кредиты за каждую картинку.\n\n"
        "<b>Что можно сделать:</b>\n"
        "• 🎓 <b>Student</b> ($2.99) — 10 картинок в месяц\n"
        "• 🥉 <b>Basic</b> ($5.99) — 40 картинок в месяц\n"
        "• 🥈 Premium / 🥇 Pro — ещё больше\n\n"
        "Тарифы и лимиты: /subscription"
    ),
    "quota_ocr": "📄 OCR — от Basic. /subscription",
    "quota_doc_translate": "🌐 Перевод документов — от Basic. /subscription",
    "quota_pdf": "📎 PDF/DOCX — от Basic. /subscription",
    "quota_student_module": "🎓 Раздел доступен от тарифа {plan}. /subscription",
    "plan_limit_ai_daily": "{n} AI-запросов в день",
    "plan_limit_ai_monthly": "{n} AI-запросов в месяц",
    "plan_limit_reminders": "До {n} напоминаний",
    "plan_limit_reminders_unlimited": "Без лимита напоминаний",
    "plan_limit_storage_mb": "Хранилище {n} МБ",
    "plan_limit_storage_gb": "Хранилище {n} ГБ",
    "plan_limit_vault_basic": "Личное хранилище: загрузка документов",
    "plan_limit_vault_lock": "🔐 Защищённый сейф: пароль на хранилище",
    "plan_all_modules": "Все модули доступны",
    "plan_feature_voice": "Голосовые сообщения",
    "plan_feature_photo": "AI-анализ фото",
    "plan_feature_priority": "Приоритетная скорость",
    "plan_feature_premium_model": "Приоритетная AI-модель",
    "quota_ai_daily": "⚠️ Дневной лимит AI исчерпан. /subscription",
    "quota_ai_monthly": "⚠️ Месячный лимит AI исчерпан. /subscription",
    "quota_voice": "🎤 Голос — от Basic. /subscription",
    "quota_vault_lock": (
        "🔐 <b>Защищённый сейф — от тарифа Student</b>\n\n"
        "В «Личное хранилище» можно сохранять паспорт, полисы, чеки и другие документы. "
        "На платных тарифах сейф дополнительно <b>защищается паролем</b>: без него раздел не откроется, "
        "а записи не попадут в общий поиск.\n\n"
        "На Free сейф работает, но без пароля."
    ),
    "quota_photo_ai": "📷 AI-фото — от Basic. /subscription",
    "quota_reminders": "⚠️ Лимит напоминаний {used}/{limit}. /subscription",
    "quota_memory": "⚠️ Лимит памяти {used}/{limit}. /subscription",
    "quota_storage": "⚠️ Хранилище {used}/{limit} МБ. /subscription",
    "quota_pdf_monthly": "⚠️ Лимит PDF/DOCX {used}/{limit}. /subscription",
    "edu_export_no_previous": "📎 Сначала попросите конспект по теме — затем можно запросить PDF, Word или другой формат.",
    "edu_export_failed": "⚠️ Не удалось создать файл. Попробуйте ещё раз или выберите другой формат.",
    "edu_export_sent": "📎 {format}: {title}",
    "edu_export_format_pdf": "PDF",
    "edu_export_format_docx": "Word (DOCX)",
    "edu_export_format_txt": "Текст (TXT)",
    "edu_export_format_md": "Markdown",
    "edu_long_notes_wait": "{emoji} Готовлю большой конспект по «{module}»… Это может занять 1–3 минуты.",
    "ai_request_failed": "⚠️ Не удалось получить ответ AI. Попробуйте ещё раз или сократите запрос (например, 3–5 страниц).",
    "quota_ai_credits": "⚠️ Недостаточно AI-кредитов. /subscription",
    "quota_ai_credits_detail": (
        "⚠️ <b>Недостаточно AI-кредитов</b>\n\n"
        "Стоимость запроса: <b>{cost}</b> AI-кредитов\n"
        "У вас осталось: <b>{left}</b> AI-кредитов"
    ),
    "quota_ai_credits_plans_title": "💳 <b>Тарифы</b>",
    "quota_ai_credits_plan_line": "{emoji} {name} — <b>{credits}</b> кред./мес · {price}",
    "quota_ai_credits_packages_title": "📦 <b>Пакеты кредитов</b> (разово, не сгорают)",
    "quota_ai_credits_pay_title": "💰 <b>Способы оплаты</b>",
    "quota_ai_credits_pay_line": "• {method}",
    "quota_ai_credits_cta": "Выберите тариф или пакет кнопками ниже 👇",
    "quota_ai_credits_btn_plans": "💳 Тарифы",
    "quota_ai_credits_btn_packages": "📦 Пакеты кредитов",
    "sub_credits_total": "💎 AI-кредитов в месяце: {total}",
    "sub_credits_used": "📉 Использовано: {used}",
    "sub_credits_left": "✅ Осталось: {left}",
    "sub_credits_bonus": "🎁 Бонусные кредиты: {bonus}",
    "sub_max_output": "📄 Макс. объём ответа: до {tokens} токенов (техн.)",
    "plan_limit_credits_monthly": "{n} AI-кредитов в месяц",
    "plan_limit_max_output": "Ответы до {n} токенов за часть",
    "plan_models_free": "GPT-4o Mini",
    "plan_models_student": "GPT-4o Mini, GPT-5.4 Mini",
    "plan_models_basic": "GPT-4o Mini, GPT-5.4 Mini",
    "plan_models_premium": "GPT-4o Mini, GPT-5.4 Mini, GPT-5.5",
    "plan_models_pro": "GPT-4o Mini, GPT-5.4 Mini, GPT-5.5",
    "plan_pkg_credits_500": "💎 +500 AI-кредитов",
    "plan_pkg_credits_2000": "💎 +2000 AI-кредитов",
    "plan_pkg_credits_5000": "💎 +5000 AI-кредитов",
    "plan_pkg_credits_10000": "💎 +10000 AI-кредитов",
    "admin_user_credits_profit": "💰 OpenAI ~${openai_usd:.2f} · кредиты {credits_used} · оценка маржи ~${margin:.2f}",
}

EXTRA_UZ: dict[str, str] = {
    "dash_greeting_morning": "Xayrli tong, {name} 👋",
    "dash_greeting_day": "Xayrli kun, {name} 👋",
    "dash_greeting_evening": "Xayrli kech, {name} 👋",
    "dash_greeting_night": "Xayrli tun, {name} 👋",
    "dash_friend": "do'st",
    "dash_today": "Bugun",
    "dash_today_empty": "Bugun tinch ✨",
    "dash_timeline": "Yaqin 7 kun",
    "dash_what_todo": "Nima qilamiz?",
    "dash_time_now": "hozir",
    "dash_time_in_min": "{n} daqiqadan keyin",
    "dash_time_in_hours": "{n} soatdan keyin",
    "dash_time_tomorrow": "ertaga",
    "dash_time_in_days": "{n} kundan keyin",
    "dash_credit_today": "Bugun to'lov: {title}",
    "dash_credit_tomorrow": "Ertaga to'lov: {title}",
    "dash_morning_title": "☀️ Xayrli tong!",
    "dash_daily_tip": "Savol yozing yoki 📷 yuboring.",
    "btn_scan": "📷 Skaner",
    "btn_sos": "🚨 SOS",
    "btn_all_modules_short": "📂 Bo'limlar",
    "btn_household": "👨‍👩‍👧 Oilaviy kirish",
    "btn_household_join": "➕ Taklif kodini kiriting",
    "household_join_prompt": "Oilaviy akkaunt egasining taklif kodini kiriting:",
    "all_modules_pick": "📂 <b>Barcha bo'limlar</b>\n\nTanlang:",
    "scan_prompt": "📷 <b>Skaner</b>\n\nRasm yuboring — AI turi aniqlaydi va arxivga saqlaydi.",
    "scan_saved": "✅ {folder} ga saqlandi",
    "remember_saved": "✅ Eslab qoldim: {text}",
    "family_rel_pet": "🐶 Uy hayvoni",
    "household_info": "👨‍👩‍👧 Kod: <code>{code}</code>\n/join {code}",
    "household_join_usage": "/join KOD",
    "household_join_ok": "✅ Ulanildi.",
    "household_join_not_found": "Kod topilmadi.",
    "household_join_already": "Allaqachon ulangansiz.",
    "household_copy_code": "Kod: {code}",
    "act_done": "✅",
    "act_add_car": "🚗 Avto profilga",
    "act_car_service": "🔧 TO eslatmasi",
    "act_car_insurance": "🛡 Sug'urta",
    "act_med_course": "💊 Davolash kursi",
    "act_med_remind": "⏰ Dori eslatmasi",
    "act_travel_plan": "✈️ Sayohat rejasi",
    "act_travel_passport": "🛂 Pasport",
    "act_save_memory": "🧠 Xotiraga",
    "act_save_expense": "💰 Xarajat",
    "act_hint_car_profile": "🚗 Avto modelini yozing.",
    "act_hint_car_service": "🔧 Avto → TO ochildi.",
    "act_hint_car_insurance": "🛡 «Avto → Sug'urta» bo'limi ochildi.",
    "act_hint_med_course": "💊 «Salomatlik → Dorilar» bo'limi ochildi.",
    "act_hint_med_remind": "⏰ «Salomatlik → Eslatmalar» bo'limi ochildi.",
    "act_hint_travel_plan": "✈️ «Sayohat» bo'limi ochildi.",
    "act_hint_travel_passport": "🛂 «Seyf → Pasport» bo'limi ochildi.",
    "act_hint_save_expense": "💰 «Moliya → Xarajatlar» bo'limi ochildi.",
    "act_hint_save_memory": "🧠 «Eslab qol: …» deb yozing.",
    "sos_menu": "🚨 <b>SOS — tezkor yordam</b>\n\nVaziyatni tanlang:",
    "sos_btn_first_aid": "🩹 Birinchi yordam",
    "sos_btn_phones": "📞 Telefonlar",
    "sos_btn_accident": "🚗 Yo'l-transport hodisasi",
    "sos_btn_passport": "🛂 Pasport yo'qolishi",
    "sos_btn_poison": "☠️ Zaharlanish",
    "sos_btn_burn": "🔥 Kuyish",
    "sos_first_aid": (
        "🩹 <b>Birinchi yordam</b>\n\n"
        "1. Oni va nafas olishni baholang\n"
        "2. 103 chaqiring (tez yordam)\n"
        "3. Umurtqa pog'onasi jarohati bo'lsa — harakat qilmang\n"
        "4. Qon ketayotgan bo'lsa — bosuvchi bandaj\n\n"
        "⚠️ Bu ma'lumot, shifokor o'rnini bosa olmaydi."
    ),
    "sos_phones": "📞 <b>Telefonlar (O'zbekiston)</b>\n\n103 — tez yordam\n102 — politsiya\n1015 — yong'in\n104 — gaz",
    "sos_accident": (
        "🚗 <b>Yo'l-transport hodisasi</b>\n\n"
        "1. Avariya chiroqlarini yoqing\n"
        "2. 102 chaqiring\n"
        "3. Joyni suratga oling\n"
        "4. Tushunarsiz hujjatlarga imzo qo'ymang\n"
        "5. Sug'urtaga xabar bering"
    ),
    "sos_passport": (
        "🛂 <b>Pasport yo'qolishi</b>\n\n"
        "1. Politsiyaga ariza bering\n"
        "2. Elchixona / Ichki ishlar organiga murojaat qiling\n"
        "3. Yo'qolganlik haqidagi ma'lumotnomani saqlang\n"
        "4. Chet el pasporti muddatini oldindan tekshiring"
    ),
    "sos_poison": (
        "☠️ <b>Zaharlanish</b>\n\n"
        "1. 103 chaqiring\n"
        "2. Shifokor aytmasdan qusishni majbur qilmang\n"
        "3. Qadoq / qoldiqlarni saqlang\n"
        "4. Agar hushida bo'lsangiz — suv iching"
    ),
    "sos_burn": (
        "🔥 <b>Kuyish</b>\n\n"
        "1. Suv bilan 15–20 daqiqa sovuting\n"
        "2. Pufakchalarni yormang\n"
        "3. Yog' surmang\n"
        "4. Katta maydonda — 103 chaqiring"
    ),
    "weather_unavailable": "Ob-havo vaqtincha mavjud emas.",
    "weather_now": "🌤 Hozir: {temp}°C, namlik {humidity}%, shamol {wind} m/s",
    "weather_today_range": "📈 Bugun: {tmin}°…{tmax}°C",
    "weather_uv": "☀️ UV indeksi: {uv}",
    "profile_facts_header": "Foydalanuvchi haqida ma'lum narsalar:",
    "household_members_title": "A'zolar",
    "scan_btn_expense": "💰 Xarajat yozish",
    "scan_amount_detected": "Chek summasi: {amount} UZS",
    "alert_reminder": "📋 <b>Eslatma</b>\n\n{title}\n📅 {when}{extra}",
    "alert_reminder_movie": "🎬 <b>Tez orada boshlanadi!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_event": "🎉 <b>Tez orada tadbir!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_ticket": "✈️ <b>Sayohatni unutmang!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_delivery": "📦 <b>Yetkazib berish</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_appointment": "📆 <b>Uchrashuv eslatmasi</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_custom": "🔔 <b>Eslatma</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_subscription": "📺 <b>Obuna</b>\n\n{title}\n📅 {when}{extra}",
    "alert_reminder_visa": "🛂 <b>Viza / hujjat</b>\n\n{title}\n📅 {when}{extra}",
    "reminder_generic_title": "Eslatma",
    "credits_remaining_short": "qoldiq {remaining}",
    "ntf_add_movie": "🎬 Film / shou",
    "ntf_add_event": "🎉 Tadbir",
    "ntf_add_ticket": "✈️ Reys / chipta",
    "ntf_add_delivery": "📦 Yetkazish",
    "ntf_add_appointment": "📆 Uchrashuv",
    "ntf_add_custom": "🔔 O'zimniki",
    "ntf_add_subscription": "📺 Obuna",
    "ntf_add_visa": "🛂 Viza",
    "ntf_manage_alerts": "📋 Eslatmalarim",
    "ntf_list_intro": "📋 <b>Eslatmalarim</b>\n\nFilmlar, tadbirlar, obunalar, vizalar va boshqalar.",
    "ntf_title_movie": "Film, serial yoki shou nomi:",
    "ntf_title_event": "Tadbir nomi (konsert, o'yin, uchrashuv…):",
    "ntf_title_ticket": "Reys, poyezd yoki tadbir:",
    "ntf_title_delivery": "Nima yetkaziladi (do'kon, posilka…):",
    "ntf_title_appointment": "Qayerga yozildingiz (shifokor, salon…):",
    "ntf_title_custom": "Eslatma nomi:",
    "ntf_title_subscription": "Obuna nomi (Netflix, Spotify…):",
    "ntf_title_visa": "Nom (AQSh vizasi, pasport…):",
    "ntf_datetime_prompt": "Sana va vaqt:\n<code>25.06.2026 19:30</code>",
    "ntf_notes_prompt": "Tafsilotlar (kinoteatr, joy, havola — yoki «-»):",
    "eco_src_movie": "Kino / shou",
    "eco_src_event": "Tadbir",
    "eco_src_ticket": "Sayohat",
    "eco_src_delivery": "Yetkazish",
    "eco_src_appointment": "Uchrashuv",
    "eco_src_custom": "Eslatma",
    "sub_btn_menu": "💎 Obuna va limitlar",
    "sub_menu_intro": "💎 <b>Obuna</b>\n\nBarcha bo'limlar ochiq — faqat hajm uchun to'lov.\n🎁 {days} kun Premium bepul.",
    "sub_btn_usage": "📊 Limitlarim",
    "sub_btn_plans": "💳 Tariflar",
    "sub_btn_packages": "📦 AI to'plamlari",
    "sub_btn_referral": "🎁 Do'stni taklif qilish",
    "sub_btn_buy": "Rasmiylashtirish",
    "sub_btn_back": "↩️ Orqaga",
    "quota_ai_daily": "⚠️ Kunlik AI limiti tugadi. /subscription",
    "quota_voice": "🎤 Ovoz Basic dan. /subscription",
    "quota_vault_lock": (
        "🔐 <b>Himoyalangan seyf — Student tarifidan</b>\n\n"
        "«Shaxsiy ombor»da pasport, polislar, cheklar va boshqa hujjatlarni saqlashingiz mumkin. "
        "Pullik tariflarda seyf <b>parol bilan himoyalanadi</b>: parolsiz bo'lim ochilmaydi "
        "va yozuvlar umumiy qidiruvda ko'rinmaydi.\n\n"
        "Free tarifida ombor ishlaydi, lekin parolsiz."
    ),
    "quota_photo_ai": "📷 AI-foto Basic dan. /subscription",
    "plan_price_free": "Bepul",
    "plan_basic_name": "Basic",
    "plan_premium_name": "Premium",
    "plan_pro_name": "Pro",
    "plan_family_name": "Oilaviy",
    "pay_instructions": (
        "💳 <b>To'lov arizasi #{order_id}</b>\n\n"
        "Mahsulot: {product}\n"
        "Summa: <b>{amount}</b>\n\n"
        "Kartaga <b>aniq summani</b> o'tkazing:\n"
        "<code>{card}</code>{holder_line}\n\n"
        "O'tkazgandan keyin <b>chek skrinshotini</b> (foto) yuboring."
    ),
    "pay_card_holder": "Qabul qiluvchi: {holder}",
    "pay_card_not_set": "karta sozlanmagan",
    "pay_card_not_configured": "To'lov vaqtincha mavjud emas. Admin bilan bog'laning.",
    "pay_product_invalid": "Bu tarifni rasmiylashtirib bo'lmaydi.",
    "pay_cancelled": "❌ Ariza bekor qilindi.",
    "pay_order_not_found": "Ariza topilmadi yoki allaqachon qayta ishlangan.",
    "pay_receipt_received": "✅ Chek qabul qilindi (#{order_id}). Admin tasdig'ini kuting.",
    "pay_approved": "✅ To'lov tasdiqlandi!\n\n{product} faollashtirildi.",
    "pay_rejected": "❌ To'lov tasdiqlanmadi. O'tkazma bo'lsa — adminga yozing.",
    "pay_admin_notify": "💰 <b>Yangi to'lov arizasi #{order_id}</b>",
    "admin_notify_new_user": (
        "👤 <b>Yangi foydalanuvchi</b>\n"
        "Telegram: <code>{telegram_id}</code> | {username}\n"
        "Bot tili: <b>{bot_lang}</b> | Telegram tili: {telegram_lang}\n"
        "Vaqt mintaqasi: {utc_offset}\n"
        "Tarif: {plan_id}"
    ),
    "admin_notify_ai_request": (
        "🤖 <b>AI so'rov</b>\n"
        "event: {event}\n"
        "user_id: <code>{telegram_id}</code>\n"
        "username: {username}\n"
        "lang: {user_lang}\n"
        "model: {model}\n"
        "tokens: in {prompt_tokens} / out {completion_tokens}\n"
        "message: {preview}"
    ),
    "pay_admin_order": (
        "📋 <b>Ariza #{order_id}</b>\n"
        "Foydalanuvchi: {user} (<code>{telegram_id}</code>)\n"
        "Mahsulot: {product}\n"
        "Summa: <b>{amount}</b>\n"
        "Chek: {submitted}\n"
        "Holat: {status}"
    ),
    "pay_admin_list_title": "💰 <b>To'lov arizalari</b>",
    "pay_admin_empty": "Tasdiq kutayotgan arizalar yo'q.",
    "pay_admin_receipt": "Chek skrinshoti",
    "pay_admin_approve": "✅ Tasdiqlash",
    "pay_admin_reject": "❌ Rad etish",
    "pay_admin_done_approved": "✅ Tasdiqlandi, tarif faollashtirildi.",
    "pay_admin_done_rejected": "❌ Ariza #{order_id} rad etildi.",
    "pay_admin_approved_toast": "Tasdiqlandi",
    "pay_admin_rejected_toast": "Rad etildi",
    "pay_admin_pending_count": "⏳ To'lov arizalari: <b>{count}</b>",
    "pay_order_already_processed": "Ariza allaqachon qayta ishlangan.",
    "pay_method_choose": (
        "💳 <b>To'lov usuli</b>\n\n"
        "{product}\n"
        "Karta: <b>{uzs}</b>\n"
        "Telegram Stars: <b>{stars}</b>\n\n"
        "Usulni tanlang:"
    ),
    "pay_method_card": "💳 Kartaga o'tkazma",
    "pay_method_stars": "⭐ Telegram Stars",
    "pay_stars_invoice_desc": "{product} — Life AI Ecosystem",
    "pay_admin_stars_notify": (
        "⭐ <b>Stars to'lovi</b>\n"
        "Foydalanuvchi: {user} (<code>{telegram_id}</code>)\n"
        "Mahsulot: {product}\n"
        "Summa: <b>{stars}</b>"
    ),
    "quota_pdf_monthly": "⚠️ PDF/DOCX limiti {used}/{limit}. /subscription",
    "edu_export_no_previous": "📎 Avval mavzu bo'yicha konspekt so'rang — keyin PDF, Word yoki boshqa format.",
    "edu_export_failed": "⚠️ Fayl yaratib bo'lmadi. Qayta urinib ko'ring yoki boshqa format tanlang.",
    "edu_export_sent": "📎 {format}: {title}",
    "edu_export_format_pdf": "PDF",
    "edu_export_format_docx": "Word (DOCX)",
    "edu_export_format_txt": "Matn (TXT)",
    "edu_export_format_md": "Markdown",
    "edu_long_notes_wait": "{emoji} «{module}» bo'yicha katta konspekt tayyorlanmoqda… 1–3 daqiqa kuting.",
    "ai_request_failed": "⚠️ AI javobini olish mumkin emas. Qayta urinib ko'ring yoki so'rovni qisqartiring (masalan, 3–5 bet).",
    "quota_ai_credits": "⚠️ AI-kreditlar yetarli emas. /subscription",
    "quota_ai_credits_detail": (
        "⚠️ <b>AI-kreditlar yetarli emas</b>\n\n"
        "So'rov narxi: <b>{cost}</b> AI-kredit\n"
        "Qolgan: <b>{left}</b> AI-kredit"
    ),
    "quota_ai_credits_plans_title": "💳 <b>Tariflar</b>",
    "quota_ai_credits_plan_line": "{emoji} {name} — <b>{credits}</b> kredit/oy · {price}",
    "quota_ai_credits_packages_title": "📦 <b>Kredit paketlari</b> (bir martalik)",
    "quota_ai_credits_pay_title": "💰 <b>To'lov usullari</b>",
    "quota_ai_credits_pay_line": "• {method}",
    "quota_ai_credits_cta": "Quyidagi tugmalardan tarif yoki paketni tanlang 👇",
    "quota_ai_credits_btn_plans": "💳 Tariflar",
    "quota_ai_credits_btn_packages": "📦 Kredit paketlari",
    "quota_image_gen_monthly": (
        "⚠️ Bu oy uchun rasm yaratish limiti tugadi ({used} / {limit}).\n\n"
        "Tarifingizda rasm yaratish bor, lekin oyiga cheklangan. "
        "Limit yangi oy boshida yangilanadi yoki kattaroq limitli tarifga o'ting.\n\n"
        "Batafsil: /subscription"
    ),
    "quota_image_gen_detail": (
        "🎨 <b>Free tarifida rasm yaratish yo'q</b>\n\n"
        "Siz rasm yaratish so'rovi yubordingiz (masalan, «chiz…», «rasm yarat…»). "
        "Bepul tarifda matnli AI va boshqa bo'limlar ishlaydi, "
        "lekin <b>tavsif bo'yicha rasm yaratish kirmaydi</b> — bu alohida funksiya: "
        "GPT-Image modeli ishlatiladi va har bir rasm uchun AI-kredit yechiladi."
    ),
    "quota_image_gen_monthly_detail": (
        "⚠️ <b>Bu oy uchun rasm yaratish limiti tugadi</b> ({used} / {limit}).\n\n"
        "Tarifingizda rasm yaratish bor, lekin oyiga cheklangan. "
        "Limit yangi oy boshida yangilanadi yoki kattaroq limitli tarifga o'ting."
    ),
    "quota_image_gen_plans_title": "💳 <b>Rasm yaratishli tariflar</b>",
    "quota_image_gen_plan_line": "{emoji} {name} — <b>{images}</b> rasm/oy · {price}",
    "quota_image_gen": (
        "🎨 <b>Free tarifida rasm yaratish yo'q</b>\n\n"
        "Siz rasm yaratish so'rovi yubordingiz (masalan, «chiz…», «rasm yarat…»). "
        "Bepul tarifda matnli AI va boshqa bo'limlar ishlaydi, "
        "lekin <b>tavsif bo'yicha rasm yaratish kirmaydi</b> — bu alohida funksiya: "
        "GPT-Image modeli ishlatiladi va har bir rasm uchun AI-kredit yechiladi.\n\n"
        "<b>Nima qilish mumkin:</b>\n"
        "• 🎓 <b>Student</b> ($2.99) — oyiga 10 rasm\n"
        "• 🥉 <b>Basic</b> ($5.99) — oyiga 40 rasm\n"
        "• 🥈 Premium / 🥇 Pro — yanada ko'p\n\n"
        "Tariflar: /subscription"
    ),
    "sub_credits_total": "💎 Oylik AI-kreditlar: {total}",
    "sub_credits_used": "📉 Sarflangan: {used}",
    "sub_credits_left": "✅ Qolgan: {left}",
    "sub_credits_bonus": "🎁 Bonus kreditlar: {bonus}",
    "sub_max_output": "📄 Javob hajmi: qismiga {tokens} tokengacha",
    "plan_limit_credits_monthly": "Oyiga {n} AI-kredit",
    "plan_limit_max_output": "Qismiga {n} tokengacha javob",
    "plan_models_free": "GPT-4o Mini",
    "plan_models_student": "GPT-4o Mini, GPT-5.4 Mini",
    "plan_models_basic": "GPT-4o Mini, GPT-5.4 Mini",
    "plan_models_premium": "GPT-4o Mini, GPT-5.4 Mini, GPT-5.5",
    "plan_models_pro": "GPT-4o Mini, GPT-5.4 Mini, GPT-5.5",
    "plan_pkg_credits_500": "💎 +500 AI-kredit",
    "plan_pkg_credits_2000": "💎 +2000 AI-kredit",
    "plan_pkg_credits_5000": "💎 +5000 AI-kredit",
    "plan_pkg_credits_10000": "💎 +10000 AI-kredit",
    "admin_user_credits_profit": "💰 OpenAI ~${openai_usd:.2f} · kreditlar {credits_used} · marja ~${margin:.2f}",
}

EXTRA_EN: dict[str, str] = {
    "dash_greeting_morning": "Good morning, {name} 👋",
    "dash_greeting_day": "Good afternoon, {name} 👋",
    "dash_greeting_evening": "Good evening, {name} 👋",
    "dash_greeting_night": "Good night, {name} 👋",
    "dash_friend": "friend",
    "dash_today": "Today",
    "dash_today_empty": "All clear for today ✨",
    "dash_timeline": "Next 7 days",
    "dash_what_todo": "What would you like to do?",
    "dash_time_now": "now",
    "dash_time_in_min": "in {n} min",
    "dash_time_in_hours": "in {n} h",
    "dash_time_tomorrow": "tomorrow",
    "dash_time_in_days": "in {n} days",
    "dash_credit_today": "Payment today: {title}",
    "dash_credit_tomorrow": "Payment tomorrow: {title}",
    "dash_morning_title": "☀️ Good morning!",
    "dash_daily_tip": "Ask a question or send 📷 — the bot will figure it out.",
    "btn_scan": "📷 Scan",
    "btn_sos": "🚨 SOS",
    "btn_all_modules_short": "📂 Sections",
    "btn_household": "👨‍👩‍👧 Family access",
    "btn_household_join": "➕ Enter invite code",
    "household_join_prompt": "Enter the invite code from the family owner:",
    "all_modules_pick": "📂 <b>All sections</b>\n\nPick one:",
    "scan_prompt": "📷 <b>Universal scanner</b>\n\nSend a photo — AI classifies and archives it.",
    "scan_saved": "✅ Saved to {folder}",
    "remember_saved": "✅ Remembered: {text}",
    "family_rel_pet": "🐶 Pet",
    "household_info": "👨‍👩‍👧 Invite code: <code>{code}</code>\n/join {code}",
    "household_join_usage": "Format: /join CODE",
    "household_join_ok": "✅ Joined family account.",
    "household_join_not_found": "Code not found.",
    "household_join_already": "Already in a household.",
    "household_copy_code": "Code: {code}",
    "act_done": "✅",
    "act_add_car": "🚗 Add car to profile",
    "act_car_service": "🔧 Service reminder",
    "act_car_insurance": "🛡 Insurance",
    "act_med_course": "💊 Treatment course",
    "act_med_remind": "⏰ Med reminders",
    "act_travel_plan": "✈️ Trip plan",
    "act_travel_passport": "🛂 Passport check",
    "act_save_memory": "🧠 Save to memory",
    "act_save_expense": "💰 Log expense",
    "act_hint_car_profile": "🚗 Type your car model — I'll save it.",
    "act_hint_car_service": "🔧 Car → Service is open.",
    "act_hint_car_insurance": "🛡 Car → Insurance is open.",
    "act_hint_med_course": "💊 Health → Medications is open.",
    "act_hint_med_remind": "⏰ Health → Med reminders is open.",
    "act_hint_travel_plan": "✈️ Travel is open.",
    "act_hint_travel_passport": "🛂 Vault → Passport is open.",
    "act_hint_save_expense": "💰 Finance → Expenses is open.",
    "act_hint_save_memory": "🧠 Type «Remember: …» to save forever.",
    "sos_menu": "🚨 <b>SOS — emergency help</b>\n\nPick a situation:",
    "sos_btn_first_aid": "🩹 First aid",
    "sos_btn_phones": "📞 Phone numbers",
    "sos_btn_accident": "🚗 Car accident",
    "sos_btn_passport": "🛂 Lost passport",
    "sos_btn_poison": "☠️ Poisoning",
    "sos_btn_burn": "🔥 Burn",
    "sos_first_aid": (
        "🩹 <b>First aid</b>\n\n"
        "1. Check consciousness and breathing\n"
        "2. Call 103 (ambulance)\n"
        "3. Don't move the person if you suspect a spinal injury\n"
        "4. For bleeding — apply direct pressure\n\n"
        "⚠️ This is guidance only, not a substitute for a doctor."
    ),
    "sos_phones": (
        "📞 <b>Phone numbers (Uzbekistan)</b>\n\n"
        "103 — ambulance\n"
        "102 — police\n"
        "1015 — fire service\n"
        "104 — gas emergency"
    ),
    "sos_accident": (
        "🚗 <b>Car accident</b>\n\n"
        "1. Turn on hazard lights\n"
        "2. Call 102\n"
        "3. Take photos of the scene\n"
        "4. Don't sign unclear paperwork\n"
        "5. Notify your insurer"
    ),
    "sos_passport": (
        "🛂 <b>Lost passport</b>\n\n"
        "1. File a report with the police\n"
        "2. Contact the embassy / MVD\n"
        "3. Keep the loss certificate\n"
        "4. Check your passport expiry date in advance"
    ),
    "sos_poison": (
        "☠️ <b>Poisoning</b>\n\n"
        "1. Call 103\n"
        "2. Don't induce vomiting unless a doctor tells you to\n"
        "3. Keep the packaging / any remaining substance\n"
        "4. Drink water only if you're conscious"
    ),
    "sos_burn": (
        "🔥 <b>Burn</b>\n\n"
        "1. Cool with water for 15–20 minutes\n"
        "2. Don't pop blisters\n"
        "3. Don't apply oil or grease\n"
        "4. For large burns — call 103"
    ),
    "weather_unavailable": "Weather temporarily unavailable.",
    "weather_now": "🌤 Now: {temp}°C, humidity {humidity}%, wind {wind} m/s",
    "weather_today_range": "📈 Today: {tmin}°…{tmax}°C",
    "weather_uv": "☀️ UV index: {uv}",
    "profile_facts_header": "Known facts about the user:",
    "household_members_title": "Members",
    "scan_btn_expense": "💰 Log expense",
    "scan_amount_detected": "Receipt amount: {amount} UZS",
    "alert_reminder": "📋 <b>Reminder</b>\n\n{title}\n📅 {when}{extra}",
    "alert_reminder_movie": "🎬 <b>Starting soon!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_event": "🎉 <b>Event coming up!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_ticket": "✈️ <b>Don't miss your trip!</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_delivery": "📦 <b>Delivery expected</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_appointment": "📆 <b>Appointment reminder</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_custom": "🔔 <b>Reminder</b>\n\n{title}\n🕐 {when}{extra}",
    "alert_reminder_subscription": "📺 <b>Subscription</b>\n\n{title}\n📅 {when}{extra}",
    "alert_reminder_visa": "🛂 <b>Visa / document</b>\n\n{title}\n📅 {when}{extra}",
    "reminder_generic_title": "Reminder",
    "credits_remaining_short": "rem. {remaining}",
    "ntf_add_movie": "🎬 Movie / show",
    "ntf_add_event": "🎉 Event",
    "ntf_add_ticket": "✈️ Flight / ticket",
    "ntf_add_delivery": "📦 Delivery",
    "ntf_add_appointment": "📆 Appointment",
    "ntf_add_custom": "🔔 Custom",
    "ntf_add_subscription": "📺 Subscription",
    "ntf_add_visa": "🛂 Visa",
    "ntf_manage_alerts": "📋 My reminders",
    "ntf_list_intro": "📋 <b>My reminders</b>\n\nMovies, events, subscriptions, visas & more.",
    "ntf_title_movie": "Movie, series or show title:",
    "ntf_title_event": "Event name (concert, match, party…):",
    "ntf_title_ticket": "Flight, train or trip:",
    "ntf_title_delivery": "What is being delivered:",
    "ntf_title_appointment": "Where you're booked (doctor, salon…):",
    "ntf_title_custom": "Reminder title:",
    "ntf_title_subscription": "Subscription name (Netflix, Spotify…):",
    "ntf_title_visa": "Title (US visa, passport expiry…):",
    "ntf_datetime_prompt": "Date and time:\n<code>25.06.2026 19:30</code>",
    "ntf_notes_prompt": "Details (cinema, seat, link — or «-»):",
    "eco_src_movie": "Movie / show",
    "eco_src_event": "Event",
    "eco_src_ticket": "Trip",
    "eco_src_delivery": "Delivery",
    "eco_src_appointment": "Appointment",
    "eco_src_custom": "Reminder",
    "btn_subscription": "💎 Subscription",
    "sub_btn_menu": "💎 Subscription & limits",
    "sub_btn_usage": "📊 My limits",
    "sub_btn_plans": "💳 Plans",
    "sub_btn_packages": "📦 AI packages",
    "sub_btn_referral": "🎁 Invite a friend",
    "sub_btn_buy": "Subscribe",
    "sub_btn_back": "↩️ Back",
    "sub_menu_intro": (
        "💎 <b>Subscription & limits</b>\n\n"
        "All modules are open — you pay for volume.\n"
        "Prices in UZS (CBU rate ~12,017 UZS / $1).\n\n"
        "🎁 First {days} days — Premium free."
    ),
    "sub_plans_title": "💳 <b>Plans</b>",
    "sub_plans_hint": "Tap a plan for details or Subscribe.",
    "sub_packages_title": "📦 <b>AI request packages</b>",
    "sub_packages_hint": "One-time purchase — bonus requests don't expire.",
    "sub_package_line": "• {name}: <b>{requests}</b> requests — <b>{price}</b>",
    "sub_usage_title": "📊 <b>Your limits</b>",
    "sub_current_plan": "Plan: {plan}",
    "sub_trial_until": "🎁 Premium trial until {date}",
    "sub_paid_until": "Paid until {date}",
    "sub_ai_daily": "AI today: {used} / {limit}",
    "sub_ai_monthly": "AI this month: {used} / {limit}",
    "sub_ai_bonus": "Bonus requests: {bonus}",
    "sub_storage_limit": "Storage: up to {limit} MB",
    "sub_vault_lock_on": "🔐 Protected vault: password lock",
    "sub_vault_lock_off": "🔐 Vault: no password (protection from Student)",
    "sub_memory_limit": "AI memory: up to {limit} facts",
    "sub_memory_unlimited": "AI memory: unlimited",
    "sub_referral_info": (
        "🎁 <b>Invite a friend</b>\n\n"
        "You both get <b>{bonus}</b> AI requests.\n\n"
        "Link:\n{link}\n\nCode: <code>{code}</code>"
    ),
    "sub_referral_applied": "🎁 Referral bonus applied!",
    "sub_trial_welcome": "🎁 Premium for {days} days + {bonus} AI requests. /subscription",
    "sub_buy_plan": "💳 <b>{plan}</b>\n<b>{price}</b> / month\n\nPay via: {contact}",
    "sub_buy_package": "📦 <b>{name}</b> — {requests} requests\n<b>{price}</b>\n\nPay via: {contact}",
    "sub_payment_default": "the bot admin",
    "pay_instructions": (
        "💳 <b>Payment order #{order_id}</b>\n\n"
        "Product: {product}\n"
        "Amount: <b>{amount}</b>\n\n"
        "Transfer the <b>exact amount</b> to:\n"
        "<code>{card}</code>{holder_line}\n\n"
        "Then send a <b>receipt screenshot</b> (photo) here."
    ),
    "pay_card_holder": "Recipient: {holder}",
    "pay_card_not_set": "card not configured",
    "pay_card_not_configured": "Payments are temporarily unavailable. Contact admin.",
    "pay_product_invalid": "This plan cannot be purchased.",
    "pay_cancelled": "❌ Order cancelled.",
    "pay_order_not_found": "Order not found or already processed.",
    "pay_receipt_received": "✅ Receipt received (order #{order_id}). Awaiting admin confirmation.",
    "pay_approved": "✅ Payment confirmed!\n\n{product} activated.",
    "pay_rejected": "❌ Payment not confirmed. If you paid, contact admin.",
    "pay_admin_notify": "💰 <b>New payment order #{order_id}</b>",
    "admin_notify_new_user": (
        "👤 <b>New user</b>\n"
        "Telegram: <code>{telegram_id}</code> | {username}\n"
        "Bot language: <b>{bot_lang}</b> | Telegram language: {telegram_lang}\n"
        "Timezone: {utc_offset}\n"
        "Plan: {plan_id}"
    ),
    "admin_notify_ai_request": (
        "🤖 <b>AI request</b>\n"
        "event: {event}\n"
        "user_id: <code>{telegram_id}</code>\n"
        "username: {username}\n"
        "lang: {user_lang}\n"
        "model: {model}\n"
        "tokens: in {prompt_tokens} / out {completion_tokens}\n"
        "message: {preview}"
    ),
    "pay_admin_order": (
        "📋 <b>Order #{order_id}</b>\n"
        "User: {user} (<code>{telegram_id}</code>)\n"
        "Product: {product}\n"
        "Amount: <b>{amount}</b>\n"
        "Receipt: {submitted}\n"
        "Status: {status}"
    ),
    "pay_admin_list_title": "💰 <b>Payment orders</b>",
    "pay_admin_empty": "No orders awaiting confirmation.",
    "pay_admin_receipt": "Receipt screenshot",
    "pay_admin_approve": "✅ Approve",
    "pay_admin_reject": "❌ Reject",
    "pay_admin_done_approved": "✅ Approved, plan activated.",
    "pay_admin_done_rejected": "❌ Order #{order_id} rejected.",
    "pay_admin_approved_toast": "Approved",
    "pay_admin_rejected_toast": "Rejected",
    "pay_admin_pending_count": "⏳ Pending payments: <b>{count}</b>",
    "pay_order_already_processed": "Order already processed.",
    "pay_method_choose": (
        "💳 <b>Payment method</b>\n\n"
        "{product}\n"
        "Card: <b>{uzs}</b>\n"
        "Telegram Stars: <b>{stars}</b>\n\n"
        "Choose:"
    ),
    "pay_method_card": "💳 Bank card transfer",
    "pay_method_stars": "⭐ Telegram Stars",
    "pay_stars_invoice_desc": "{product} — Life AI Ecosystem",
    "pay_admin_stars_notify": (
        "⭐ <b>Stars payment</b>\n"
        "User: {user} (<code>{telegram_id}</code>)\n"
        "Product: {product}\n"
        "Amount: <b>{stars}</b>"
    ),
    "plan_price_free": "Free",
    "plan_price_monthly": "<b>{price}</b> / mo (~${usd})",
    "plan_free_name": "Free",
    "plan_free_desc": "GPT-4o Mini, document vault, AI and photo limits.",
    "plan_basic_name": "Basic",
    "plan_basic_desc": "GPT-5.4 Mini, voice, password-protected vault, 40 images/mo.",
    "plan_premium_name": "Premium",
    "plan_premium_desc": "GPT-5.5, family up to 5, protected vault, 120 images/mo.",
    "plan_pro_name": "Pro",
    "plan_pro_desc": "Max AI, family up to 10, protected vault, 400 images/mo.",
    "plan_family_name": "Family",
    "plan_family_desc": "Up to 5 people.",
    "plan_pkg_100": "100 AI requests",
    "plan_pkg_500": "500 AI requests",
    "plan_pkg_1000": "1000 AI requests",
    "plan_limit_ai_daily": "{n} AI requests per day",
    "plan_limit_ai_monthly": "{n} AI requests per month",
    "plan_limit_reminders": "Up to {n} reminders",
    "plan_limit_reminders_unlimited": "Unlimited reminders",
    "plan_limit_storage_mb": "Storage {n} MB",
    "plan_limit_storage_gb": "Storage {n} GB",
    "plan_limit_vault_basic": "Personal vault: upload documents",
    "plan_limit_vault_lock": "🔐 Protected vault: password lock",
    "plan_all_modules": "All modules available",
    "plan_feature_voice": "Voice messages",
    "plan_feature_photo": "AI photo analysis",
    "plan_feature_priority": "Priority speed",
    "plan_feature_premium_model": "Premium AI model",
    "quota_ai_daily": "⚠️ Daily AI limit reached. /subscription",
    "quota_ai_monthly": "⚠️ Monthly AI limit reached. /subscription",
    "quota_voice": "🎤 Voice from Basic plan. /subscription",
    "quota_vault_lock": (
        "🔐 <b>Protected vault — from Student plan</b>\n\n"
        "Save passport scans, policies, receipts and other documents in Personal vault. "
        "On paid plans the vault is <b>password-protected</b>: it won't open without the password, "
        "and entries are hidden from global search.\n\n"
        "On Free the vault works, but without a password."
    ),
    "quota_photo_ai": "📷 AI photos from Basic. /subscription",
    "quota_reminders": "⚠️ Reminder limit {used}/{limit}. /subscription",
    "quota_memory": "⚠️ Memory limit {used}/{limit}. /subscription",
    "quota_storage": "⚠️ Storage full {used}/{limit} MB. /subscription",
    "quota_pdf_monthly": "⚠️ PDF/DOCX limit {used}/{limit}. /subscription",
    "edu_export_no_previous": "📎 Ask for study notes on a topic first — then request PDF, Word, or another format.",
    "edu_export_failed": "⚠️ Could not create the file. Try again or pick another format.",
    "edu_export_sent": "📎 {format}: {title}",
    "edu_export_format_pdf": "PDF",
    "edu_export_format_docx": "Word (DOCX)",
    "edu_export_format_txt": "Text (TXT)",
    "edu_export_format_md": "Markdown",
    "edu_long_notes_wait": "{emoji} Preparing a large study guide on «{module}»… This may take 1–3 minutes.",
    "ai_request_failed": "⚠️ Could not get an AI response. Try again or shorten the request (e.g. 3–5 pages).",
    "quota_ai_credits": "⚠️ Not enough AI credits. /subscription",
    "quota_ai_credits_detail": (
        "⚠️ <b>Not enough AI credits</b>\n\n"
        "Request cost: <b>{cost}</b> AI credits\n"
        "You have left: <b>{left}</b> AI credits"
    ),
    "quota_ai_credits_plans_title": "💳 <b>Plans</b>",
    "quota_ai_credits_plan_line": "{emoji} {name} — <b>{credits}</b> credits/mo · {price}",
    "quota_ai_credits_packages_title": "📦 <b>Credit packs</b> (one-time, no expiry)",
    "quota_ai_credits_pay_title": "💰 <b>Payment methods</b>",
    "quota_ai_credits_pay_line": "• {method}",
    "quota_ai_credits_cta": "Choose a plan or pack with the buttons below 👇",
    "quota_ai_credits_btn_plans": "💳 Plans",
    "quota_ai_credits_btn_packages": "📦 Credit packs",
    "quota_image_gen_monthly": (
        "⚠️ Image generation limit reached for this month ({used} of {limit}).\n\n"
        "Your plan includes image generation, but the number of images per month is limited. "
        "The limit resets at the start of next month, or you can upgrade to a plan with a higher cap.\n\n"
        "Details: /subscription"
    ),
    "quota_image_gen_detail": (
        "🎨 <b>Image generation is not available on the Free plan</b>\n\n"
        "You sent a request to create an image (e.g. “draw…”, “generate a picture…”). "
        "On the free plan you can use text AI and other bot sections, "
        "but <b>image generation from a text prompt is not included</b> — it's a separate feature: "
        "it uses the GPT-Image model and spends AI credits per image."
    ),
    "quota_image_gen_monthly_detail": (
        "⚠️ <b>Image generation limit reached for this month</b> ({used} of {limit}).\n\n"
        "Your plan includes image generation, but the number of images per month is limited. "
        "The limit resets at the start of next month, or upgrade to a plan with a higher cap."
    ),
    "quota_image_gen_plans_title": "💳 <b>Plans with image generation</b>",
    "quota_image_gen_plan_line": "{emoji} {name} — <b>{images}</b> images/mo · {price}",
    "quota_image_gen": (
        "🎨 <b>Image generation is not available on the Free plan</b>\n\n"
        "You sent a request to create an image (e.g. “draw…”, “generate a picture…”). "
        "On the free plan you can use text AI and other bot sections, "
        "but <b>image generation from a text prompt is not included</b> — it's a separate feature: "
        "it uses the GPT-Image model and spends AI credits per image.\n\n"
        "<b>What you can do:</b>\n"
        "• 🎓 <b>Student</b> ($2.99) — 10 images per month\n"
        "• 🥉 <b>Basic</b> ($5.99) — 40 images per month\n"
        "• 🥈 Premium / 🥇 Pro — even more\n\n"
        "Plans: /subscription"
    ),
    "sub_credits_total": "💎 Monthly AI credits: {total}",
    "sub_credits_used": "📉 Used: {used}",
    "sub_credits_left": "✅ Left: {left}",
    "sub_credits_bonus": "🎁 Bonus credits: {bonus}",
    "sub_max_output": "📄 Max response chunk: up to {tokens} tokens (technical)",
    "plan_limit_credits_monthly": "{n} AI credits per month",
    "plan_limit_max_output": "Responses up to {n} tokens per part",
    "plan_models_free": "GPT-4o Mini",
    "plan_models_student": "GPT-4o Mini, GPT-5.4 Mini",
    "plan_models_basic": "GPT-4o Mini, GPT-5.4 Mini",
    "plan_models_premium": "GPT-4o Mini, GPT-5.4 Mini, GPT-5.5",
    "plan_models_pro": "GPT-4o Mini, GPT-5.4 Mini, GPT-5.5",
    "plan_pkg_credits_500": "💎 +500 AI credits",
    "plan_pkg_credits_2000": "💎 +2000 AI credits",
    "plan_pkg_credits_5000": "💎 +5000 AI credits",
    "plan_pkg_credits_10000": "💎 +10000 AI credits",
    "admin_user_credits_profit": "💰 OpenAI ~${openai_usd:.2f} · credits {credits_used} · est. margin ~${margin:.2f}",
}
