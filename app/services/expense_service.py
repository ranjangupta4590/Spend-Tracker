import hashlib
import json
import math
from datetime import date
from typing import Optional, Tuple
from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Expense
from app.repositories.expense_repository import expense_repository
from app.schemas import ExpenseCreate, ExpenseResponse, ExpenseListResponse


class ExpenseService:
    @staticmethod
    def _compute_payload_hash(payload: ExpenseCreate) -> str:
        canonical_str = json.dumps(
            payload.model_dump(mode="json"),
            sort_keys=True,
            separators=(",", ":"),
        )
        return hashlib.sha256(canonical_str.encode("utf-8")).hexdigest()

    def create_expense(
        self,
        db: Session,
        user_id: int,
        expense_in: ExpenseCreate,
        idempotency_key: Optional[str] = None,
    ) -> Tuple[ExpenseResponse, int]:
        clean_key = idempotency_key.strip() if idempotency_key else None
        if clean_key and len(clean_key) > 128:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Idempotency-Key must not exceed 128 characters",
            )

        payload_hash = self._compute_payload_hash(expense_in)

        if clean_key:
            existing_record = expense_repository.get_idempotency_record(db, clean_key)
            if existing_record:
                if existing_record.request_hash == payload_hash:
                    cached_data = json.loads(existing_record.response_body)
                    return ExpenseResponse(**cached_data), existing_record.response_status
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="Idempotency key was previously used with a different request payload",
                )

        try:
            expense = expense_repository.create_expense(
                db=db,
                user_id=user_id,
                amount=expense_in.amount,
                category=expense_in.category,
                note=expense_in.note,
                expense_date=expense_in.date,
            )
            db.flush()

            response_obj = ExpenseResponse(
                id=expense.id,
                amount=float(expense.amount),
                category=expense.category,
                note=expense.note,
                date=expense.expense_date,
                created_at=expense.created_at,
                updated_at=expense.updated_at,
            )

            if clean_key:
                expense_repository.create_idempotency_record(
                    db=db,
                    key=clean_key,
                    request_hash=payload_hash,
                    status_code=status.HTTP_201_CREATED,
                    response_body=json.dumps(response_obj.model_dump(mode="json")),
                )

            db.commit()
            db.refresh(expense)
            return response_obj, status.HTTP_201_CREATED

        except IntegrityError:
            db.rollback()
            if clean_key:
                # Concurrent race condition check
                record = expense_repository.get_idempotency_record(db, clean_key)
                if record:
                    if record.request_hash == payload_hash:
                        cached_data = json.loads(record.response_body)
                        return ExpenseResponse(**cached_data), record.response_status
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Idempotency key conflict: simultaneous request with different payload",
                    )
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database integrity error while creating expense",
            )

    def list_expenses(
        self,
        db: Session,
        user_id: int,
        category: Optional[str] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> ExpenseListResponse:
        if page < 1:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page must be a positive integer greater than 0",
            )
        if page_size < 1 or page_size > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Page size must be between 1 and 100",
            )
        if start_date and end_date and start_date > end_date:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="start_date must be on or before end_date",
            )

        clean_category = category.strip() if category else None
        skip = (page - 1) * page_size

        total = expense_repository.count_expenses(
            db=db,
            user_id=user_id,
            category=clean_category,
            start_date=start_date,
            end_date=end_date,
        )
        expenses = expense_repository.list_expenses(
            db=db,
            user_id=user_id,
            category=clean_category,
            start_date=start_date,
            end_date=end_date,
            skip=skip,
            limit=page_size,
        )

        items = [
            ExpenseResponse(
                id=item.id,
                amount=float(item.amount),
                category=item.category,
                note=item.note,
                date=item.expense_date,
                created_at=item.created_at,
                updated_at=item.updated_at,
            )
            for item in expenses
        ]

        total_pages = max(1, math.ceil(total / page_size)) if total > 0 else 1

        return ExpenseListResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


expense_service = ExpenseService()
