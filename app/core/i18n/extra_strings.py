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
}
