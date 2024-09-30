from fastapi import FastAPI
from app.routers.match_routers import router as MatchRouter
from app.routers.player_routers import router as PlayerRouter
from app.database import engine, Base

app = FastAPI()

Base.metadata.drop_all(engine)

Base.metadata.create_all(engine)

app.include_router(MatchRouter)
app.include_router(PlayerRouter)

@app.get("/")
async def root():
    return {"message": "The switcher"}