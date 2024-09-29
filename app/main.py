from fastapi import FastAPI
from app.routers.match_routers import router as MatchRouter
from app.routers.player_routers import router as PlayerRouter

app = FastAPI()
app.include_router(MatchRouter)
app.include_router(PlayerRouter)

@app.get("/")
async def root():
    return {"message": "The switcher"}