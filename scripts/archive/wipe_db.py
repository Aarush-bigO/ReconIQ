import asyncio
from database.session import engine
from sqlalchemy import text

async def wipe():
    async with engine.begin() as conn:
        await conn.execute(text("TRUNCATE TABLE transactions CASCADE;"))
    print("Transactions truncated.")

asyncio.run(wipe())
