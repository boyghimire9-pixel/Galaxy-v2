"""
Galaxy AI V2
Database Setup
"""

import asyncio
from database.database import setup_database


async def initialize_database():
    """Initialize all database tables."""
    try:
        await setup_database()
        print("✅ Galaxy AI database initialized successfully.")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")


if __name__ == "__main__":
    asyncio.run(initialize_database())
