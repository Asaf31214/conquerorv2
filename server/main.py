import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status

load_dotenv()
ENVIRONMENT = os.environ.get("ENVIRONMENT")
API_KEY = os.getenv("API_KEY")


async def require_api_key(x_api_key: str = Header(None)):
    print(f"API_KEY: {API_KEY}")
    print(f"x_api_key: {x_api_key}")
    print(f"ENVIRONMENT: {ENVIRONMENT}")
    if ENVIRONMENT == "CLOUD" and x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )


app = FastAPI(dependencies=[Depends(require_api_key)])


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
