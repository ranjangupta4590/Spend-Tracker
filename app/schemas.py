import re
from datetime import date, datetime
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, List, Dict, Union
from pydantic import BaseModel, Field, EmailStr, field_validator, model_validator, ConfigDict


class UserSignupRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    confirm_password: str = Field(..., min_length=8, max_length=128)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v

    @field_validator("password", mode="after")
    @classmethod
    def validate_password_complexity(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[a-zA-Z]", v):
            raise ValueError("Password must contain at least one letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one number")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>_\-+=\[\]\\/;'`~]", v):
            raise ValueError("Password must contain at least one special character")
        return v

    @model_validator(mode="after")
    def check_passwords_match(self) -> "UserSignupRequest":
        if self.password != self.confirm_password:
            raise ValueError("Passwords do not match")
        return self


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip().lower()
        return v


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    is_verified: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponse(BaseModel):
    message: str



class ExpenseBase(BaseModel):
    amount: Decimal = Field(..., gt=0, le=Decimal("1000000000.00"))
    category: str = Field(..., min_length=1, max_length=50)
    note: Optional[str] = Field(None, max_length=255)
    date: date

    @field_validator("category", mode="before")
    @classmethod
    def validate_category(cls, v: str) -> str:
        if not isinstance(v, str) or not v.strip():
            raise ValueError("Category cannot be empty or whitespace only")
        return v.strip()

    @field_validator("note", mode="before")
    @classmethod
    def validate_note(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and isinstance(v, str):
            v_stripped = v.strip()
            return v_stripped if v_stripped else None
        return v

    @field_validator("amount", mode="after")
    @classmethod
    def validate_amount(cls, v: Decimal) -> Decimal:
        # Quantize to 2 decimal places safely
        return v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


class ExpenseCreate(ExpenseBase):
    pass


class ExpenseResponse(BaseModel):
    id: int
    amount: float
    category: str
    note: Optional[str]
    date: date
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_validator("amount", mode="before")
    @classmethod
    def serialize_amount(cls, v: Union[Decimal, float, int, str]) -> float:
        return float(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


class ExpenseListResponse(BaseModel):
    items: List[ExpenseResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class MonthOverMonthSummary(BaseModel):
    current_month: float
    previous_month: float
    change_percent: Optional[float]


class CategoryInsight(BaseModel):
    category: str
    increase_percent: float
    message: str


class CategorySpendingInsight(BaseModel):
    category: str
    previous_month: float
    current_month: float
    change_percent: Optional[float]
    flagged: bool


class SummaryResponse(BaseModel):
    period: str
    total_spend: float
    transaction_count: int
    spend_by_category: Dict[str, float]
    category_percentages: Dict[str, float]
    month_over_month: MonthOverMonthSummary
    insights: List[CategoryInsight] = Field(default_factory=list)
    category_insights: List[CategorySpendingInsight] = Field(default_factory=list)
