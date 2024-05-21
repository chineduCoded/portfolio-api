import time
from typing import Any, Callable, TypeVar
from fastapi import Request, Response
from loguru import logger

F = TypeVar("F", bound=Callable[..., Any])

async def log_middleware(request: Request, call_next: F) -> Response:
    start_time = time.time()
    response = await call_next(request)
    process_time = round(time.time() - start_time, 3)
    response.headers["X-Process-Time"] = str(process_time)

    logger.info(
        "method: {method} | path: {path} | status_code: {status_code} | process_time: {process_time:.2f}s",
        method=request.method,
        path=request.url.path,
        status_code=response.status_code,
        process_time=process_time,
    )

    return response