import aiosqlite
import config

DATABASE = config.DATABASE_PATH


class Database:

    @staticmethod
    async def connect():
        return await aiosqlite.connect(DATABASE)

    @staticmethod
    async def initialize():

        async with aiosqlite.connect(DATABASE) as db:

            # ==========================
            # Economy
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS economy (
                user_id INTEGER PRIMARY KEY,
                wallet INTEGER DEFAULT 0,
                bank INTEGER DEFAULT 0,
                last_daily INTEGER DEFAULT 0,
                last_work INTEGER DEFAULT 0
            )
            """)

            # ==========================
            # Levels
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS levels (
                user_id INTEGER,
                guild_id INTEGER,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                PRIMARY KEY(user_id, guild_id)
            )
            """)

            # ==========================
            # Premium
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS premium (
                user_id INTEGER PRIMARY KEY,
                expires_at INTEGER,
                premium_type TEXT
            )
            """)

            # ==========================
            # Tickets
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS tickets (
                channel_id INTEGER PRIMARY KEY,
                user_id INTEGER,
                guild_id INTEGER,
                created_at INTEGER,
                status TEXT
            )
            """)

            # ==========================
            # Warnings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS warnings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                guild_id INTEGER,
                user_id INTEGER,
                moderator_id INTEGER,
                reason TEXT,
                created_at INTEGER
            )
            """)

            await db.commit()
          # ==========================
            # Bug Reports
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS bug_reports (
                bug_id TEXT PRIMARY KEY,
                reporter_id INTEGER,
                message_id INTEGER,
                guild_id INTEGER,
                title TEXT,
                description TEXT,
                status TEXT DEFAULT 'Open',
                priority TEXT DEFAULT 'Medium',
                developer_notes TEXT DEFAULT '',
                assigned_to INTEGER DEFAULT NULL,
                created_at INTEGER DEFAULT (strftime('%s','now'))
            )
            """)

            # ==========================
            # Giveaways
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS giveaways (
                message_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                guild_id INTEGER,
                prize TEXT,
                winners INTEGER,
                ends_at INTEGER,
                hosted_by INTEGER,
                ended INTEGER DEFAULT 0
            )
            """)

            # ==========================
            # Logging Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS logging_settings (
                guild_id INTEGER PRIMARY KEY,
                log_channel_id INTEGER
            )
            """)

            # ==========================
            # Welcome Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS welcome_settings (
                guild_id INTEGER PRIMARY KEY,
                channel_id INTEGER,
                message TEXT,
                auto_role INTEGER
            )
            """)

            # ==========================
            # Ticket Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS ticket_settings (
                guild_id INTEGER PRIMARY KEY,
                category_id INTEGER,
                transcript_channel INTEGER,
                support_role INTEGER
            )
            """)
          # ==========================
            # Economy Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS economy_settings (
                guild_id INTEGER PRIMARY KEY,
                currency_name TEXT DEFAULT 'Credits',
                currency_symbol TEXT DEFAULT '💰',
                daily_reward INTEGER DEFAULT 1000,
                work_min INTEGER DEFAULT 500,
                work_max INTEGER DEFAULT 3000,
                max_balance INTEGER DEFAULT 100000000000000000000
            )
            """)

            # ==========================
            # Level Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS level_settings (
                guild_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                levelup_channel INTEGER,
                levelup_message TEXT DEFAULT '🎉 {user} reached level {level}!',
                levelup_role INTEGER,
                xp_min INTEGER DEFAULT 15,
                xp_max INTEGER DEFAULT 25,
                cooldown INTEGER DEFAULT 60
            )
            """)

            # ==========================
            # AutoMod Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS automod_settings (
                guild_id INTEGER PRIMARY KEY,
                anti_spam INTEGER DEFAULT 1,
                anti_links INTEGER DEFAULT 0,
                anti_invites INTEGER DEFAULT 1,
                anti_mentions INTEGER DEFAULT 1,
                anti_caps INTEGER DEFAULT 1,
                bad_words INTEGER DEFAULT 1
            )
            """)

            # ==========================
            # AI Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS ai_settings (
                guild_id INTEGER PRIMARY KEY,
                enabled INTEGER DEFAULT 1,
                ai_channel INTEGER,
                model TEXT DEFAULT 'gpt-5.5',
                max_history INTEGER DEFAULT 20
            )
            """)

            # ==========================
            # Premium Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS premium_settings (
                guild_id INTEGER PRIMARY KEY,
                premium_role INTEGER,
                premium_log_channel INTEGER
            )
            """)
          # ==========================
            # Command Usage
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS command_usage (
                command_name TEXT PRIMARY KEY,
                uses INTEGER DEFAULT 0
            )
            """)

            # ==========================
            # User Profiles
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                user_id INTEGER PRIMARY KEY,
                bio TEXT DEFAULT '',
                birthday TEXT DEFAULT '',
                favorite_color TEXT DEFAULT '',
                timezone TEXT DEFAULT '',
                created_at INTEGER DEFAULT (strftime('%s','now'))
            )
            """)

            # ==========================
            # Global Configuration
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS global_config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT
            )
            """)

            # ==========================
            # Notification Settings
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS notification_settings (
                user_id INTEGER PRIMARY KEY,
                dm_notifications INTEGER DEFAULT 1,
                reminder_notifications INTEGER DEFAULT 1,
                giveaway_notifications INTEGER DEFAULT 1,
                level_notifications INTEGER DEFAULT 1
            )
            """)

            # ==========================
            # Bot Statistics
            # ==========================

            await db.execute("""
            CREATE TABLE IF NOT EXISTS bot_statistics (
                stat_name TEXT PRIMARY KEY,
                stat_value INTEGER DEFAULT 0
            )
            """)
          # ==========================
    # Execute Query
    # ==========================

    @staticmethod
    async def execute(query: str, parameters: tuple = ()):

        async with aiosqlite.connect(DATABASE) as db:
            await db.execute(query, parameters)
            await db.commit()

    # ==========================
    # Fetch One
    # ==========================

    @staticmethod
    async def fetchone(query: str, parameters: tuple = ()):

        async with aiosqlite.connect(DATABASE) as db:
            cursor = await db.execute(query, parameters)
            return await cursor.fetchone()

    # ==========================
    # Fetch All
    # ==========================

    @staticmethod
    async def fetchall(query: str, parameters: tuple = ()):

        async with aiosqlite.connect(DATABASE) as db:
            cursor = await db.execute(query, parameters)
            return await cursor.fetchall()

    # ==========================
    # Execute Many
    # ==========================

    @staticmethod
    async def executemany(query: str, parameters: list):

        async with aiosqlite.connect(DATABASE) as db:
            await db.executemany(query, parameters)
            await db.commit()

    # ==========================
    # Database Health Check
    # ==========================

    @staticmethod
    async def health_check():

        try:
            async with aiosqlite.connect(DATABASE) as db:
                await db.execute("SELECT 1")
                return True

        except Exception:
            return False

    # ==========================
    # Close Connection
    # ==========================

    @staticmethod
    async def close(connection):

        if connection:
            await connection.close()
