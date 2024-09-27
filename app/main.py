from fastapi import FastAPI
from app.routers import player

app = FastAPI()

app.include_router(player.router)

@app.get("/")
async def root():
    return {"message": "The switcher"}
