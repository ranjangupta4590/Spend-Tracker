from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, Header, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import ExpenseCreate, ExpenseListResponse
from app.services.expense_service import expense_service

router = APIRouter(prefix="/expenses", tags=["expenses"])


@router.post("", summary="Create an expense")
def create_expense(
    payload: ExpenseCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    idempotency_key: Optional[str] = Header(None, alias="Idempotency-Key"),
):
    result, status_code = expense_service.create_expense(
        db=db,
        user_id=current_user.id,
        expense_in=payload,
        idempotency_key=idempotency_key,
    )
    return JSONResponse(
        status_code=status_code,
        content=result.model_dump(mode="json"),
    )


@router.get("", response_model=ExpenseListResponse, summary="List expenses with filtering and pagination")
def list_expenses(
    category: Optional[str] = Query(None, description="Filter by category name"),
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return expense_service.list_expenses(
        db=db,
        user_id=current_user.id,
        category=category,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )
