from pydantic import BaseModel, Field

from schemas.base import BaseSchema


class TransactionCreate(BaseModel):
    amount: int = Field(gt=0)
    category_id: int
    tag_ids: list[int] = Field(default_factory=list)
    transaction_time: int
    timezone_offset: int = Field(default=480)  # UTC+8 in minutes
    note: str = Field(default="", max_length=255)
    type: str = "expense"


class TransactionUpdate(BaseModel):
    amount: int | None = Field(default=None, gt=0)
    category_id: int | None = None
    tag_ids: list[int] | None = None
    transaction_time: int | None = None
    timezone_offset: int | None = None
    note: str | None = Field(default=None, max_length=255)
    type: str | None = None


class TagBrief(BaseSchema):
    id: int
    name: str


class CategoryBrief(BaseSchema):
    id: int
    name: str
    icon: str
    color: str


class TransactionResponse(BaseSchema):
    id: int
    amount: int
    category: CategoryBrief
    tags: list[TagBrief] = Field(default_factory=list)
    transaction_time: int
    timezone_offset: int
    note: str
    type: str


class TransactionListResponse(BaseModel):
    items: list[TransactionResponse]
    next_cursor: int | None = None
    total: int = 0


class BatchDeleteRequest(BaseModel):
    ids: list[int] = Field(min_length=1)
