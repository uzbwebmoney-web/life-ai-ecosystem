from aiogram.fsm.state import State, StatesGroup


class RecordStates(StatesGroup):
    waiting_text = State()
    waiting_amount = State()


class ReminderStates(StatesGroup):
    waiting_title = State()
    waiting_datetime = State()


class MemoryStates(StatesGroup):
    waiting_save = State()
    waiting_search = State()


class AiChatStates(StatesGroup):
    waiting_question = State()


class FamilyStates(StatesGroup):
    waiting_name = State()
    waiting_relation = State()


class CreditStates(StatesGroup):
    waiting_title = State()
    waiting_total = State()
    waiting_monthly = State()
    waiting_day = State()
    waiting_payment_amount = State()


class HealthStates(StatesGroup):
    waiting_metric_value = State()
    waiting_metric_notes = State()
    waiting_med_name = State()
    waiting_med_dosage = State()
    waiting_med_times = State()
    waiting_med_edit_name = State()
    waiting_med_edit_dosage = State()
    waiting_med_edit_times = State()
    waiting_med_snooze_delay = State()
    waiting_visit_title = State()
    waiting_visit_datetime = State()
    waiting_doc_title = State()


class CarStates(StatesGroup):
    waiting_maint_date = State()
    waiting_maint_notes = State()
    waiting_compliance_date = State()
    waiting_expense_title = State()
    waiting_expense_amount = State()


class FinanceStates(StatesGroup):
    waiting_tx_title = State()
    waiting_tx_amount = State()
    waiting_goal_title = State()
    waiting_goal_target = State()
    waiting_goal_current = State()
    waiting_budget_limit = State()
    waiting_bill_title = State()
    waiting_bill_amount = State()
    waiting_bill_date = State()


class TravelStates(StatesGroup):
    waiting_fx_amount = State()
    waiting_fx_from = State()
    waiting_fx_to = State()


class HomeStates(StatesGroup):
    waiting_utility_title = State()
    waiting_utility_amount = State()
    waiting_utility_date = State()
    waiting_expense_title = State()
    waiting_expense_amount = State()
    waiting_repair_title = State()
    waiting_repair_notes = State()
    waiting_shopping_title = State()
    waiting_inventory_title = State()
    waiting_inventory_location = State()
    waiting_inventory_qty = State()


class NutritionStates(StatesGroup):
    waiting_grocery_title = State()
    waiting_water_ml = State()
    waiting_cal_weight = State()
    waiting_cal_height = State()
    waiting_cal_age = State()


class VaultStates(StatesGroup):
    waiting_title = State()
    waiting_body = State()
    waiting_expiry = State()
    waiting_amount = State()
    waiting_attachment = State()


class VaultLockStates(StatesGroup):
    waiting_unlock = State()
    waiting_set_password = State()
    waiting_confirm_password = State()
    waiting_remove_password = State()
    waiting_change_old = State()


class OrganizerStates(StatesGroup):
    waiting_task_title = State()
    waiting_task_due = State()
    waiting_note_title = State()
    waiting_note_body = State()
    waiting_event_title = State()
    waiting_event_datetime = State()
    waiting_remind_title = State()
    waiting_remind_datetime = State()


class NotificationsStates(StatesGroup):
    waiting_title = State()
    waiting_due = State()
    waiting_notes = State()
    waiting_amount = State()


class ScanStates(StatesGroup):
    waiting_photo = State()


class PaymentStates(StatesGroup):
    waiting_receipt = State()


class AdminStates(StatesGroup):
    waiting_user_search = State()
    waiting_bonus_amount = State()
    waiting_credits_adjust = State()
    waiting_support_reply = State()


class SupportStates(StatesGroup):
    chat_active = State()


class OnboardingStates(StatesGroup):
    waiting_confirm = State()


class HouseholdStates(StatesGroup):
    waiting_join_code = State()


class MusicStates(StatesGroup):
    waiting_audio = State()
    waiting_lyrics_text = State()


class EducationStates(StatesGroup):
    waiting_study_spec = State()
