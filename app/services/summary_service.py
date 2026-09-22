import calendar
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.repositories.expense_repository import expense_repository
from app.schemas import (
    SummaryResponse,
    MonthOverMonthSummary,
    CategoryInsight,
    CategorySpendingInsight,
)


class SummaryService:
    def get_summary(
        self,
        db: Session,
        user_id: int,
        year: Optional[int] = None,
        month: Optional[int] = None,
    ) -> SummaryResponse:
        today = date.today()
        target_year = year if year else today.year
        target_month = month if month else today.month

        # Determine current month boundary
        _, last_day_current = calendar.monthrange(target_year, target_month)
        current_start = date(target_year, target_month, 1)
        current_end = date(target_year, target_month, last_day_current)

        # Determine previous month boundary
        if target_month == 1:
            prev_year = target_year - 1
            prev_month = 12
        else:
            prev_year = target_year
            prev_month = target_month - 1

        _, last_day_prev = calendar.monthrange(prev_year, prev_month)
        prev_start = date(prev_year, prev_month, 1)
        prev_end = date(prev_year, prev_month, last_day_prev)

        # Fetch current month metrics
        current_total, current_count = expense_repository.get_period_total_and_count(
            db, user_id, current_start, current_end
        )
        current_cat_tuples = expense_repository.get_period_category_totals(
            db, user_id, current_start, current_end
        )
        current_categories: Dict[str, Decimal] = {
            cat: amt for cat, amt in current_cat_tuples
        }

        # Fetch previous month metrics
        prev_total, _ = expense_repository.get_period_total_and_count(
            db, user_id, prev_start, prev_end
        )
        prev_cat_tuples = expense_repository.get_period_category_totals(
            db, user_id, prev_start, prev_end
        )
        prev_categories: Dict[str, Decimal] = {
            cat: amt for cat, amt in prev_cat_tuples
        }

        # Calculate MoM percentage change
        mom_change_percent: Optional[float] = None
        if prev_total > Decimal("0"):
            change = (current_total - prev_total) / prev_total * Decimal("100")
            mom_change_percent = float(change.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
        elif prev_total == Decimal("0") and current_total == Decimal("0"):
            mom_change_percent = 0.0

        # Calculate category percentages
        category_percentages: Dict[str, float] = {}
        for cat, amt in current_categories.items():
            if current_total > Decimal("0"):
                pct = (amt / current_total) * Decimal("100")
                category_percentages[cat] = float(pct.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
            else:
                category_percentages[cat] = 0.0

        # Calculate category spending insights (Bonus Feature 2)
        all_categories = sorted(set(current_categories.keys()) | set(prev_categories.keys()))
        category_insights: List[CategorySpendingInsight] = []
        insights: List[CategoryInsight] = []

        for cat in all_categories:
            curr_amt = current_categories.get(cat, Decimal("0"))
            prev_amt = prev_categories.get(cat, Decimal("0"))

            curr_float = float(curr_amt.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
            prev_float = float(prev_amt.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))

            if prev_amt > Decimal("0"):
                diff = curr_amt - prev_amt
                cat_growth = (diff / prev_amt) * Decimal("100")
                change_pct = float(cat_growth.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP))
                # Strictly greater than 20%
                flagged = cat_growth > Decimal("20.0")
            else:
                change_pct = None
                flagged = False

            category_insights.append(
                CategorySpendingInsight(
                    category=cat,
                    previous_month=prev_float,
                    current_month=curr_float,
                    change_percent=change_pct,
                    flagged=flagged,
                )
            )

            if flagged and change_pct is not None:
                insights.append(
                    CategoryInsight(
                        category=cat,
                        increase_percent=change_pct,
                        message=f"{cat} spending increased by {change_pct}% compared with previous month.",
                    )
                )

        month_name = calendar.month_name[target_month]
        period_str = f"{month_name} {target_year}"

        return SummaryResponse(
            period=period_str,
            total_spend=float(current_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
            transaction_count=current_count,
            spend_by_category={
                k: float(v.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))
                for k, v in current_categories.items()
            },
            category_percentages=category_percentages,
            month_over_month=MonthOverMonthSummary(
                current_month=float(current_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                previous_month=float(prev_total.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)),
                change_percent=mom_change_percent,
            ),
            insights=insights,
            category_insights=category_insights,
        )


summary_service = SummaryService()
