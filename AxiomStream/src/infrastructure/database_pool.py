import asyncio
import os
import sys
import logging
import asyncpg

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("DB_POOL")

class DatabasePoolManager:
    def __init__(self):
        self._pool: asyncpg.Pool | None = None
        self.dsn = os.getenv("DATABASE_URL", "postgresql://postgres:securepassword@localhost:5432/axiom_db")
        self.min_size = int(os.getenv("DB_POOL_MIN_SIZE", "10"))
        self.max_size = int(os.getenv("DB_POOL_MAX_SIZE", "50"))

    async def initialize_pool(self):
        if self._pool is not None:
            return
        try:
            logger.info("🔌 [DB-POOL] Initializing database pool...")
            self._pool = await asyncpg.create_pool(dsn=self.dsn, min_size=self.min_size, max_size=self.max_size)
        except Exception as e:
            logger.error(f"❌ Failure: {str(e)}")
            raise

    async def execute_query(self, query: str, *args):
        if not self._pool: await self.initialize_pool()
        async with self._pool.acquire() as conn: return await conn.execute(query, *args)

    async def close_pool(self):
        if self._pool: await self._pool.close()

db_manager = DatabasePoolManager()
