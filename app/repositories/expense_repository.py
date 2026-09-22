from datetime import date
from decimal import Decimal
from typing import Optional, List, Tuple
from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import Expense, IdempotencyRecord


class ExpenseRepository:
    def create_expense(
        self,
        db: Session,
        user_id: int,
        amount: Decimal,
        category: str,
        note: Optional[str],
        expense_date: date,
    ) -> Expense:
        expense = Expense(
            user_id=user_id,
            amount=amount,
            category=category,
            note=note,
            expense_date=expense_date,
        )
        db.add(expense)
        return expense

    def get_idempotency_record(self, db: Session, key: str) -> Optional[IdempotencyRecord]:
        stmt = select(IdempotencyRecord).where(IdempotencyRecord.key == key)
        return db.execute(stmt).scalar_one_or_none()

    def create_idempotency_record(
        self,
        db: Session,
        key: str,
        request_hash: str,
        status_code: int,
        response_body: str,
    ) -> IdempotencyRecord:
        record = IdempotencyRecord(
            key=key,
            request_hash=request_hash,
            response_status=status_code,
            response_body=response_body,
        )
        db.add(record)
        return record

    def list_expenses(
        self,
        db: Session,
        user_id: int,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        skip: int = 0,
        limit: int = 20,
    ) -> List[Expense]:
        stmt = select(Expense).where(Expense.user_id == user_id)
        if category:
            stmt = stmt.where(Expense.category == category)
        if start_date:
            stmt = stmt.where(Expense.expense_date >= start_date)
        if end_date:
            stmt = stmt.where(Expense.expense_date <= end_date)

        stmt = stmt.order_by(Expense.expense_date.desc(), Expense.id.desc()).offset(skip).limit(limit)
        return list(db.execute(stmt).scalars().all())

    def count_expenses(
        self,
        db: Session,
        user_id: int,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> int:
        stmt = select(func.count(Expense.id)).where(Expense.user_id == user_id)
        if category:
            stmt = stmt.where(Expense.category == category)
        if start_date:
            stmt = stmt.where(Expense.expense_date >= start_date)
        if end_date:
            stmt = stmt.where(Expense.expense_date <= end_date)

        return db.execute(stmt).scalar_one() or 0

    def get_period_category_totals(
        self,
        db: Session,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> List[Tuple[str, Decimal]]:
        stmt = (
            select(Expense.category, func.coalesce(func.sum(Expense.amount), 0))
            .where(
                Expense.user_id == user_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
            )
            .group_by(Expense.category)
            .order_by(func.sum(Expense.amount).desc())
        )
        results = db.execute(stmt).all()
        return [(row[0], Decimal(str(row[1]))) for row in results]

    def get_period_total_and_count(
        self,
        db: Session,
        user_id: int,
        start_date: date,
        end_date: date,
    ) -> Tuple[Decimal, int]:
        stmt = (
            select(
                func.coalesce(func.sum(Expense.amount), 0),
                func.count(Expense.id),
            )
            .where(
                Expense.user_id == user_id,
                Expense.expense_date >= start_date,
                Expense.expense_date <= end_date,
            )
        )
        result = db.execute(stmt).one()
        return Decimal(str(result[0])), int(result[1])


expense_repository = ExpenseRepository()
