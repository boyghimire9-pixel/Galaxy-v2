import discord
import aiosqlite
import config

DATABASE = config.DATABASE_PATH


class JoinGiveawayButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Join Giveaway",
            emoji="🎉",
            style=discord.ButtonStyle.green,
            custom_id="join_giveaway"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS giveaway_entries (
                    message_id INTEGER,
                    user_id INTEGER,
                    PRIMARY KEY(message_id, user_id)
                )
                """
            )

            await db.execute(
                """
                INSERT OR IGNORE INTO giveaway_entries
                (message_id, user_id)
                VALUES (?, ?)
                """,
                (
                    interaction.message.id,
                    interaction.user.id
                )
            )

            await db.commit()

            cursor = await db.execute(
                """
                SELECT COUNT(*)
                FROM giveaway_entries
                WHERE message_id=?
                """,
                (interaction.message.id,)
            )

            total = (await cursor.fetchone())[0]

        embed = discord.Embed(
            title="🎉 Giveaway Joined",
            description=(
                f"You've successfully entered this giveaway!\n\n"
                f"**Entries:** {total}"
            ),
            color=0x57F287
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


class GiveawayView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(
            JoinGiveawayButton()
      )
      import random

# ==========================
# Leave Giveaway Button
# ==========================

class LeaveGiveawayButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Leave Giveaway",
            emoji="❌",
            style=discord.ButtonStyle.red,
            custom_id="leave_giveaway"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                DELETE FROM giveaway_entries
                WHERE message_id=? AND user_id=?
                """,
                (
                    interaction.message.id,
                    interaction.user.id
                )
            )

            await db.commit()

            cursor = await db.execute(
                """
                SELECT COUNT(*)
                FROM giveaway_entries
                WHERE message_id=?
                """,
                (interaction.message.id,)
            )

            total = (await cursor.fetchone())[0]

        embed = discord.Embed(
            title="❌ Giveaway Left",
            description=(
                "You have left this giveaway.\n\n"
                f"**Current Entries:** {total}"
            ),
            color=0xED4245
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ==========================
# Participants Button
# ==========================

class ParticipantsButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Participants",
            emoji="👥",
            style=discord.ButtonStyle.blurple,
            custom_id="participants"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT user_id
                FROM giveaway_entries
                WHERE message_id=?
                """,
                (interaction.message.id,)
            )

            rows = await cursor.fetchall()

        if not rows:

            return await interaction.response.send_message(
                "No one has joined this giveaway yet.",
                ephemeral=True
            )

        members = []

        for row in rows[:25]:

            members.append(f"<@{row[0]}>")

        embed = discord.Embed(
            title="👥 Giveaway Participants",
            description="\n".join(members),
            color=0x5865F2
        )

        embed.set_footer(
            text=f"Total Participants: {len(rows)}"
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
        )


# ==========================
# Pick Winner Helper
# ==========================

async def pick_winner(message_id):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT user_id
            FROM giveaway_entries
            WHERE message_id=?
            """,
            (message_id,)
        )

        users = await cursor.fetchall()

    if not users:
        return None

    winner = random.choice(users)

    return winner[0]
class GiveawayView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(JoinGiveawayButton())
        self.add_item(LeaveGiveawayButton())
        self.add_item(ParticipantsButton())
      # ==========================
# End Giveaway Button
# ==========================

class EndGiveawayButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="End Giveaway",
            emoji="🏁",
            style=discord.ButtonStyle.red,
            custom_id="end_giveaway"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.manage_guild:

            return await interaction.response.send_message(
                "❌ You need the **Manage Server** permission.",
                ephemeral=True
            )

        winner = await pick_winner(interaction.message.id)

        if winner is None:

            embed = discord.Embed(
                title="❌ Giveaway Ended",
                description="No valid participants joined this giveaway.",
                color=0xED4245
            )

        else:

            embed = discord.Embed(
                title="🏆 Giveaway Ended",
                description=f"Congratulations <@{winner}>!\n\nYou won the giveaway! 🎉",
                color=0xFEE75C
            )

        await interaction.message.reply(embed=embed)

        self.disabled = True

        await interaction.message.edit(view=self.view)

        await interaction.response.send_message(
            "✅ Giveaway ended.",
            ephemeral=True
        )


