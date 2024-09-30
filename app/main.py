from fastapi import FastAPI
from app.routers.match_routers import router as MatchRouter
from app.routers.player_routers import router as PlayerRouter
from app.database import engine, Base
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:80",
    "http://localhost:8000",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

app.include_router(MatchRouter)
app.include_router(PlayerRouter)

@app.get("/")
async def root():
    return {"message": "The switcher"}