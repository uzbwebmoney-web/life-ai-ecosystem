from __future__ import annotations

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.core.i18n import t
from app.core.modules.catalog import MODULE_BY_ID
from app.models.entities import HomeInventoryItem, HomeRepairTask, HomeShoppingItem, HomeUtilityBill


def home_module_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    mod = MODULE_BY_ID["home"]
    rows = [
        [InlineKeyboardButton(text=sub.title(lang), callback_data=f"sub:home:{sub.id}")]
        for sub in mod.submodules
    ]
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_menu"), callback_data="hub:menu")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_utilities_kb(bills: list[HomeUtilityBill], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "home_utility_add"), callback_data="home:util:add")],
    ]
    for bill in bills[:8]:
        rows.append([InlineKeyboardButton(text=f"💡 {bill.title[:26]}", callback_data=f"home:util:open:{bill.id}")])
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_utility_item_kb(bill_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "home_delete"), callback_data=f"home:util:del:{bill_id}")],
            [InlineKeyboardButton(text=t(lang, "home_back_utilities"), callback_data="home:util:list")],
        ]
    )


def home_expenses_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "home_expense_add"), callback_data="home:exp:add")],
            [InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:home")],
        ]
    )


def home_repair_kb(tasks: list[HomeRepairTask], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "home_repair_add"), callback_data="home:repair:add")],
        [InlineKeyboardButton(text=t(lang, "btn_ask_ai"), callback_data="ai:home:repair")],
    ]
    for task in tasks[:10]:
        icon = {"planned": "📋", "in_progress": "🔨", "done": "✅"}.get(task.status, "📋")
        rows.append(
            [InlineKeyboardButton(text=f"{icon} {task.title[:28]}", callback_data=f"home:repair:open:{task.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_repair_item_kb(task_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "home_repair_cycle"), callback_data=f"home:repair:status:{task_id}")],
            [InlineKeyboardButton(text=t(lang, "home_delete"), callback_data=f"home:repair:del:{task_id}")],
            [InlineKeyboardButton(text=t(lang, "home_back_repair"), callback_data="home:repair:list")],
        ]
    )


def home_shopping_kb(items: list[HomeShoppingItem], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "home_shopping_add"), callback_data="home:shop:add")],
    ]
    for item in items[:12]:
        mark = "✅" if item.done else "⬜"
        rows.append(
            [InlineKeyboardButton(text=f"{mark} {item.title[:30]}", callback_data=f"home:shop:toggle:{item.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_inventory_kb(items: list[HomeInventoryItem], lang: str = "ru") -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=t(lang, "home_inventory_add"), callback_data="home:inv:add")],
    ]
    for item in items[:10]:
        rows.append(
            [InlineKeyboardButton(text=f"📦 {item.title[:28]}", callback_data=f"home:inv:open:{item.id}")]
        )
    rows.append([InlineKeyboardButton(text=t(lang, "btn_back_module"), callback_data="mod:home")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def home_inventory_item_kb(item_id: int, lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t(lang, "home_delete"), callback_data=f"home:inv:del:{item_id}")],
            [InlineKeyboardButton(text=t(lang, "home_back_inventory"), callback_data="home:inv:list")],
        ]
    )


def home_cancel_kb(lang: str = "ru") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=t(lang, "btn_cancel"), callback_data="home:cancel")]]
    )
