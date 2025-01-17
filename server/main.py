import os

import dotenv
import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, status

dotenv.load_dotenv()


async def require_api_key(x_api_key: str = Header(None)):
    API_KEY = os.getenv("API_KEY")
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )


app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/secret")
def secret():
    return (
        {"message": "This is a secret endpoint. You need to provide an API key."},
        status.HTTP_200_OK,
    )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
