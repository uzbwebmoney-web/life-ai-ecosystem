from __future__ import annotations



from dataclasses import dataclass





@dataclass(frozen=True)

class SubmoduleDef:

    id: str

    title_ru: str

    title_uz: str

    title_en: str



    def title(self, lang: str = "ru") -> str:

        if lang == "uz":

            return self.title_uz

        if lang == "en":

            return self.title_en

        return self.title_ru





@dataclass(frozen=True)

class ModuleDef:

    id: str

    emoji: str

    title_ru: str

    title_uz: str

    title_en: str

    phase: int

    category_ru: str

    ai_hint_ru: str

    submodules: tuple[SubmoduleDef, ...]



    def title(self, lang: str = "ru") -> str:

        if lang == "uz":

            return self.title_uz

        if lang == "en":

            return self.title_en

        return self.title_ru





def _sub(sid: str, ru: str, uz: str | None = None, en: str | None = None) -> SubmoduleDef:

    return SubmoduleDef(sid, ru, uz or ru, en or ru)





MODULES: tuple[ModuleDef, ...] = (

    ModuleDef(

        "health", "🩺", "Здоровье", "Salomatlik", "Health", 1, "Здоровье",

        "Симптомы, анализы, обследования, лекарства, дневник показателей, визиты к врачу, мед. документы.",

        (

            _sub("consultant", "Задать вопрос", "Savol berish", "Ask a question"),

            _sub("symptoms", "Симптомы", "Alomatlar", "Symptoms"),

            _sub("tests", "Анализы", "Tahlillar", "Lab tests"),

            _sub("exams", "Обследования", "Tekshiruvlar", "Examinations"),

            _sub("medicines", "Лекарства", "Dori-darmonlar", "Medications"),

            _sub("med_reminders", "Приём лекарств", "Dori eslatmalari", "Med reminders"),

            _sub("visits", "Визиты к врачу", "Shifokor tashriflari", "Doctor visits"),

            _sub("diary", "Дневник показателей", "Ko'rsatkichlar jurnali", "Health diary"),

            _sub("documents", "Мед. документы", "Tibbiy hujjatlar", "Medical docs"),

        ),

    ),

    ModuleDef(

        "car", "🚗", "Автомобиль", "Avtomobil", "Car", 1, "Транспорт",

        "Ошибки по фото, звуки, ТО, масло/фильтры/шины, страховка, техосмотр, расходы.",

        (

            _sub("panel_photo", "Ошибки по фото", "Foto xatoliklar", "Dashboard errors"),

            _sub("sounds", "Анализ звуков", "Ovoz tahlili", "Sound analysis"),

            _sub("service", "График ТО", "TO jadvali", "Service schedule"),

            _sub("reminders", "Масло и фильтры", "Yog' va filtrlar", "Oil & filters"),

            _sub("compliance", "Страховка и ТО", "Sug'urta va texko'rik", "Insurance & inspection"),

            _sub("expenses", "Расходы на авто", "Avto xarajatlari", "Car expenses"),

        ),

    ),

    ModuleDef(

        "finance", "💰", "Финансы", "Moliya", "Finance", 1, "Деньги",

        "Доходы, расходы, цели, бюджет, счета, анализ по категориям.",

        (

            _sub("income", "Доходы", "Daromadlar", "Income"),

            _sub("expense", "Расходы", "Xarajatlar", "Expenses"),

            _sub("goals", "Финансовые цели", "Moliyaviy maqsadlar", "Financial goals"),

            _sub("budget", "Бюджет", "Byudjet", "Budget"),

            _sub("bills", "Оплата счетов", "Hisob to'lovi", "Bill payments"),

            _sub("loans", "Кредит и ипотека", "Kredit va ipoteka", "Loans & mortgage"),

            _sub("analysis", "Анализ расходов", "Xarajat tahlili", "Expense analysis"),

        ),

    ),

    ModuleDef(

        "business", "💼", "Бизнес", "Biznes", "Business", 2, "Деньги",

        "Бизнес-планы, реклама, конкуренты, договоры, клиенты, продажи.",

        (

            _sub("consultant", "Задать вопрос", "Savol berish", "Ask a question"),

            _sub("plans", "Бизнес-планы", "Biznes-rejalar", "Business plans"),

            _sub("ads", "Генерация рекламы", "Reklama yaratish", "Ad generation"),

            _sub("competitors", "Анализ конкурентов", "Raqobatchilar tahlili", "Competitor analysis"),

            _sub("contracts", "Генерация договоров", "Shartnomalar", "Contract generation"),

            _sub("client_responses", "Ответы клиентам", "Mijozlarga javoblar", "Client responses"),

            _sub("sales_analysis", "Анализ продаж", "Savdo tahlili", "Sales analysis"),

        ),

    ),

    ModuleDef(

        "legal", "⚖️", "Юридическая помощь", "Yuridik yordam", "Legal", 2, "Право",

        "Юридические вопросы, документы, заявления, законодательство, чек-листы.",

        (

            _sub("questions", "Юридические вопросы", "Yuridik savollar", "Legal Q&A"),

            _sub("doc_check", "Проверка документов", "Hujjatlarni tekshirish", "Document review"),

            _sub("applications", "Генерация заявлений", "Ariza yaratish", "Application drafts"),

            _sub("legislation", "Объяснение законов", "Qonunlar tushuntirishi", "Legislation explained"),

            _sub("checklists", "Чек-листы действий", "Harakatlar ro'yxati", "Action checklists"),

        ),

    ),

    ModuleDef(

        "travel", "✈️", "Путешествия", "Sayohat", "Travel", 2, "Транспорт",

        "Маршруты, визы, бюджет, чек-лист, переводчик, валюта.",

        (

            _sub("routes", "Планирование маршрутов", "Marshrut rejalash", "Route planning"),

            _sub("visas", "Визовая информация", "Viza ma'lumoti", "Visa information"),

            _sub("budget", "Бюджет поездки", "Sayohat byudjeti", "Trip budget"),

            _sub("packing", "Чек-лист вещей", "Narsalar ro'yxati", "Packing checklist"),

            _sub("translator", "Переводчик", "Tarjimon", "Translator"),

            _sub("currency", "Конвертер валют", "Valyuta konvertori", "Currency converter"),

        ),

    ),

    ModuleDef(

        "home", "🏠", "Дом", "Uy", "Home", 2, "Быт",

        "Коммуналка, расходы, ремонт, покупки, инвентарь.",

        (

            _sub("utilities", "Коммунальные услуги", "Kommunal to'lovlar", "Utility bills"),

            _sub("expenses", "Домашние расходы", "Uy xarajatlari", "Home expenses"),

            _sub("repair", "План ремонта", "Ta'mirlash rejasi", "Renovation plan"),

            _sub("shopping", "Список покупок", "Xaridlar ro'yxati", "Shopping list"),

            _sub("inventory", "Домашний инвентарь", "Uy inventari", "Home inventory"),

        ),

    ),

    ModuleDef(

        "shopping", "🛒", "Покупки", "Xaridlar", "Shopping", 2, "Быт",

        "Сравнение товаров, выгодные предложения, характеристики, советы по выбору.",

        (

            _sub("compare", "Сравнение товаров", "Mahsulotlarni solishtirish", "Product comparison"),

            _sub("deals", "Выгодные предложения", "Foydali takliflar", "Best deals"),

            _sub("specs", "Проверка характеристик", "Xususiyatlarni tekshirish", "Spec check"),

            _sub("advice", "Советы по выбору", "Tanlov bo'yicha maslahat", "Buying advice"),

        ),

    ),

    ModuleDef(

        "education", "📚", "Обучение", "Ta'lim", "Education", 2, "Обучение",

        "Объяснение тем, экзамены, языки, конспекты, домашние задания.",

        (

            _sub("topics", "Объяснение тем", "Mavzular tushuntirishi", "Topic explanations"),

            _sub("exams", "Подготовка к экзаменам", "Imtihonlarga tayyorgarlik", "Exam prep"),

            _sub("languages", "Изучение языков", "Tillarni o'rganish", "Language learning"),

            _sub("notes", "Генерация конспектов", "Konspekt yaratish", "Note generation"),

            _sub("homework", "Проверка ДЗ", "Uy vazifasini tekshirish", "Homework check"),

        ),

    ),


    ModuleDef(

        "nutrition", "🍽", "Питание", "Ovqatlanish", "Nutrition", 2, "Здоровье",

        "Рацион, калории, рецепты, список продуктов, учёт воды.",

        (

            _sub("diet", "Подбор рациона", "Ratsion tanlash", "Meal planning"),

            _sub("calories", "Расчёт калорий", "Kaloriya hisoblash", "Calorie calculator"),

            _sub("recipes", "Рецепты", "Retseptlar", "Recipes"),

            _sub("grocery", "Список продуктов", "Mahsulotlar ro'yxati", "Grocery list"),

            _sub("water", "Учёт воды", "Suv hisobi", "Water tracking"),

        ),

    ),

    ModuleDef(

        "fitness", "🏋️", "Фитнес", "Fitnes", "Fitness", 2, "Здоровье",

        "Планы тренировок, прогресс, напоминания о тренировках.",

        (

            _sub("workouts", "План тренировок", "Mashq rejasi", "Workout plans"),

            _sub("progress", "Отслеживание прогресса", "Progress kuzatuvi", "Progress tracking"),

            _sub("reminders", "Напоминания о тренировках", "Mashq eslatmalari", "Workout reminders"),

        ),

    ),

    ModuleDef(

        "organizer", "📅", "Органайзер", "Tashkilotchi", "Organizer", 1, "Планирование",

        "Задачи, календарь, напоминания, дни рождения, встречи, заметки.",

        (

            _sub("tasks", "Задачи", "Vazifalar", "Tasks"),

            _sub("calendar", "Календарь", "Taqvim", "Calendar"),

            _sub("reminders", "Напоминания", "Eslatmalar", "Reminders"),

            _sub("birthdays", "Дни рождения", "Tug'ilgan kunlar", "Birthdays"),

            _sub("meetings", "Встречи", "Uchrashuvlar", "Meetings"),

            _sub("notes", "Заметки", "Qaydlar", "Notes"),

        ),

    ),

    ModuleDef(

        "ai_assistant", "🤖", "AI-ассистент", "AI yordamchi", "AI assistant", 1, "AI",

        "Вопросы, переводы, документы, фото, тексты, код.",

        (

            _sub("questions", "Любые вопросы", "Har qanday savollar", "Any questions"),

            _sub("translate", "Переводы", "Tarjimalar", "Translations"),

            _sub("documents", "PDF и документы", "PDF va hujjatlar", "PDF & documents"),

            _sub("photo", "Анализ фото", "Foto tahlil", "Photo analysis"),

            _sub("images", "Создание картинок", "Rasm yaratish", "Image generation"),

            _sub("writing", "Создание текстов", "Matn yaratish", "Text writing"),

            _sub("code", "Программирование", "Dasturlash", "Programming"),

        ),

    ),

    ModuleDef(

        "vault", "🔐", "Личное хранилище", "Shaxsiy ombor", "Personal vault", 1, "AI",

        "Документы, паспорт, полисы, гарантии, чеки, важные заметки.",

        (

            _sub("documents", "Документы", "Hujjatlar", "Documents"),

            _sub("passport", "Паспортные данные", "Pasport ma'lumotlari", "Passport data"),

            _sub("policies", "Полисы", "Polislar", "Policies"),

            _sub("warranty", "Гарантийные талоны", "Kafolat talonlari", "Warranty cards"),

            _sub("receipts", "Чеки", "Cheklar", "Receipts"),

            _sub("notes", "Важные заметки", "Muhim qaydlar", "Important notes"),

        ),

    ),

    ModuleDef(

        "music", "🎵", "Музыка", "Musiqa", "Music", 1, "Развлечения",

        "Текст песен, разделение вокала и минуса, анализ трека, перевод, аккорды.",

        (

            _sub("lyrics", "Текст песни", "Qo'shiq matni", "Song lyrics"),

            _sub("separate", "Вокал и минус", "Vokal va minus", "Vocal separation"),

            _sub("analyze", "Анализ трека", "Trek tahlili", "Track analysis"),

            _sub("translate", "Перевод текста", "Matn tarjimasi", "Lyrics translation"),

            _sub("chords", "Аккорды", "Akkordlar", "Chords"),

            _sub("collection", "Моя коллекция", "Mening to'plamim", "My collection"),

        ),

    ),

)



MODULE_BY_ID: dict[str, ModuleDef] = {m.id: m for m in MODULES}



CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (

    ("Здоровье и питание", ("health", "nutrition", "fitness")),

    ("Деньги и бизнес", ("finance", "business")),

    ("Транспорт и путешествия", ("car", "travel")),

    ("Дом и покупки", ("home", "shopping")),

    ("Обучение", ("education",)),

    ("Право", ("legal",)),

    ("Планирование", ("organizer",)),

    ("AI и данные", ("ai_assistant", "vault")),

    ("Музыка", ("music",)),

)

