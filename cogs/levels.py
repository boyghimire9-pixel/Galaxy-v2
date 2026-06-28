import discord
import aiosqlite
import random

from discord.ext import commands
from discord import app_commands

import config

DATABASE = config.DATABASE_PATH


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # XP Event
    # ==========================

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if message.guild is None:
            return

        xp = random.randint(10, 20)

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT xp, level
                FROM users
                WHERE user_id=?
                """,
                (message.author.id,)
            )

            data = await cursor.fetchone()

            if data is None:

                await db.execute(
                    """
                    INSERT INTO users
                    (user_id, xp, level)
                    VALUES (?, ?, ?)
                    """,
                    (
                        message.author.id,
                        xp,
                        1
                    )
                )

                await db.commit()

                return

            current_xp, level = data

            current_xp += xp

            required = level * 250

            if current_xp >= required:

                level += 1

                current_xp = 0

                embed = discord.Embed(

                    title="🎉 Level Up!",

                    description=(
                        f"{message.author.mention} reached **Level {level}**!"
                    ),

                    color=0x8A2BE2

                )

                await message.channel.send(embed=embed)

            await db.execute(
                """
                UPDATE users
                SET xp=?, level=?
                WHERE user_id=?
                """,
                (
                    current_xp,
                    level,
                    message.author.id
                )
            )

            await db.commit()

    # ==========================
    # Rank Command
    # ==========================

    @app_commands.command(
        name="rank",
        description="View your level."
    )
    async def rank(

        self,

        interaction: discord.Interaction,

        member: discord.Member=None

    ):

        if member is None:

            member = interaction.user

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT xp, level
                FROM users
                WHERE user_id=?
                """,
                (member.id,)
            )

            data = await cursor.fetchone()

        if data is None:

            await interaction.response.send_message(

                "No level data found."

            )

            return

        xp, level = data

        embed = discord.Embed(

            title=f"🏆 {member.name}'s Rank",

            color=0x8A2BE2

        )

        embed.add_field(
            name="Level",
            value=level
        )

        embed.add_field(
            name="XP",
            value=xp
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
          )
      from discord.ext import tasks
import time

# ==========================
# XP Cooldown
# ==========================

XP_COOLDOWN = 60  # Seconds

LEVEL_ROLE_REWARDS = {
    5: "🌟 Beginner",
    10: "⭐ Member",
    20: "💎 Elite",
    30: "🔥 Pro",
    50: "👑 Legend",
    75: "🌌 Galaxy",
    100: "🚀 Cosmic"
}


