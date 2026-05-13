import time
import logging
from fastapi import Request

logger = logging.getLogger("http")


async def logging_middleware(request: Request, call_next):
    start = time.time()

    response = await call_next(request)

    duration = (time.time() - start) * 1000

    logger.info(
        f"{request.method} {request.url.path} "
        f"status={response.status_code} "
        f"duration={duration:.2f}ms"
    )

    return response