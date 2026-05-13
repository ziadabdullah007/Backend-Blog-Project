from typing import Optional

from pydantic import BaseModel, Field


class PostCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: str = Field(..., min_length=3)


class PostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = Field(None, min_length=3)


class PostResponse(BaseModel):
    id: int
    title: str
    content: str
    user_id: int

    model_config = {"from_attributes": True}


class PaginatedPostsResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: list[PostResponse]