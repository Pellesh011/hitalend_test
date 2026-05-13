from contextvars import ContextVar
import logging
from typing import Optional

trace_id_ctx: Optional[ContextVar[str]] = ContextVar(
    "trace_id",
    default=None,
)


class TraceIdFilter(logging.Filter):

    def filter(self, record):

        record.trace_id = trace_id_ctx.get() or "-"

        return True