from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from models.post_model import Post
from schemas.post_schema import PostCreate
from app.redis_client import redis_client
from app.logger import logger
import json

router = APIRouter(prefix="/posts", tags=["Posts"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def clear_posts_cache():
    for key in redis_client.scan_iter("posts:*"):
        redis_client.delete(key)


@router.post("/")
def create_post(post: PostCreate, db: Session = Depends(get_db)):
    new_post = Post(
        title=post.title,
        content=post.content,
        user_id=post.user_id
    )

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    clear_posts_cache()
    logger.info(f"POST /posts created post id={new_post.id}")

    return {
        "id": new_post.id,
        "title": new_post.title,
        "content": new_post.content,
        "user_id": new_post.user_id
    }


@router.get("/")
def get_posts(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db)
):
    logger.info(f"GET /posts?page={page}&limit={limit}")

    cache_key = f"posts:page={page}:limit={limit}"

    cached_posts = redis_client.get(cache_key)
    if cached_posts:
        logger.info(f"GET /posts?page={page}&limit={limit} from Redis cache")
        return json.loads(cached_posts)

    skip = (page - 1) * limit

    posts = db.query(Post).order_by(Post.id).offset(skip).limit(limit).all()
    total = db.query(Post).count()

    posts_data = []

    for post in posts:
        posts_data.append({
            "id": post.id,
            "title": post.title,
            "content": post.content,
            "user_id": post.user_id
        })

    response = {
        "page": page,
        "limit": limit,
        "total": total,
        "data": posts_data
    }

    redis_client.setex(cache_key, 60, json.dumps(response))
    logger.info(f"GET /posts?page={page}&limit={limit} from database and saved to Redis")

    return response


@router.get("/{post_id}")
def get_post(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"GET /posts/{post_id}")

    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        logger.warning(f"GET /posts/{post_id} - Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    return {
        "id": post.id,
        "title": post.title,
        "content": post.content,
        "user_id": post.user_id
    }


@router.delete("/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    logger.info(f"DELETE /posts/{post_id}")

    post = db.query(Post).filter(Post.id == post_id).first()

    if post is None:
        logger.warning(f"DELETE /posts/{post_id} - Post not found")
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    clear_posts_cache()
    logger.info(f"DELETE /posts/{post_id} success and posts cache cleared")

    return {"message": "Post deleted"}