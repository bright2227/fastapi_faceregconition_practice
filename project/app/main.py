import asyncio

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.db import check_db_alive, close_db
from app.routers import user


app = FastAPI()
app.include_router(user.router)


@app.on_event("startup")
async def on_startup():
    await check_db_alive()

@app.on_event("shutdown")
async def shutdown():
    await close_db()


@app.exception_handler(asyncio.TimeoutError)
async def unicorn_exception_handler(request: Request, exc: asyncio.TimeoutError ):
    if exc.args:
        msg = exc.args[0]
    else:
        msg = "Tasks Timeout "
    return JSONResponse(
        status_code=408,
        content={"message": msg},
    )
