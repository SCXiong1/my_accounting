from pydantic import BaseModel, Field


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=32)


class TagUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=32)


class TagSortItem(BaseModel):
    id: int
    display_order: int


class TagSortRequest(BaseModel):
    orders: list[TagSortItem]


class TagResponse(BaseModel):
    id: int
    name: str
    display_order: int
    expense_count: int = 0

    model_config = {"from_attributes": True}
