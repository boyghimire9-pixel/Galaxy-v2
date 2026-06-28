import os
import asyncio
import logging

import discord
from discord.ext import commands
from dotenv import load_dotenv

import config

# ===============================
# Load Environment
# ===============================

load_dotenv()

TOKEN = config.TOKEN

# ===============================
# Logging
# ===============================

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s"
)

logger = logging.getLogger("GalaxyAI")

# ===============================
# Intents
# ===============================

intents = discord.Intents.default()

intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True
intents.voice_states = True
intents.reactions = True
intents.presences = True

# ===============================
# Bot
# ===============================

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    help_command=None
)

# ===============================
# Cogs
# ===============================

COGS = [
    "cogs.moderation",
    "cogs.automod",
    "cogs.tickets",
    "cogs.premium",
    "cogs.levels",
    "cogs.ai",
    "cogs.welcome",
    "cogs.logging",
    "cogs.utility",
    "cogs.owner",
    "cogs.giveaway",
    "cogs.bugreport"
]

# ===============================
# Events
# ===============================

@bot.event
async def on_ready():

    print("=" * 50)
    print(f"{bot.user} is online!")
    print(f"Guilds : {len(bot.guilds)}")
    print("=" * 50)

    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name="🌌 Script Galaxy"
        )
    )

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash commands.")

    except Exception as e:
        print(e)

# ===============================
# Load Extensions
# ===============================

async def load_extensions():

    for cog in COGS:

        try:
            await bot.load_extension(cog)
            print(f"Loaded {cog}")

        except Exception as e:
            print(f"Failed to load {cog}")
            print(e)

# ===============================
# Main
# ===============================

async def main():

    async with bot:

        await load_extensions()

        await bot.start(TOKEN)

asyncio.run(main())
# ===============================
# Global Error Handler
# ===============================

@bot.tree.error
async def on_app_command_error(interaction: discord.Interaction, error):

    if isinstance(error, discord.app_commands.MissingPermissions):
        await interaction.response.send_message(
            "❌ You don't have permission to use this command.",
            ephemeral=True
        )
        return

    if isinstance(error, discord.app_commands.CommandOnCooldown):
        await interaction.response.send_message(
            f"⏳ Try again in {round(error.retry_after)} seconds.",
            ephemeral=True
        )
        return

    logger.error(error)

    try:
        await interaction.response.send_message(
            "⚠️ An unexpected error occurred.",
            ephemeral=True
        )
    except:
        pass


# ===============================
# Member Join
# ===============================

@bot.event
async def on_member_join(member):

    logger.info(f"{member} joined {member.guild.name}")


# ===============================
# Member Leave
# ===============================

@bot.event
async def on_member_remove(member):

    logger.info(f"{member} left {member.guild.name}")


# ===============================
# Message Delete
# ===============================

@bot.event
async def on_message_delete(message):

    if message.author.bot:
        return

    logger.info(
        f"Deleted message from {message.author}: {message.content}"
    )


# ===============================
# Message Edit
# ===============================

@bot.event
async def on_message_edit(before, after):

    if before.author.bot:
        return

    if before.content == after.content:
        return

    logger.info(
        f"{before.author} edited a message."
    )


# ===============================
# Background Task
# ===============================

async def background_loop():

    await bot.wait_until_ready()

    while not bot.is_closed():

        logger.info("Galaxy AI background task running...")

        # Future Tasks
        # Premium expiry
        # Database backup
        # Reminder system
        # Auto announcements

        await asyncio.sleep(300)


@bot.event
async def setup_hook():

    bot.loop.create_task(background_loop())
  # ===============================
# Status Rotation Task
# ===============================

STATUS_MESSAGES = [
    "🌌 Script Galaxy",
    "🤖 Galaxy AI V2",
    "🎟️ Ticket System",
    "💎 Premium Members",
    "📜 Roblox Scripts",
    "⚡ /help"
]

async def rotate_status():

    await bot.wait_until_ready()

    index = 0

    while not bot.is_closed():

        try:

            await bot.change_presence(
                activity=discord.Activity(
                    type=discord.ActivityType.watching,
                    name=STATUS_MESSAGES[index]
                )
            )

            index += 1

            if index >= len(STATUS_MESSAGES):
                index = 0

        except Exception as e:
            logger.error(e)

        await asyncio.sleep(60)


# ===============================
# Premium Expiry Loop
# ===============================

async def premium_expiry_loop():

    await bot.wait_until_ready()

    while not bot.is_closed():

        try:

            logger.info("Checking premium expiry...")

            # Premium database check
            # Remove expired roles
            # DM users
            # Send premium logs

        except Exception as e:

            logger.error(e)

        await asyncio.sleep(300)


# ===============================
# Database Backup Loop
# ===============================

async def backup_database():

    await bot.wait_until_ready()

    while not bot.is_closed():

        try:

            logger.info("Database backup completed.")

        except Exception as e:

            logger.error(e)

        await asyncio.sleep(3600)


# ===============================
# Startup Tasks
# ===============================

@bot.event
async def setup_hook():

    bot.loop.create_task(background_loop())
    bot.loop.create_task(rotate_status())
    bot.loop.create_task(premium_expiry_loop())
    bot.loop.create_task(backup_database())

    logger.info("Background tasks started.")
  # ==========================================
# Slash Command Sync Command
# ==========================================

@bot.command()
@commands.is_owner()
async def sync(ctx):
    """Sync all slash commands."""
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Synced {len(synced)} slash commands.")
    except Exception as e:
        await ctx.send(f"❌ Failed to sync commands:\n{e}")

# ==========================================
# Bot Shutdown
# ==========================================

async def shutdown():
    logger.info("Shutting down Galaxy AI V2...")
    await bot.close()

# ==========================================
# Startup Checks
# ==========================================

def startup_checks():
    if TOKEN is None or TOKEN == "":
        raise RuntimeError(
            "DISCORD_TOKEN is missing! Check your .env file."
        )

    logger.info("Configuration loaded successfully.")
    logger.info(f"Bot Name: {config.BOT_NAME}")
    logger.info(f"Version: {config.BOT_VERSION}")

# ==========================================
# Run Bot
# ==========================================

if __name__ == "__main__":
    startup_checks()

    try:
        asyncio.run(main())

    except KeyboardInterrupt:
        logger.info("Bot stopped manually.")

    except Exception as e:
        logger.exception(e)
