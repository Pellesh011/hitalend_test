import time
import logging
from sqlalchemy import event
from sqlalchemy.engine import Engine

logger = logging.getLogger("sql")


def setup_sql_logging(engine: Engine):

    @event.listens_for(engine.sync_engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._start_time = time.time()

        logger.info({
            "event": "sql_start",
            "statement": statement,
            "params": str(parameters),
        })

    @event.listens_for(engine.sync_engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        duration = (time.time() - context._start_time) * 1000

        logger.info({
            "event": "sql_end",
            "duration_ms": round(duration, 2),
            "statement": statement,
        })