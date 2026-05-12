from pydantic import BaseModel, Field


class ExpenseCreate(BaseModel):
    amount: int = Field(gt=0)
    category_id: int
    tag_ids: list[int] = Field(default_factory=list)
    transaction_time: int
    timezone_offset: int = Field(default=480)
    note: str = Field(default="", max_length=255)


class ExpenseUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    category_id: int | None = None
    tag_ids: list[int] | None = None
    transaction_time: int | None = None
    timezone_offset: int | None = None
    note: str | None = Field(default=None, max_length=255)


class TagBrief(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class CategoryBrief(BaseModel):
    id: int
    name: str
    icon: str
    color: str

    model_config = {"from_attributes": True}


class ExpenseResponse(BaseModel):
    id: int
    amount: int
    category: CategoryBrief
    tags: list[TagBrief] = Field(default_factory=list)
    transaction_time: int
    timezone_offset: int
    note: str

    model_config = {"from_attributes": True}


class ExpenseListResponse(BaseModel):
    items: list[ExpenseResponse]
    next_cursor: int | None = None
    total: int = 0
