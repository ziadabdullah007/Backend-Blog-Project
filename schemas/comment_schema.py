from pydantic import BaseModel
from typing import Optional, List


class CommentCreate(BaseModel):
    content: str
    post_id: int
    parent_id: Optional[int] = None


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int
    user_id: int
    parent_id: Optional[int] = None
    replies: List["CommentResponse"] = []

    class Config:
        from_attributes = True


CommentResponse.model_rebuild()