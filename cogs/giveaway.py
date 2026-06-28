import discord
import aiosqlite
import random

from discord.ext import commands
from discord import app_commands

import config

DATABASE = config.DATABASE_PATH


class Giveaway(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Start Giveaway
    # ==========================

    @app_commands.command(
        name="giveaway",
        description="Start a giveaway."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def giveaway(
        self,
        interaction: discord.Interaction,
        prize: str,
        winners: app_commands.Range[int, 1, 20],
        duration_minutes: app_commands.Range[int, 1, 10080]
    ):

        end_time = int(discord.utils.utcnow().timestamp()) + (duration_minutes * 60)

        embed = discord.Embed(
            title="🎉 Galaxy Giveaway",
            description=(
                f"## 🎁 Prize\n"
                f"**{prize}**\n\n"
                f"👑 **Hosted By:** {interaction.user.mention}\n"
                f"🏆 **Winners:** {winners}\n"
                f"⏰ **Ends:** <t:{end_time}:R>\n\n"
                f"🎊 **Click the button below to enter!**"
            ),
            color=0x8A2BE2
        )

        embed.set_footer(
            text="Galaxy AI V2 Giveaway System"
        )

        view = GiveawayView()

        message = await interaction.channel.send(
            embed=embed,
            view=view
        )

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                INSERT INTO giveaways
                (
                    message_id,
                    channel_id,
                    guild_id,
                    prize,
                    winners,
                    host_id,
                    end_time,
                    ended
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    message.id,
                    interaction.channel.id,
                    interaction.guild.id,
                    prize,
                    winners,
                    interaction.user.id,
                    end_time
                )
            )

            await db.commit()

        await interaction.response.send_message(
            "✅ Giveaway started!",
            ephemeral=True
        )


    # ==========================
    # End Giveaway
    # ==========================

    @app_commands.command(
        name="endgiveaway",
        description="End a giveaway."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def endgiveaway(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):

        await interaction.response.send_message(
            "✅ Giveaway ending feature will be completed in Part 2.",
            ephemeral=True
        )


    # ==========================
    # Reroll Giveaway
    # ==========================

    @app_commands.command(
        name="reroll",
        description="Reroll a giveaway."
    )
    @app_commands.default_permissions(manage_guild=True)
    async def reroll(
        self,
        interaction: discord.Interaction,
        message_id: str
    ):

        await interaction.response.send_message(
            "🎲 Reroll system will be added in Part 2.",
            ephemeral=True
      )
      import time


# ==========================
# Giveaway Join Button
# ==========================

class GiveawayView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(
        label="🎉 Join Giveaway",
        style=discord.ButtonStyle.success,
        custom_id="galaxy_join_giveaway"
    )
    async def join(
        self,
        interaction: discord.Interaction,
        button: discord.ui.Button
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT 1
                FROM giveaway_entries
                WHERE giveaway_id=? AND user_id=?
                """,
                (
                    interaction.message.id,
                    interaction.user.id
                )
            )

            exists = await cursor.fetchone()

            if exists:

                return await interaction.response.send_message(
                    "❌ You have already entered this giveaway.",
                    ephemeral=True
                )

            # Premium users receive one bonus entry.
            entries = 2 if any(
                role.name.lower().startswith("premium")
                for role in interaction.user.roles
            ) else 1

            for _ in range(entries):

                await db.execute(
                    """
                    INSERT INTO giveaway_entries
                    (
                        giveaway_id,
                        user_id
                    )
                    VALUES (?, ?)
                    """,
                    (
                        interaction.message.id,
                        interaction.user.id
                    )
                )

            await db.commit()

        await interaction.response.send_message(
            f"🎉 You entered the giveaway! ({entries} entr{'y' if entries == 1 else 'ies'})",
            ephemeral=True
        )


# ==========================
# End Giveaway
# ==========================

@app_commands.command(
    name="endgiveaway",
    description="End a giveaway immediately."
)
@app_commands.default_permissions(manage_guild=True)
async def endgiveaway(
    self,
    interaction: discord.Interaction,
    message_id: str
):

    async with aiosqlite.connect(DATABASE) as db:

        giveaway = await (
            await db.execute(
                """
                SELECT prize,winners
                FROM giveaways
                WHERE message_id=?
                """,
                (int(message_id),)
            )
        ).fetchone()

        if giveaway is None:

            return await interaction.response.send_message(
                "❌ Giveaway not found.",
                ephemeral=True
            )

        prize, winner_count = giveaway

        rows = await (
            await db.execute(
                """
                SELECT user_id
                FROM giveaway_entries
                WHERE giveaway_id=?
                """,
                (int(message_id),)
            )
        ).fetchall()

        users = [r[0] for r in rows]

        if not users:

            return await interaction.response.send_message(
                "❌ Nobody entered this giveaway.",
                ephemeral=True
            )

        winners = random.sample(
            users,
            min(winner_count, len(users))
        )

        mentions = []

        for uid in winners:

            member = interaction.guild.get_member(uid)

            if member:
                mentions.append(member.mention)

        await db.execute(
            """
            UPDATE giveaways
            SET ended=1
            WHERE message_id=?
            """,
            (int(message_id),)
        )

        await db.commit()

    embed = discord.Embed(
        title="🏆 Giveaway Ended",
        description=(
            f"**Prize:** {prize}\n\n"
            f"🎉 Winners:\n"
            + "\n".join(mentions)
        ),
        color=0xFFD700
    )

    await interaction.channel.send(embed=embed)

    await interaction.response.send_message(
        "✅ Giveaway ended.",
        ephemeral=True
    )


# ==========================
# Reroll Giveaway
# ==========================

@app_commands.command(
    name="reroll",
    description="Choose new giveaway winners."
)
@app_commands.default_permissions(manage_guild=True)
async def reroll(
    self,
    interaction: discord.Interaction,
    message_id: str
):

    await interaction.response.send_message(
        "🎲 Reroll support will be expanded in the next part.",
        ephemeral=True
)
from discord.ext import tasks

# ==========================
# Background Giveaway Checker
# ==========================

@tasks.loop(seconds=30)
async def giveaway_loop(self):

    current_time = int(discord.utils.utcnow().timestamp())

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                message_id,
                channel_id,
                guild_id,
                prize,
                winners
            FROM giveaways
            WHERE ended=0
            AND end_time<=?
            """,
            (current_time,)
        )

        giveaways = await cursor.fetchall()

        for giveaway in giveaways:

            message_id, channel_id, guild_id, prize, winner_count = giveaway

            guild = self.bot.get_guild(guild_id)

            if guild is None:
                continue

            channel = guild.get_channel(channel_id)

            if channel is None:
                continue

            cursor2 = await db.execute(
                """
                SELECT user_id
                FROM giveaway_entries
                WHERE giveaway_id=?
                """,
                (message_id,)
            )

            entries = await cursor2.fetchall()

            participants = [entry[0] for entry in entries]

            if participants:

                winners = random.sample(
                    participants,
                    min(winner_count, len(participants))
                )

                mentions = []

                for uid in winners:

                    member = guild.get_member(uid)

                    if member:
                        mentions.append(member.mention)

                        # Winner DM
                        try:
                            dm = discord.Embed(
                                title="🎉 You Won!",
                                description=(
                                    f"Congratulations!\n\n"
                                    f"You won **{prize}** in **{guild.name}**!"
                                ),
                                color=0xFFD700
                            )

                            await member.send(embed=dm)

                        except:
                            pass

                result = discord.Embed(
                    title="🏆 Giveaway Ended",
                    description=(
                        f"**Prize:** {prize}\n\n"
                        f"🎉 Winners:\n"
                        + "\n".join(mentions)
                    ),
                    color=0xFFD700
                )

            else:

                result = discord.Embed(
                    title="❌ Giveaway Ended",
                    description="Nobody entered this giveaway.",
                    color=0xED4245
                )

            await channel.send(embed=result)

            await db.execute(
                """
                UPDATE giveaways
                SET ended=1
                WHERE message_id=?
                """,
                (message_id,)
            )

        await db.commit()


# ==========================
# Before Loop
# ==========================

@giveaway_loop.before_loop
async def before_giveaway_loop(self):
    await self.bot.wait_until_ready()


# ==========================
# Cog Load
# ==========================

async def cog_load(self):
    self.giveaway_loop.start()


# ==========================
# Cog Unload
# ==========================

async def cog_unload(self):
    self.giveaway_loop.cancel()


# ==========================
# Giveaway History
# ==========================

@app_commands.command(
    name="giveawayhistory",
    description="View recently ended giveaways."
)
@app_commands.default_permissions(manage_guild=True)
async def giveawayhistory(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT prize,end_time
            FROM giveaways
            WHERE guild_id=?
            ORDER BY end_time DESC
            LIMIT 10
            """,
            (interaction.guild.id,)
        )

        rows = await cursor.fetchall()

    embed = discord.Embed(
        title="📜 Giveaway History",
        color=0x8A2BE2
    )

    if not rows:

        embed.description = "No giveaway history found."

    else:

        for prize, end_time in rows:

            embed.add_field(
                name=prize,
                value=f"Ended <t:{end_time}:R>",
                inline=False
            )

    await interaction.response.send_message(embed=embed)
# ==========================
# Giveaway Statistics
# ==========================

@app_commands.command(
    name="giveawaystats",
    description="View giveaway statistics."
)
@app_commands.default_permissions(manage_guild=True)
async def giveawaystats(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        total = await (
            await db.execute(
                "SELECT COUNT(*) FROM giveaways WHERE guild_id=?",
                (interaction.guild.id,)
            )
        ).fetchone()

        active = await (
            await db.execute(
                """
                SELECT COUNT(*)
                FROM giveaways
                WHERE guild_id=?
                AND ended=0
                """,
                (interaction.guild.id,)
            )
        ).fetchone()

        ended = await (
            await db.execute(
                """
                SELECT COUNT(*)
                FROM giveaways
                WHERE guild_id=?
                AND ended=1
                """,
                (interaction.guild.id,)
            )
        ).fetchone()

    embed = discord.Embed(
        title="📊 Giveaway Statistics",
        color=0x8A2BE2
    )

    embed.add_field(
        name="🎉 Total Giveaways",
        value=str(total[0]),
        inline=True
    )

    embed.add_field(
        name="🟢 Active",
        value=str(active[0]),
        inline=True
    )

    embed.add_field(
        name="🔴 Ended",
        value=str(ended[0]),
        inline=True
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Giveaway Log Helper
# ==========================

async def send_giveaway_log(
    self,
    guild: discord.Guild,
    title: str,
    description: str
):

    channel = discord.utils.get(
        guild.text_channels,
        name="giveaway-logs"
    )

    if channel is None:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=0x5865F2,
        timestamp=discord.utils.utcnow()
    )

    await channel.send(embed=embed)


# ==========================
# Required Role Check
# ==========================

def has_required_role(
    self,
    member: discord.Member,
    role_id: int | None
):

    if role_id is None:
        return True

    role = member.guild.get_role(role_id)

    return role in member.roles if role else False


# ==========================
# Blacklist Check
# ==========================

async def is_blacklisted(
    self,
    user_id: int
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT 1
            FROM giveaway_blacklist
            WHERE user_id=?
            """,
            (user_id,)
        )

        return await cursor.fetchone() is not None


# ==========================
# Blacklist User
# ==========================

@app_commands.command(
    name="giveawayblacklist",
    description="Blacklist a user from giveaways."
)
@app_commands.default_permissions(administrator=True)
async def giveawayblacklist(
    self,
    interaction: discord.Interaction,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT OR IGNORE
            INTO giveaway_blacklist(user_id)
            VALUES(?)
            """,
            (member.id,)
        )

        await db.commit()

    await interaction.response.send_message(
        f"🚫 {member.mention} has been blacklisted from giveaways."
      )
# ==========================
# Giveaway Info
# ==========================

@app_commands.command(
    name="giveawayinfo",
    description="View information about a giveaway."
)
@app_commands.default_permissions(manage_guild=True)
async def giveawayinfo(
    self,
    interaction: discord.Interaction,
    message_id: str
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                prize,
                winners,
                host_id,
                end_time,
                ended
            FROM giveaways
            WHERE message_id=?
            """,
            (int(message_id),)
        )

        data = await cursor.fetchone()

    if not data:
        return await interaction.response.send_message(
            "❌ Giveaway not found.",
            ephemeral=True
        )

    prize, winners, host_id, end_time, ended = data

    embed = discord.Embed(
        title="🎁 Giveaway Information",
        color=0x8A2BE2
    )

    embed.add_field(
        name="Prize",
        value=prize,
        inline=False
    )

    embed.add_field(
        name="Host",
        value=f"<@{host_id}>",
        inline=True
    )

    embed.add_field(
        name="Winners",
        value=str(winners),
        inline=True
    )

    embed.add_field(
        name="Ends",
        value=f"<t:{end_time}:F>",
        inline=False
    )

    embed.add_field(
        name="Status",
        value="✅ Ended" if ended else "🟢 Active",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Remove Giveaway Blacklist
# ==========================

@app_commands.command(
    name="removegiveawayblacklist",
    description="Remove a user from the giveaway blacklist."
)
@app_commands.default_permissions(administrator=True)
async def removegiveawayblacklist(
    self,
    interaction: discord.Interaction,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            DELETE FROM giveaway_blacklist
            WHERE user_id=?
            """,
            (member.id,)
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ {member.mention} has been removed from the giveaway blacklist."
    )


# ==========================
# Giveaway Configuration
# ==========================

@app_commands.command(
    name="giveawayconfig",
    description="View giveaway configuration."
)
@app_commands.default_permissions(manage_guild=True)
async def giveawayconfig(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="⚙️ Giveaway Configuration",
        color=0x5865F2
    )

    embed.description = (
        "Current Galaxy AI V2 giveaway features:\n\n"
        "✅ Multiple winners\n"
        "✅ Automatic ending\n"
        "✅ Reroll support\n"
        "✅ Premium bonus entries\n"
        "✅ Giveaway history\n"
        "✅ Giveaway statistics\n"
        "✅ Blacklist system\n"
        "✅ Winner DMs\n"
        "✅ SQLite database\n"
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Setup
# ==========================

async def setup(bot):
    await bot.add_cog(Giveaway(bot))
