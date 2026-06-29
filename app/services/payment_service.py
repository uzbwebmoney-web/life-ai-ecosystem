from __future__ import annotations

from datetime import datetime, timedelta

from aiogram import Bot
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.i18n import t
from app.core.plans import ADDON_PACKAGES, PLANS, format_stars, format_uzs, usd_to_stars, usd_to_uzs
from app.models.entities import PaymentOrder, ProcessedStarsPayment, User


def _utcnow() -> datetime:
    return datetime.utcnow()


def product_label(product_type: str, product_id: str, *, lang: str) -> str:
    if product_type == "plan" and product_id in PLANS:
        plan = PLANS[product_id]  # type: ignore[index]
        return f"{plan.emoji} {t(lang, plan.name_key)}"
    pkg = next((p for p in ADDON_PACKAGES if p.id == product_id), None)
    if pkg:
        return t(lang, pkg.name_key)
    return product_id


def _resolve_product_raw(product_id: str) -> tuple[str, str, float]:
    if product_id in PLANS:
        plan = PLANS[product_id]  # type: ignore[index]
        if not plan.usd_monthly:
            raise ValueError("free plan")
        return "plan", product_id, plan.usd_monthly
    pkg = next((p for p in ADDON_PACKAGES if p.id == product_id), None)
    if pkg:
        return "package", product_id, pkg.usd_price
    raise ValueError(f"unknown product {product_id}")


def resolve_product(product_id: str) -> tuple[str, str, int]:
    product_type, pid, usd = _resolve_product_raw(product_id)
    return product_type, pid, usd_to_uzs(usd)


def resolve_product_stars(product_id: str) -> tuple[str, str, int]:
    product_type, pid, usd = _resolve_product_raw(product_id)
    return product_type, pid, usd_to_stars(usd)


def build_stars_payload(product_type: str, product_id: str) -> str:
    kind = "plan" if product_type == "plan" else "pkg"
    return f"st:{kind}:{product_id}"


def parse_stars_payload(payload: str) -> tuple[str, str] | None:
    parts = (payload or "").split(":")
    if len(parts) != 3 or parts[0] != "st":
        return None
    product_type = "plan" if parts[1] == "plan" else "package" if parts[1] == "pkg" else None
    if not product_type:
        return None
    product_id = parts[2]
    try:
        _resolve_product_raw(product_id)
    except ValueError:
        return None
    return product_type, product_id


async def activate_product_purchase(
    session: AsyncSession,
    user: User,
    product_type: str,
    product_id: str,
) -> User:
    if product_type == "plan":
        user.plan_id = product_id
        user.plan_expires_at = _utcnow() + timedelta(days=30)
    elif product_type == "package":
        pkg = next((p for p in ADDON_PACKAGES if p.id == product_id), None)
        if pkg:
            if pkg.kind == "ai_credits":
                user.ai_bonus_balance = (user.ai_bonus_balance or 0) + pkg.amount
            elif pkg.kind == "photo_analysis":
                user.bonus_photo_analysis = (user.bonus_photo_analysis or 0) + pkg.amount
            elif pkg.kind == "image_gen":
                user.bonus_image_gen = (user.bonus_image_gen or 0) + pkg.amount
            elif pkg.kind == "memory_facts":
                user.bonus_memory_facts = (user.bonus_memory_facts or 0) + pkg.amount
            elif pkg.kind == "storage_mb":
                user.bonus_storage_mb = (user.bonus_storage_mb or 0) + pkg.amount
    await session.commit()
    await session.refresh(user)
    return user


async def register_stars_payment(
    session: AsyncSession,
    *,
    charge_id: str,
    user_id: int,
    product_type: str,
    product_id: str,
) -> bool:
    """Return True if payment is new and should be fulfilled."""
    existing = (
        await session.execute(select(ProcessedStarsPayment).where(ProcessedStarsPayment.charge_id == charge_id))
    ).scalar_one_or_none()
    if existing:
        return False
    session.add(
        ProcessedStarsPayment(
            charge_id=charge_id,
            user_id=user_id,
            product_type=product_type,
            product_id=product_id,
        )
    )
    await session.flush()
    return True


async def get_open_order(session: AsyncSession, user_id: int) -> PaymentOrder | None:
    return (
        await session.execute(
            select(PaymentOrder)
            .where(
                PaymentOrder.user_id == user_id,
                PaymentOrder.status.in_(("awaiting_receipt", "pending")),
            )
            .order_by(PaymentOrder.created_at.desc())
            .limit(1)
        )
    ).scalar_one_or_none()


async def create_payment_order(
    session: AsyncSession,
    user: User,
    product_type: str,
    product_id: str,
    amount_uzs: int,
) -> PaymentOrder:
    existing = await get_open_order(session, user.id)
    if existing:
        existing.status = "cancelled"
    order = PaymentOrder(
        user_id=user.id,
        product_type=product_type,
        product_id=product_id,
        amount_uzs=amount_uzs,
        status="awaiting_receipt",
    )
    session.add(order)
    await session.commit()
    await session.refresh(order)
    return order


async def get_payment_order(
    session: AsyncSession,
    order_id: int,
    *,
    user_id: int | None = None,
) -> PaymentOrder | None:
    q = select(PaymentOrder).where(PaymentOrder.id == order_id)
    if user_id is not None:
        q = q.where(PaymentOrder.user_id == user_id)
    return (await session.execute(q)).scalar_one_or_none()


