from pydantic import BaseModel


class OverviewResponse(BaseModel):
    today: int = 0
    this_week: int = 0
    this_month: int = 0
    this_year: int = 0


class CategoryStatItem(BaseModel):
    category_id: int
    category_name: str
    category_icon: str
    category_color: str
    total_amount: int = 0
    percentage: float = 0.0
    transaction_count: int = 0


class TagStatItem(BaseModel):
    tag_id: int
    tag_name: str
    total_amount: int = 0
    percentage: float = 0.0
    transaction_count: int = 0


class MonthlyCategoryDetail(BaseModel):
    category_id: int
    category_name: str
    category_icon: str
    category_color: str
    amount: int = 0


class MonthlyTagDetail(BaseModel):
    tag_id: int
    tag_name: str
    amount: int = 0


class MonthlyStatItem(BaseModel):
    year: int
    month: int
    total_amount: int = 0
    transaction_count: int = 0
    by_category: list[MonthlyCategoryDetail] = []
    by_tag: list[MonthlyTagDetail] = []
