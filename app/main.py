from fastapi import FastAPI
from routes import user_routes, post_routes, comment_routes
from app.database import Base, engine
from models import user_model, post_model, comment_model

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(user_routes.router)
app.include_router(post_routes.router)
app.include_router(comment_routes.router)

@app.get("/")
def root():
    return {"message": "Blog API is running"}