class Levels(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.xp_cooldowns = {}

    # ==========================
    # Give Level Role
    # ==========================

    async def give_level_role(
        self,
        member,
        level
    ):

        if level not in LEVEL_ROLE_REWARDS:
            return

        role = discord.utils.get(
            member.guild.roles,
            name=LEVEL_ROLE_REWARDS[level]
        )

        if role is None:
            return

        try:
            await member.add_roles(
                role,
                reason="Galaxy AI Level Reward"
            )
        except:
            pass

    # ==========================
    # Level Up Notification
    # ==========================

    async def send_level_notification(
        self,
        member,
        level
    ):

        channel = discord.utils.get(
            member.guild.text_channels,
            name="level-up"
        )

        if channel is None:
            return

        embed = discord.Embed(
            title="🎉 Level Up!",
            color=0x8A2BE2
        )

        embed.add_field(
            name="👤 Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="⭐ New Level",
            value=str(level),
            inline=True
        )

        if level in LEVEL_ROLE_REWARDS:

            embed.add_field(
                name="🎁 Reward",
                value=LEVEL_ROLE_REWARDS[level],
                inline=False
            )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await channel.send(embed=embed)

    # ==========================
    # XP Cooldown Check
    # ==========================

    def can_gain_xp(
        self,
        user_id
    ):

        now = time.time()

        if user_id not in self.xp_cooldowns:

            self.xp_cooldowns[user_id] = now

            return True

        if now - self.xp_cooldowns[user_id] >= XP_COOLDOWN:

            self.xp_cooldowns[user_id] = now

            return True

        return False

    # ==========================
    # Set Level Channel
    # ==========================

    @app_commands.command(
        name="setlevelchannel",
        description="Set the level-up notification channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setlevelchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        # TODO:
        # Save channel.id to SQLite.

        embed = discord.Embed(
            title="✅ Level Channel Updated",
            description=f"Level-up messages will now be sent in {channel.mention}.",
            color=0x57F287
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Voice XP Placeholder
    # ==========================

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member,
        before,
        after
    ):

        # TODO:
        # Award voice XP every minute while in voice.
        pass
      # ==========================
# Leaderboard
# ==========================

@app_commands.command(
    name="leaderboard",
    description="View the server XP leaderboard."
)
async def leaderboard(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT user_id, level, xp
            FROM users
            ORDER BY level DESC, xp DESC
            LIMIT 10
            """
        )

        users = await cursor.fetchall()

    embed = discord.Embed(
        title="🏆 Galaxy AI Leaderboard",
        color=0x8A2BE2
    )

    rank = 1

    for user_id, level, xp in users:

        member = interaction.guild.get_member(user_id)

        if member:

            embed.add_field(
                name=f"#{rank} • {member.display_name}",
                value=f"⭐ Level **{level}**\n✨ XP **{xp}**",
                inline=False
            )

            rank += 1

    await interaction.response.send_message(embed=embed)


# ==========================
# Daily Bonus
# ==========================

@app_commands.command(
    name="dailyxp",
    description="Claim your daily XP reward."
)
async def dailyxp(
    self,
    interaction: discord.Interaction
):

    bonus = 250

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE users
            SET xp = xp + ?
            WHERE user_id = ?
            """,
            (
                bonus,
                interaction.user.id
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="🎁 Daily XP",
        description=f"You received **{bonus} XP!**",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Weekly Bonus
# ==========================

@app_commands.command(
    name="weeklyxp",
    description="Claim your weekly XP reward."
)
async def weeklyxp(
    self,
    interaction: discord.Interaction
):

    bonus = 1500

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE users
            SET xp = xp + ?
            WHERE user_id = ?
            """,
            (
                bonus,
                interaction.user.id
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="🎉 Weekly XP",
        description=f"You received **{bonus} XP!**",
        color=0x8A2BE2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Level Role List
# ==========================

@app_commands.command(
    name="levelroles",
    description="View all level rewards."
)
async def levelroles(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🏅 Level Rewards",
        color=0x8A2BE2
    )

    for level, role in LEVEL_ROLE_REWARDS.items():

        embed.add_field(
            name=f"Level {level}",
            value=role,
            inline=True
        )

    await interaction.response.send_message(embed=embed)
# ==========================
# Level Role Add
# ==========================

@app_commands.command(
    name="levelrole_add",
    description="Add a level reward role."
)
@app_commands.default_permissions(administrator=True)
async def levelrole_add(
    self,
    interaction: discord.Interaction,
    level: app_commands.Range[int, 1, 1000],
    role: discord.Role
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT OR REPLACE INTO level_roles
            (level, role_id)
            VALUES (?, ?)
            """,
            (
                level,
                role.id
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="✅ Level Role Added",
        color=0x57F287
    )

    embed.add_field(
        name="Level",
        value=str(level)
    )

    embed.add_field(
        name="Role",
        value=role.mention
    )

    await interaction.response.send_message(
        embed=embed
    )

# ==========================
# Level Role Remove
# ==========================

@app_commands.command(
    name="levelrole_remove",
    description="Remove a level reward."
)
@app_commands.default_permissions(administrator=True)
async def levelrole_remove(
    self,
    interaction: discord.Interaction,
    level: int
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            DELETE FROM level_roles
            WHERE level=?
            """,
            (level,)
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ Removed reward for **Level {level}**."
    )

# ==========================
# Level Role List
# ==========================

@app_commands.command(
    name="levelrole_list",
    description="Show all configured level roles."
)
async def levelrole_list(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT level, role_id
            FROM level_roles
            ORDER BY level ASC
            """
        )

        rewards = await cursor.fetchall()

    embed = discord.Embed(
        title="🏆 Level Rewards",
        color=0x8A2BE2
    )

    if not rewards:

        embed.description = "No level rewards configured."

    else:

        for level, role_id in rewards:

            role = interaction.guild.get_role(role_id)

            if role:

                embed.add_field(
                    name=f"Level {level}",
                    value=role.mention,
                    inline=False
                )

    await interaction.response.send_message(embed=embed)

# ==========================
# Voice XP Task
# ==========================

@tasks.loop(minutes=1)
async def voice_xp_task(self):

    for guild in self.bot.guilds:

        for voice_channel in guild.voice_channels:

            for member in voice_channel.members:

                if member.bot:
                    continue

                async with aiosqlite.connect(DATABASE) as db:

                    await db.execute(
                        """
                        UPDATE users
                        SET xp = xp + 15
                        WHERE user_id = ?
                        """,
                        (member.id,)
                    )

                    await db.commit()

# ==========================
# Ready Event
# ==========================

@commands.Cog.listener()
async def on_ready(self):

    if not self.voice_xp_task.is_running():
        self.voice_xp_task.start()

    print("✅ Level System Loaded")
# ==========================
# Add XP (Admin)
# ==========================

@app_commands.command(
    name="addxp",
    description="Add XP to a member."
)
@app_commands.default_permissions(administrator=True)
async def addxp(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: app_commands.Range[int, 1, 100000]
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE users
            SET xp = xp + ?
            WHERE user_id = ?
            """,
            (amount, member.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="✅ XP Added",
        description=f"Added **{amount} XP** to {member.mention}.",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Remove XP (Admin)
# ==========================

@app_commands.command(
    name="removexp",
    description="Remove XP from a member."
)
@app_commands.default_permissions(administrator=True)
async def removexp(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: app_commands.Range[int, 1, 100000]
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE users
            SET xp = MAX(xp - ?, 0)
            WHERE user_id = ?
            """,
            (amount, member.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="➖ XP Removed",
        description=f"Removed **{amount} XP** from {member.mention}.",
        color=0xED4245
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Set Level (Admin)
# ==========================

@app_commands.command(
    name="setlevel",
    description="Set a member's level."
)
@app_commands.default_permissions(administrator=True)
async def setlevel(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    level: app_commands.Range[int, 1, 1000]
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE users
            SET level = ?, xp = 0
            WHERE user_id = ?
            """,
            (level, member.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="🏆 Level Updated",
        description=f"{member.mention} is now **Level {level}**.",
        color=0x8A2BE2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Reset Level (Admin)
# ==========================

@app_commands.command(
    name="resetlevel",
    description="Reset a member's level."
)
@app_commands.default_permissions(administrator=True)
async def resetlevel(
    self,
    interaction: discord.Interaction,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE users
            SET level = 1, xp = 0
            WHERE user_id = ?
            """,
            (member.id,)
        )

        await db.commit()

    await interaction.response.send_message(
        f"🔄 {member.mention}'s level has been reset."
    )


# ==========================
# Global Leaderboard
# ==========================

@app_commands.command(
    name="globalleaderboard",
    description="View the global XP leaderboard."
)
async def globalleaderboard(
    self,
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "🌍 Global leaderboard is coming soon!"
    )


# ==========================
# Setup
# ==========================

async def setup(bot):

    await bot.add_cog(Levels(bot))
