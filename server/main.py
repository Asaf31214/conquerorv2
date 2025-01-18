import os

import uvicorn
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException, status

load_dotenv()
ENVIRONMENT = os.environ.get("ENVIRONMENT")
API_KEY = os.getenv("API_KEY")


async def require_api_key(x_api_key: str = Header(None)):
    if ENVIRONMENT == "CLOUD" and x_api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid API key",
        )


app = FastAPI()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/",dependencies=[Depends(require_api_key)])
async def root():
    return {"message": "Hello World"}


@app.get("/env")
async def env():
    return {"ENV": ENVIRONMENT, "API_KEY": API_KEY, "ALL": os.environ}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