# ==========================
# Reroll Winner Button
# ==========================

class RerollWinnerButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Reroll",
            emoji="🎲",
            style=discord.ButtonStyle.blurple,
            custom_id="reroll_giveaway"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        if not interaction.user.guild_permissions.manage_guild:

            return await interaction.response.send_message(
                "❌ You need the **Manage Server** permission.",
                ephemeral=True
            )

        winner = await pick_winner(interaction.message.id)

        if winner is None:

            return await interaction.response.send_message(
                "❌ No participants found.",
                ephemeral=True
            )

        embed = discord.Embed(
            title="🎲 New Winner",
            description=f"Congratulations <@{winner}>!",
            color=0x57F287
        )

        await interaction.channel.send(embed=embed)

        await interaction.response.send_message(
            "✅ Giveaway rerolled.",
            ephemeral=True
        )


# ==========================
# Giveaway Stats Button
# ==========================

class GiveawayStatsButton(discord.ui.Button):

    def __init__(self):

        super().__init__(
            label="Statistics",
            emoji="📊",
            style=discord.ButtonStyle.secondary,
            custom_id="giveaway_stats"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT COUNT(*)
                FROM giveaway_entries
                WHERE message_id=?
                """,
                (interaction.message.id,)
            )

            total = (await cursor.fetchone())[0]

        embed = discord.Embed(
            title="📊 Giveaway Statistics",
            color=0x5865F2
        )

        embed.add_field(
            name="Participants",
            value=str(total),
            inline=False
        )

        await interaction.response.send_message(
            embed=embed,
            ephemeral=True
)
      class GiveawayView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(JoinGiveawayButton())
        self.add_item(LeaveGiveawayButton())
        self.add_item(ParticipantsButton())
        self.add_item(EndGiveawayButton())
        self.add_item(RerollWinnerButton())
        self.add_item(GiveawayStatsButton())
      import datetime

# ==========================
# Pick Multiple Winners
# ==========================

async def pick_multiple_winners(
    message_id: int,
    winner_count: int
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT user_id
            FROM giveaway_entries
            WHERE message_id=?
            """,
            (message_id,)
        )

        rows = await cursor.fetchall()

    if len(rows) == 0:
        return []

    users = [row[0] for row in rows]

    if winner_count >= len(users):
        return users

    return random.sample(users, winner_count)


# ==========================
# End Giveaway Automatically
# ==========================

async def end_giveaway(
    bot,
    channel_id: int,
    message_id: int,
    winner_count: int = 1
):

    channel = bot.get_channel(channel_id)

    if channel is None:
        return

    try:
        message = await channel.fetch_message(message_id)
    except discord.NotFound:
        return

    winners = await pick_multiple_winners(
        message_id,
        winner_count
    )

    if not winners:

        embed = discord.Embed(
            title="❌ Giveaway Ended",
            description="No valid participants entered.",
            color=0xED4245,
            timestamp=discord.utils.utcnow()
        )

        await channel.send(embed=embed)
        return

    winner_mentions = ", ".join(
        f"<@{user_id}>"
        for user_id in winners
    )

    embed = discord.Embed(
        title="🎉 Giveaway Ended",
        description=(
            f"🏆 **Winner(s):** {winner_mentions}\n\n"
            "Congratulations!"
        ),
        color=0xFEE75C,
        timestamp=discord.utils.utcnow()
    )

    embed.set_footer(
        text=f"{len(winners)} winner(s)"
    )

    await channel.send(embed=embed)

    try:
        await message.edit(view=None)
    except Exception:
        pass


# ==========================
# Giveaway Time Remaining
# ==========================

def format_remaining(seconds: int):

    if seconds <= 0:
        return "Ended"

    delta = datetime.timedelta(seconds=seconds)

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    return f"{days}d {hours}h {minutes}m"
