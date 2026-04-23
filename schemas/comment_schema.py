from pydantic import BaseModel


class CommentCreate(BaseModel):
    content: str
    post_id: int


class CommentResponse(BaseModel):
    id: int
    content: str
    post_id: int

    class Config:
        orm_mode = True
        