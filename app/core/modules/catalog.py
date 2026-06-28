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
        "health", "🩺", "Здоровье", "Salomatlik", "Health", 1, "Здоровье и семья",
        "Симптомы, анализы, обследования, лекарства, дневник показателей, визиты к врачу, мед. документы.",
        (
            _sub("consultant", "AI-консультант", "AI maslahatchi", "AI consultant"),
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
        "car", "🚗", "Автомобиль", "Avtomobil", "Car", 2, "Транспорт",
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
        "Доходы, расходы, цели, бюджет, счета, анализ по категориям, кредиты.",
        (
            _sub("income", "Доходы", "Daromadlar", "Income"),
            _sub("expense", "Расходы", "Xarajatlar", "Expenses"),
            _sub("goals", "Финансовые цели", "Moliyaviy maqsadlar", "Financial goals"),
            _sub("budget", "Бюджет", "Byudjet", "Budget"),
            _sub("bills", "Оплата счетов", "Hisob to'lovi", "Bill payments"),
            _sub("analysis", "Анализ расходов", "Xarajat tahlili", "Expense analysis"),
            _sub("loans", "Кредиты", "Kreditlar", "Loans"),
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
        "business", "💼", "Бизнес", "Biznes", "Business", 2, "Деньги",
        "Бизнес-планы, реклама, конкуренты, договоры, клиенты, продажи.",
        (
            _sub("consultant", "AI-консультант", "AI maslahatchi", "AI consultant"),
            _sub("plans", "Бизнес-планы", "Biznes-rejalar", "Business plans"),
            _sub("ads", "Генерация рекламы", "Reklama yaratish", "Ad generation"),
            _sub("competitors", "Анализ конкурентов", "Raqobatchilar tahlili", "Competitor analysis"),
            _sub("contracts", "Генерация договоров", "Shartnomalar", "Contract generation"),
            _sub("client_responses", "Ответы клиентам", "Mijozlarga javoblar", "Client responses"),
            _sub("sales_analysis", "Анализ продаж", "Savdo tahlili", "Sales analysis"),
        ),
    ),
    ModuleDef(
        "work", "👔", "Работа", "Ish", "Work", 2, "Карьера",
        "Резюме, вакансии, собеседования, карьерный AI, зарплата.",
        (
            _sub("resume", "Резюме"),
            _sub("jobs", "Поиск вакансий"),
            _sub("interview", "Подготовка к собеседованию"),
            _sub("career_ai", "Карьерный AI"),
            _sub("salary", "Зарплата"),
        ),
    ),
    ModuleDef(
        "education", "📚", "Образование", "Ta'lim", "Education", 2, "Обучение",
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
        "nutrition", "🥗", "Питание", "Ovqatlanish", "Nutrition", 2, "Здоровье и семья",
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
        "sport", "🏃", "Спорт", "Sport", "Sport", 2, "Активность",
        "Тренировки, бег, велосипед, футбол, прогресс.",
        (
            _sub("workouts", "Тренировки"),
            _sub("running", "Бег"),
            _sub("cycling", "Велосипед"),
            _sub("football", "Футбол"),
            _sub("progress", "Прогресс"),
        ),
    ),
    ModuleDef(
        "beauty", "💄", "Красота", "Go'zallik", "Beauty", 3, "Быт",
        "Уход за кожей, волосы, косметика, напоминания.",
        (
            _sub("skin", "Уход за кожей"),
            _sub("hair", "Волосы"),
            _sub("cosmetics", "Косметика"),
            _sub("reminders", "Напоминания"),
        ),
    ),
    ModuleDef(
        "family", "👨‍👩‍👧", "Семья", "Oila", "Family", 1, "Здоровье и семья",
        "Семейный календарь, беременность, дети, школа, родители.",
        (
            _sub("calendar", "Семейный календарь"),
            _sub("pregnancy", "Беременность"),
            _sub("kids", "Дети"),
            _sub("school", "Школа"),
            _sub("parents", "Родители"),
        ),
    ),
    ModuleDef(
        "psychology", "🧘", "Психология", "Psixologiya", "Psychology", 2, "Здоровье и семья",
        "Дневник настроения, антистресс, медитация, сон.",
        (
            _sub("mood", "Дневник настроения"),
            _sub("antistress", "Антистресс"),
            _sub("meditation", "Медитация"),
            _sub("sleep", "Сон"),
        ),
    ),
    ModuleDef(
        "ai_assistant", "🤖", "AI-ассистент", "AI yordamchi", "AI assistant", 1, "AI",
        "Вопросы, переводы, документы, фото, тексты, картинки, код.",
        (
            _sub("questions", "Любые вопросы", "Har qanday savollar", "Any questions"),
            _sub("translate", "Переводы", "Tarjimalar", "Translations"),
            _sub("documents", "PDF и документы", "PDF va hujjatlar", "PDF & documents"),
            _sub("photo", "Анализ фото", "Foto tahlil", "Photo analysis"),
            _sub("writing", "Создание текстов", "Matn yaratish", "Text writing"),
            _sub("images", "Создание картинок", "Rasm yaratish", "Image creation"),
            _sub("code", "Программирование", "Dasturlash", "Programming"),
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
        "notifications", "🔔", "Уведомления", "Bildirishnomalar", "Alerts", 1, "Планирование",
        "Лекарства, ТО, коммуналка, подписки, кредиты, визы.",
        (
            _sub("medicine", "Лекарства"),
            _sub("car_service", "ТО"),
            _sub("utilities", "Коммуналка"),
            _sub("subscriptions", "Подписки"),
            _sub("loans", "Кредиты"),
            _sub("visas", "Визы"),
        ),
    ),
    ModuleDef(
        "gov", "🏛", "Госуслуги", "Davlat xizmatlari", "Government", 2, "Право",
        "Документы, налоги, штрафы, очереди, госпошлины.",
        (
            _sub("docs", "Документы"),
            _sub("taxes", "Налоги"),
            _sub("fines", "Штрафы"),
            _sub("queues", "Очереди"),
            _sub("fees", "Госпошлины"),
        ),
    ),
    ModuleDef(
        "security", "🛡", "Безопасность", "Xavfsizlik", "Security", 2, "Право",
        "Проверка ссылок, мошенников, сайтов, файлов, кибербезопасность.",
        (
            _sub("links", "Проверка ссылок"),
            _sub("scammers", "Проверка мошенников"),
            _sub("sites", "Проверка сайтов"),
            _sub("files", "Проверка файлов"),
            _sub("tips", "Кибербезопасность"),
        ),
    ),
    ModuleDef(
        "emergency", "🆘", "Экстренная помощь", "Favqulodda yordam", "Emergency", 1, "Право",
        "ДТП, первая помощь, потеря документов, экстренные телефоны.",
        (
            _sub("accident", "Что делать при ДТП"),
            _sub("first_aid", "Первая помощь"),
            _sub("lost_docs", "Потеря документов"),
            _sub("phones", "Экстренные телефоны"),
        ),
    ),
    ModuleDef(
        "smart_home", "🏡", "Умный дом", "Aqlli uy", "Smart home", 3, "Технологии",
        "Устройства, напоминания, автоматизация.",
        (
            _sub("devices", "Управление устройствами"),
            _sub("reminders", "Напоминания"),
            _sub("automation", "Автоматизация"),
        ),
    ),
    ModuleDef(
        "entertainment", "🎬", "Развлечения", "Ko'ngilochar", "Entertainment", 3, "Медиа",
        "Фильмы, книги, игры, музыка, афиша.",
        (
            _sub("movies", "Фильмы"),
            _sub("books", "Книги"),
            _sub("games", "Игры"),
            _sub("music", "Музыка"),
            _sub("events", "Афиша"),
        ),
    ),
    ModuleDef(
        "news", "📰", "Новости", "Yangiliklar", "News", 3, "Медиа",
        "Персональная лента, спорт, финансы, технологии.",
        (
            _sub("feed", "Персональная лента"),
            _sub("sport", "Спорт"),
            _sub("finance", "Финансы"),
            _sub("tech", "Технологии"),
        ),
    ),
    ModuleDef(
        "ecology", "🌿", "Экология", "Ekologiya", "Ecology", 3, "Медиа",
        "Погода, качество воздуха, UV, пыльца.",
        (
            _sub("weather", "Погода"),
            _sub("air", "Качество воздуха"),
            _sub("uv", "УФ-индекс"),
            _sub("pollen", "Пыльца"),
        ),
    ),
    ModuleDef(
        "social", "🎉", "Социальная жизнь", "Ijtimoiy hayot", "Social", 3, "Быт",
        "Контакты, праздники, поздравления, встречи.",
        (
            _sub("contacts", "Контакты"),
            _sub("holidays", "Праздники"),
            _sub("greetings", "Поздравления"),
            _sub("meetups", "Организация встреч"),
        ),
    ),
    ModuleDef(
        "pets", "🐾", "Животные", "Hayvonlar", "Pets", 2, "Быт",
        "Уход, вакцинация, напоминания, питание.",
        (
            _sub("care", "Уход"),
            _sub("vaccines", "Вакцинация"),
            _sub("reminders", "Напоминания"),
            _sub("food", "Питание"),
        ),
    ),
    ModuleDef(
        "realestate", "🏢", "Недвижимость", "Ko'chmas mulk", "Real estate", 2, "Деньги",
        "Покупка, аренда, ипотека, ремонт, оценка.",
        (
            _sub("buy", "Покупка"),
            _sub("rent", "Аренда"),
            _sub("mortgage", "Ипотека"),
            _sub("repair", "Ремонт"),
            _sub("valuation", "Оценка стоимости"),
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
)

MODULE_BY_ID: dict[str, ModuleDef] = {m.id: m for m in MODULES}

CATEGORIES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("Здоровье и семья", ("health", "nutrition", "family", "psychology", "pets")),
    ("Деньги и карьера", ("finance", "business", "work", "realestate")),
    ("Транспорт и путешествия", ("car", "travel")),
    ("Дом и быт", ("home", "shopping", "beauty", "social")),
    ("Обучение и спорт", ("education", "sport")),
    ("Право и безопасность", ("legal", "gov", "security", "emergency")),
    ("AI и данные", ("ai_assistant", "vault")),
    ("Планирование", ("organizer", "notifications")),
    ("Медиа и технологии", ("entertainment", "news", "ecology", "smart_home")),
)
