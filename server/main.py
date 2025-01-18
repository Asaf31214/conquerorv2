import uvicorn
from fastapi import FastAPI


async def startup():
    print("Starting up")

async def shutdown():
    print("Shutting down")
app = FastAPI(on_startup=[startup], on_shutdown=[shutdown])

@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.get("/")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
