from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator
from routes import user_routes, post_routes, comment_routes
from auth import auth_routes
from app.database import Base, engine
from models import user_model, post_model, comment_model

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Instrumentator().instrument(app).expose(app)

app.include_router(user_routes.router)
app.include_router(post_routes.router)
app.include_router(comment_routes.router)
app.include_router(auth_routes.router)

@app.get("/")
def root():
    return {"message": "Blog API is running"}