async def submit_receipt(
    session: AsyncSession,
    order_id: int,
    user_id: int,
    file_id: str,
) -> PaymentOrder | None:
    order = await get_payment_order(session, order_id, user_id=user_id)
    if not order or order.status not in ("awaiting_receipt", "pending"):
        return None
    order.receipt_file_id = file_id
    order.receipt_submitted_at = _utcnow()
    order.status = "pending"
    await session.commit()
    await session.refresh(order)
    return order


async def list_pending_orders(session: AsyncSession, *, limit: int = 20) -> list[PaymentOrder]:
    rows = (
        await session.execute(
            select(PaymentOrder)
            .where(PaymentOrder.status == "pending")
            .order_by(PaymentOrder.receipt_submitted_at.desc())
            .limit(limit)
        )
    ).scalars().all()
    return list(rows)


async def count_pending_orders(session: AsyncSession) -> int:
    return (
        await session.execute(
            select(func.count(PaymentOrder.id)).where(PaymentOrder.status == "pending")
        )
    ).scalar_one() or 0


async def approve_payment_order(
    session: AsyncSession,
    order_id: int,
    admin_user: User,
) -> tuple[PaymentOrder | None, User | None]:
    order = await get_payment_order(session, order_id)
    if not order or order.status != "pending":
        return None, None
    buyer = (
        await session.execute(select(User).where(User.id == order.user_id))
    ).scalar_one_or_none()
    if not buyer:
        return None, None

    await activate_product_purchase(session, buyer, order.product_type, order.product_id)

    order.status = "approved"
    order.reviewed_at = _utcnow()
    order.admin_user_id = admin_user.id
    await session.commit()
    await session.refresh(order)
    await session.refresh(buyer)
    return order, buyer


async def reject_payment_order(
    session: AsyncSession,
    order_id: int,
    admin_user: User,
) -> PaymentOrder | None:
    order = await get_payment_order(session, order_id)
    if not order or order.status != "pending":
        return None
    order.status = "rejected"
    order.reviewed_at = _utcnow()
    order.admin_user_id = admin_user.id
    await session.commit()
    await session.refresh(order)
    return order


def format_payment_instructions(
    order: PaymentOrder,
    *,
    lang: str,
    card_number: str,
    card_holder: str,
) -> str:
    product = product_label(order.product_type, order.product_id, lang=lang)
    holder_line = f"\n{t(lang, 'pay_card_holder', holder=card_holder)}" if card_holder else ""
    return t(
        lang,
        "pay_instructions",
        order_id=order.id,
        product=product,
        amount=format_uzs(order.amount_uzs),
        card=card_number or t(lang, "pay_card_not_set"),
        holder_line=holder_line,
    )


def format_order_admin_card(order: PaymentOrder, buyer: User, *, lang: str) -> str:
    username = f"@{buyer.username}" if buyer.username else f"id{buyer.telegram_id}"
    product = product_label(order.product_type, order.product_id, lang=lang)
    submitted = (
        order.receipt_submitted_at.strftime("%d.%m.%Y %H:%M")
        if order.receipt_submitted_at
        else "—"
    )
    return t(
        lang,
        "pay_admin_order",
        order_id=order.id,
        user=username,
        telegram_id=buyer.telegram_id,
        product=product,
        amount=format_uzs(order.amount_uzs),
        submitted=submitted,
        status=order.status,
    )


async def notify_admins_payment_pending(
    bot: Bot,
    order: PaymentOrder,
    buyer: User,
    *,
    lang: str = "ru",
) -> None:
    from app.bot.keyboards_payment import admin_order_kb
    from app.core.config import settings

    text = t(lang, "pay_admin_notify", order_id=order.id) + "\n\n" + format_order_admin_card(
        order, buyer, lang=lang
    )
    for admin_tid in settings.admin_telegram_id_list:
        try:
            if order.receipt_file_id:
                await bot.send_photo(
                    admin_tid,
                    order.receipt_file_id,
                    caption=text,
                    reply_markup=admin_order_kb(order.id, lang),
                )
            else:
                await bot.send_message(
                    admin_tid,
                    text,
                    reply_markup=admin_order_kb(order.id, lang),
                )
        except Exception:
            continue


async def notify_admins_stars_purchase(
    bot: Bot,
    buyer: User,
    product_type: str,
    product_id: str,
    stars: int,
    *,
    lang: str = "ru",
) -> None:
    from app.core.config import settings

    product = product_label(product_type, product_id, lang=lang)
    username = f"@{buyer.username}" if buyer.username else f"id{buyer.telegram_id}"
    text = t(
        lang,
        "pay_admin_stars_notify",
        user=username,
        telegram_id=buyer.telegram_id,
        product=product,
        stars=format_stars(stars),
    )
    for admin_tid in settings.admin_telegram_id_list:
        try:
            await bot.send_message(admin_tid, text)
        except Exception:
            continue


def format_buyer_approved_message(order: PaymentOrder, *, lang: str) -> str:
    product = product_label(order.product_type, order.product_id, lang=lang)
    return t(lang, "pay_approved", product=product)


def format_buyer_rejected_message(*, lang: str) -> str:
    return t(lang, "pay_rejected")


def format_orders_list(orders: list[PaymentOrder], users: dict[int, User], *, lang: str) -> str:
    if not orders:
        return t(lang, "pay_admin_empty")
    lines = [t(lang, "pay_admin_list_title"), ""]
    for order in orders:
        buyer = users.get(order.user_id)
        name = f"@{buyer.username}" if buyer and buyer.username else f"#{order.user_id}"
        product = product_label(order.product_type, order.product_id, lang=lang)
        lines.append(f"• <b>#{order.id}</b> {name} — {product} — {format_uzs(order.amount_uzs)}")
    return "\n".join(lines)
