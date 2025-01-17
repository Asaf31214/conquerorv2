import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI

load_dotenv()
app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/env")
async def env():
    key = os.environ.get("API_KEY")
    env_ = os.environ.get("ENV")
    return {"key": key, "env": env_}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
