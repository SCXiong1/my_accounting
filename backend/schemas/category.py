from pydantic import BaseModel, Field


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=32)
    icon: str = Field(default="📦", max_length=10)
    color: str = Field(default="#607D8B", max_length=7)


class CategoryUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=32)
    icon: str | None = Field(default=None, max_length=10)
    color: str | None = Field(default=None, max_length=7)


class CategorySortItem(BaseModel):
    id: int
    display_order: int


class CategorySortRequest(BaseModel):
    orders: list[CategorySortItem]


class CategoryResponse(BaseModel):
    id: int
    name: str
    icon: str
    color: str
    display_order: int
    expense_count: int = 0
    total_amount: int = 0

    model_config = {"from_attributes": True}
