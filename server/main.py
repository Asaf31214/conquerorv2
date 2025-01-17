import os

import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/")
def root():
    return {"message": "Hello World 3"}

@app.get("/env")
def env():
    key = os.getenv("API_KEY")
    env_ = os.getenv("ENVIRONMENT")
    return {"key": key, "env": env_}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
