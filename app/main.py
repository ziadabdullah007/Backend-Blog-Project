from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routes import user_routes, post_routes, comment_routes
from app.database import Base, engine
from models import user_model, post_model, comment_model
from auth import auth_routes
from prometheus_fastapi_instrumentator import Instrumentator


Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(post_routes.router)
app.include_router(comment_routes.router)


Instrumentator().instrument(app).expose(app)

app.mount("/static", StaticFiles(directory="front"), name="static")

@app.get("/")
def root():
    return FileResponse("front/index.html")