from typing import Optional

from pydantic import BaseModel, Field


class CommentCreate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)
    post_id: int
    parent_id: Optional[int] = None


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    replies: list["CommentResponse"] = Field(default_factory=list)

    model_config = {"from_attributes": True}


class PaginatedCommentsResponse(BaseModel):
    page: int
    limit: int
    total: int
    data: list[CommentResponse]


CommentResponse.model_rebuild()