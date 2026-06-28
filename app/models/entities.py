from datetime import datetime

from sqlalchemy import BigInteger, Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    language: Mapped[str] = mapped_column(String(8), default="ru")
    memory_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    voice_mode: Mapped[bool] = mapped_column(Boolean, default=False)
    utc_offset_minutes: Mapped[int] = mapped_column(Integer, default=300)
    active_profile_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("family_profiles.id"), nullable=True)
    active_module_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    active_submodule_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    onboarding_done: Mapped[bool] = mapped_column(Boolean, default=False)
    welcome_pending: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FamilyProfile(Base):
    __tablename__ = "family_profiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    name: Mapped[str] = mapped_column(String(128))
    relation: Mapped[str] = mapped_column(String(64), default="self")
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class LifeRecord(Base):
    __tablename__ = "life_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    module_id: Mapped[str] = mapped_column(String(32), index=True)
    submodule_id: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, default="")
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    meta_json: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    starts_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    event_type: Mapped[str] = mapped_column(String(32), default="meeting")
    notes: Mapped[str] = mapped_column(Text, default="")
    recurrence: Mapped[str] = mapped_column(String(16), default="")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AlertItem(Base):
    __tablename__ = "alert_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    alert_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    due_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    amount: Mapped[float | None] = mapped_column(Float, nullable=True)
    currency: Mapped[str | None] = mapped_column(String(8), nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class Reminder(Base):
    __tablename__ = "reminders"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    module_id: Mapped[str] = mapped_column(String(32), default="notifications")
    title: Mapped[str] = mapped_column(String(255))
    due_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    sent: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class MemoryEntry(Base):
    __tablename__ = "memory_entries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    module_id: Mapped[str | None] = mapped_column(String(32), nullable=True)
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)


class CreditLoan(Base):
    __tablename__ = "credit_loans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    total_amount: Mapped[float] = mapped_column(Float)
    monthly_payment: Mapped[float] = mapped_column(Float)
    payment_day: Mapped[int] = mapped_column(Integer)
    currency: Mapped[str] = mapped_column(String(8), default="UZS")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_month: Mapped[str | None] = mapped_column(String(7), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HealthMetric(Base):
    __tablename__ = "health_metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    metric_type: Mapped[str] = mapped_column(String(32), index=True)
    value_primary: Mapped[float] = mapped_column(Float)
    value_secondary: Mapped[float | None] = mapped_column(Float, nullable=True)
    unit: Mapped[str] = mapped_column(String(16), default="")
    notes: Mapped[str] = mapped_column(Text, default="")
    recorded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HealthMedication(Base):
    __tablename__ = "health_medications"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    name: Mapped[str] = mapped_column(String(255))
    dosage: Mapped[str] = mapped_column(String(128), default="")
    reminder_times: Mapped[str] = mapped_column(String(128))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_key: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CarMaintenanceItem(Base):
    __tablename__ = "car_maintenance_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    item_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    due_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CarCompliance(Base):
    __tablename__ = "car_compliance"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    compliance_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    expires_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_key: Mapped[str | None] = mapped_column(String(32), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FinanceGoal(Base):
    __tablename__ = "finance_goals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    target_amount: Mapped[float] = mapped_column(Float)
    current_amount: Mapped[float] = mapped_column(Float, default=0.0)
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FinanceBudget(Base):
    __tablename__ = "finance_budgets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    category: Mapped[str] = mapped_column(String(32), index=True)
    limit_amount: Mapped[float] = mapped_column(Float)
    month_key: Mapped[str] = mapped_column(String(7), index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class FinanceBill(Base):
    __tablename__ = "finance_bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    due_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    category: Mapped[str] = mapped_column(String(32), default="bills")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HomeUtilityBill(Base):
    __tablename__ = "home_utility_bills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    amount: Mapped[float] = mapped_column(Float)
    due_at: Mapped[datetime] = mapped_column(DateTime, index=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    last_notified_date: Mapped[str | None] = mapped_column(String(10), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HomeRepairTask(Base):
    __tablename__ = "home_repair_tasks"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    notes: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(16), default="planned")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HomeShoppingItem(Base):
    __tablename__ = "home_shopping_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class HomeInventoryItem(Base):
    __tablename__ = "home_inventory_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    location: Mapped[str] = mapped_column(String(128), default="")
    quantity: Mapped[str] = mapped_column(String(32), default="1")
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NutritionGroceryItem(Base):
    __tablename__ = "nutrition_grocery_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    title: Mapped[str] = mapped_column(String(255))
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class NutritionWaterDaily(Base):
    __tablename__ = "nutrition_water_daily"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    day_key: Mapped[str] = mapped_column(String(10), index=True)
    total_ml: Mapped[int] = mapped_column(Integer, default=0)
    goal_ml: Mapped[int] = mapped_column(Integer, default=2000)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class OrganizerItem(Base):
    __tablename__ = "organizer_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    profile_id: Mapped[int | None] = mapped_column(ForeignKey("family_profiles.id"), nullable=True)
    item_type: Mapped[str] = mapped_column(String(16), index=True)
    title: Mapped[str] = mapped_column(String(255))
    body: Mapped[str] = mapped_column(Text, default="")
    due_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    done: Mapped[bool] = mapped_column(Boolean, default=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
