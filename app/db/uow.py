import time
import logging

from app.repositories.department import DepartmentRepository
from app.repositories.employee import EmployeeRepository

logger = logging.getLogger("uow")


class UnitOfWork:
    def __init__(self, session_factory):
        self.session = None
        self._start_time = None
        self._session_factory = session_factory

    async def __aenter__(self):
        self._start_time = time.time()

        self.session = self._session_factory()
        self.departments = DepartmentRepository(self.session)
        self.employees = EmployeeRepository(self.session)

        logger.info(
            {
                "event": "uow_start",
            }
        )

        return self

    async def __aexit__(self, exc_type, exc, tb):
        duration_ms = (time.time() - self._start_time) * 1000

        if exc:
            await self.session.rollback()

            logger.error(
                {
                    "event": "uow_rollback",
                    "reason": str(exc),
                    "duration_ms": round(duration_ms, 2),
                }
            )
        else:
            await self.session.commit()

            logger.info(
                {
                    "event": "uow_commit",
                    "duration_ms": round(duration_ms, 2),
                }
            )

        await self.session.close()

        logger.info(
            {
                "event": "uow_close",
            }
        )

    async def commit(self):
        logger.info({"event": "manual_commit"})
        await self.session.commit()

    async def rollback(self):
        logger.warning({"event": "manual_rollback"})
        await self.session.rollback()
