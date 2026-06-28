import aiosqlite
import config

DATABASE = config.DATABASE_PATH


async def connect():
    return await aiosqlite.connect(DATABASE)


async def setup_database():
    async with aiosqlite.connect(DATABASE) as db:

        # =========================
        # Users
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            xp INTEGER DEFAULT 0,
            level INTEGER DEFAULT 1,
            balance INTEGER DEFAULT 0,
            daily_claim INTEGER DEFAULT 0
        )
        """)

        # =========================
        # Premium
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS premium (
            user_id INTEGER PRIMARY KEY,
            plan TEXT,
            purchase_date TEXT,
            expiry_date TEXT
        )
        """)

        # =========================
        # Warnings
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS warnings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            user_id INTEGER,
            moderator_id INTEGER,
            reason TEXT,
            timestamp TEXT
        )
        """)

        # =========================
        # Tickets
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            channel_id INTEGER,
            creator_id INTEGER,
            ticket_type TEXT,
            status TEXT
        )
        """)

        # =========================
        # Giveaways
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS giveaways (
            giveaway_id INTEGER PRIMARY KEY AUTOINCREMENT,
            guild_id INTEGER,
            channel_id INTEGER,
            message_id INTEGER,
            prize TEXT,
            winners INTEGER,
            end_time TEXT
        )
        """)

        # =========================
        # Bug Reports
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS bug_reports (
            bug_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            title TEXT,
            description TEXT,
            priority TEXT,
            status TEXT
        )
        """)

        # =========================
        # Server Settings
        # =========================
        await db.execute("""
        CREATE TABLE IF NOT EXISTS settings (
            guild_id INTEGER PRIMARY KEY,
            welcome_channel INTEGER,
            log_channel INTEGER,
            ticket_category INTEGER,
            premium_log_channel INTEGER
        )
        """)

        await db.commit()

        print("✅ Database initialized successfully.")
