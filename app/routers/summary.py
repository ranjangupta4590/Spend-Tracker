from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas import SummaryResponse
from app.services.summary_service import summary_service

router = APIRouter(prefix="/summary", tags=["summary"])


@router.get("", response_model=SummaryResponse, summary="Get monthly spending summary")
def get_summary(
    year: Optional[int] = Query(None, ge=2000, le=2100, description="Target year"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Target month (1-12)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return summary_service.get_summary(db=db, user_id=current_user.id, year=year, month=month)

