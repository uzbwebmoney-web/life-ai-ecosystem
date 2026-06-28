from datetime import datetime

from app.models.entities import CreditLoan
from app.services.credit_loans import apply_credit_payment, loan_remaining, payment_day_matches_today


def test_payment_day_matches_exact():
    assert payment_day_matches_today(15, datetime(2026, 6, 15, 10, 0))


def test_payment_day_no_match():
    assert not payment_day_matches_today(15, datetime(2026, 6, 14, 10, 0))


def test_payment_day_31_in_february():
    assert payment_day_matches_today(31, datetime(2026, 2, 28, 9, 0))
    assert not payment_day_matches_today(31, datetime(2026, 2, 27, 9, 0))


def test_loan_remaining_defaults_to_total():
    loan = CreditLoan(
        id=1,
        user_id=1,
        title="Test",
        total_amount=1_000_000,
        remaining_amount=None,
        monthly_payment=100_000,
        payment_day=15,
    )
    assert loan_remaining(loan) == 1_000_000


def test_loan_remaining_uses_stored_value():
    loan = CreditLoan(
        id=1,
        user_id=1,
        title="Test",
        total_amount=1_000_000,
        remaining_amount=500_000,
        monthly_payment=100_000,
        payment_day=15,
    )
    assert loan_remaining(loan) == 500_000
