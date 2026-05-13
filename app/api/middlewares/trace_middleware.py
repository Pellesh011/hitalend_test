import logging
import time
import uuid

from starlette.types import ASGIApp
from starlette.types import Receive
from starlette.types import Scope
from starlette.types import Send

from app.core.trace import trace_id_ctx


logger = logging.getLogger("http")


class TraceMiddleware:

    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(
        self,
        scope: Scope,
        receive: Receive,
        send: Send,
    ):

        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        start_time = time.perf_counter()

        headers = dict(scope["headers"])

        trace_id = headers.get(
            b"x-trace-id",
            uuid.uuid4().hex.encode(),
        ).decode()

        token = trace_id_ctx.set(trace_id)

        method = scope["method"]
        path = scope["path"]

        status_code = 500

        async def send_wrapper(message):

            nonlocal status_code

            if message["type"] == "http.response.start":

                status_code = message["status"]

                response_headers = message.setdefault(
                    "headers",
                    [],
                )

                response_headers.append(
                    (
                        b"x-trace-id",
                        trace_id.encode(),
                    )
                )

            await send(message)

        try:

            await self.app(
                scope,
                receive,
                send_wrapper,
            )

        except Exception:

            logger.exception(
                "request failed method=%s path=%s",
                method,
                path,
            )

            raise

        finally:

            duration_ms = (
                time.perf_counter() - start_time
            ) * 1000

            logger.info(
                "%s %s status=%s duration=%.2fms",
                method,
                path,
                status_code,
                duration_ms,
            )

            trace_id_ctx.reset(token)