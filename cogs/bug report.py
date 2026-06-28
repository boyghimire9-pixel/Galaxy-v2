import uuid
import aiosqlite
import discord

from discord.ext import commands
from discord import app_commands

import config

DATABASE = config.DATABASE_PATH


# ==========================
# Bug Report Modal
# ==========================

class BugReportModal(discord.ui.Modal, title="🐞 Galaxy AI V2 Bug Report"):

    bug_title = discord.ui.TextInput(
        label="Bug Title",
        placeholder="Short title of the bug...",
        max_length=100
    )

    description = discord.ui.TextInput(
        label="Description",
        style=discord.TextStyle.paragraph,
        placeholder="Describe the bug in detail...",
        max_length=2000
    )

    steps = discord.ui.TextInput(
        label="Steps to Reproduce",
        style=discord.TextStyle.paragraph,
        required=False,
        max_length=1500
    )

    screenshot = discord.ui.TextInput(
        label="Screenshot URL (Optional)",
        placeholder="https://...",
        required=False
    )

    async def on_submit(
        self,
        interaction: discord.Interaction
    ):

        bug_id = str(uuid.uuid4())[:8].upper()

        embed = discord.Embed(
            title=f"🐞 Bug Report • {bug_id}",
            color=0xED4245,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="👤 Reporter",
            value=interaction.user.mention,
            inline=False
        )

        embed.add_field(
            name="📌 Title",
            value=str(self.bug_title),
            inline=False
        )

        embed.add_field(
            name="📝 Description",
            value=str(self.description),
            inline=False
        )

        embed.add_field(
            name="🔁 Steps",
            value=str(self.steps) if self.steps else "Not provided",
            inline=False
        )

        embed.add_field(
            name="⚠️ Priority",
            value="🟡 Medium",
            inline=True
        )

        embed.add_field(
            name="📊 Status",
            value="🟢 Open",
            inline=True
        )

        if self.screenshot:

            embed.add_field(
                name="📷 Screenshot",
                value=str(self.screenshot),
                inline=False
            )

        bug_channel = discord.utils.get(
            interaction.guild.text_channels,
            name="bug-reports"
        )

        if bug_channel:

            message = await bug_channel.send(embed=embed)

            async with aiosqlite.connect(DATABASE) as db:

                await db.execute(
                    """
                    INSERT INTO bug_reports
                    (
                        bug_id,
                        reporter_id,
                        message_id,
                        guild_id,
                        title,
                        description,
                        status,
                        priority
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        bug_id,
                        interaction.user.id,
                        message.id,
                        interaction.guild.id,
                        str(self.bug_title),
                        str(self.description),
                        "Open",
                        "Medium"
                    )
                )

                await db.commit()

        success = discord.Embed(
            title="✅ Bug Submitted",
            description=(
                f"Your bug report has been submitted.\n\n"
                f"**Bug ID:** `{bug_id}`"
            ),
            color=0x57F287
        )

        await interaction.response.send_message(
            embed=success,
            ephemeral=True
        )


class BugReport(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Report Bug
    # ==========================

    @app_commands.command(
        name="bugreport",
        description="Report a bug to the developers."
    )
    async def bugreport(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_modal(
            BugReportModal()
      )
      # ==========================
# Bug Information
# ==========================

@app_commands.command(
    name="buginfo",
    description="View information about a bug report."
)
@app_commands.default_permissions(manage_messages=True)
async def buginfo(
    self,
    interaction: discord.Interaction,
    bug_id: str
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                reporter_id,
                title,
                description,
                status,
                priority
            FROM bug_reports
            WHERE bug_id=?
            """,
            (bug_id.upper(),)
        )

        bug = await cursor.fetchone()

    if bug is None:

        return await interaction.response.send_message(
            "❌ Bug report not found.",
            ephemeral=True
        )

    reporter_id, title, description, status, priority = bug

    embed = discord.Embed(
        title=f"🐞 Bug Report • {bug_id.upper()}",
        color=0x8A2BE2,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="👤 Reporter",
        value=f"<@{reporter_id}>",
        inline=False
    )

    embed.add_field(
        name="📌 Title",
        value=title,
        inline=False
    )

    embed.add_field(
        name="📝 Description",
        value=description,
        inline=False
    )

    embed.add_field(
        name="📊 Status",
        value=status,
        inline=True
    )

    embed.add_field(
        name="⚠️ Priority",
        value=priority,
        inline=True
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Update Bug Status
# ==========================

@app_commands.command(
    name="bugstatus",
    description="Update the status of a bug report."
)
@app_commands.default_permissions(manage_messages=True)
@app_commands.choices(
    status=[
        app_commands.Choice(name="🟢 Open", value="Open"),
        app_commands.Choice(name="🟡 In Progress", value="In Progress"),
        app_commands.Choice(name="✅ Fixed", value="Fixed"),
        app_commands.Choice(name="🔴 Closed", value="Closed"),
    ]
)
async def bugstatus(
    self,
    interaction: discord.Interaction,
    bug_id: str,
    status: app_commands.Choice[str]
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE bug_reports
            SET status=?
            WHERE bug_id=?
            """,
            (
                status.value,
                bug_id.upper()
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="✅ Bug Status Updated",
        description=(
            f"**Bug ID:** `{bug_id.upper()}`\n"
            f"**New Status:** {status.value}"
        ),
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Change Priority
# ==========================

@app_commands.command(
    name="bugpriority",
    description="Change the priority of a bug."
)
@app_commands.default_permissions(manage_messages=True)
@app_commands.choices(
    priority=[
        app_commands.Choice(name="🟢 Low", value="Low"),
        app_commands.Choice(name="🟡 Medium", value="Medium"),
        app_commands.Choice(name="🟠 High", value="High"),
        app_commands.Choice(name="🔴 Critical", value="Critical"),
    ]
)
async def bugpriority(
    self,
    interaction: discord.Interaction,
    bug_id: str,
    priority: app_commands.Choice[str]
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE bug_reports
            SET priority=?
            WHERE bug_id=?
            """,
            (
                priority.value,
                bug_id.upper()
            )
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ Priority updated to **{priority.value}**.",
        ephemeral=True
  )
  # ==========================
# Developer Notes
# ==========================

@app_commands.command(
    name="bugnote",
    description="Add developer notes to a bug report."
)
@app_commands.default_permissions(manage_messages=True)
async def bugnote(
    self,
    interaction: discord.Interaction,
    bug_id: str,
    note: str
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE bug_reports
            SET developer_notes=?
            WHERE bug_id=?
            """,
            (
                note,
                bug_id.upper()
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="📝 Developer Notes Updated",
        description=(
            f"**Bug ID:** `{bug_id.upper()}`\n\n"
            f"{note}"
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ==========================
# Assign Developer
# ==========================

@app_commands.command(
    name="assignbug",
    description="Assign a bug to a developer."
)
@app_commands.default_permissions(manage_messages=True)
async def assignbug(
    self,
    interaction: discord.Interaction,
    bug_id: str,
    developer: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE bug_reports
            SET assigned_to=?
            WHERE bug_id=?
            """,
            (
                developer.id,
                bug_id.upper()
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="👨‍💻 Developer Assigned",
        description=(
            f"**Bug ID:** `{bug_id.upper()}`\n"
            f"**Assigned To:** {developer.mention}"
        ),
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Bug List
# ==========================

@app_commands.command(
    name="buglist",
    description="View the latest bug reports."
)
@app_commands.default_permissions(manage_messages=True)
async def buglist(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                bug_id,
                title,
                status,
                priority
            FROM bug_reports
            ORDER BY rowid DESC
            LIMIT 10
            """
        )

        rows = await cursor.fetchall()

    embed = discord.Embed(
        title="🐞 Latest Bug Reports",
        color=0x8A2BE2
    )

    if not rows:

        embed.description = "No bug reports found."

    else:

        for bug_id, title, status, priority in rows:

            embed.add_field(
                name=f"{bug_id} • {title}",
                value=(
                    f"📊 Status: **{status}**\n"
                    f"⚠️ Priority: **{priority}**"
                ),
                inline=False
            )

    await interaction.response.send_message(embed=embed)


# ==========================
# Bug Statistics
# ==========================

@app_commands.command(
    name="bugstats",
    description="View bug report statistics."
)
@app_commands.default_permissions(manage_messages=True)
async def bugstats(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        total = await (
            await db.execute(
                "SELECT COUNT(*) FROM bug_reports"
            )
        ).fetchone()

        open_count = await (
            await db.execute(
                """
                SELECT COUNT(*)
                FROM bug_reports
                WHERE status='Open'
                """
            )
        ).fetchone()

        fixed = await (
            await db.execute(
                """
                SELECT COUNT(*)
                FROM bug_reports
                WHERE status='Fixed'
                """
            )
        ).fetchone()

    embed = discord.Embed(
        title="📊 Bug Report Statistics",
        color=0x8A2BE2
    )

    embed.add_field(
        name="🐞 Total",
        value=str(total[0]),
        inline=True
    )

    embed.add_field(
        name="🟢 Open",
        value=str(open_count[0]),
        inline=True
    )

    embed.add_field(
        name="✅ Fixed",
        value=str(fixed[0]),
        inline=True
    )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Search Bug
# ==========================

@app_commands.command(
    name="bugsearch",
    description="Search bug reports by title."
)
@app_commands.default_permissions(manage_messages=True)
async def bugsearch(
    self,
    interaction: discord.Interaction,
    keyword: str
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                bug_id,
                title,
                status,
                priority
            FROM bug_reports
            WHERE title LIKE ?
            LIMIT 10
            """,
            (f"%{keyword}%",)
        )

        results = await cursor.fetchall()

    embed = discord.Embed(
        title="🔍 Bug Search Results",
        color=0x8A2BE2
    )

    if not results:
        embed.description = "No matching bug reports found."

    else:
        for bug_id, title, status, priority in results:

            embed.add_field(
                name=f"{bug_id} • {title}",
                value=(
                    f"📊 Status: **{status}**\n"
                    f"⚠️ Priority: **{priority}**"
                ),
                inline=False
            )

    await interaction.response.send_message(embed=embed)


# ==========================
# Delete Bug
# ==========================

@app_commands.command(
    name="deletebug",
    description="Delete a bug report."
)
@app_commands.default_permissions(administrator=True)
async def deletebug(
    self,
    interaction: discord.Interaction,
    bug_id: str
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT message_id FROM bug_reports WHERE bug_id=?",
            (bug_id.upper(),)
        )

        row = await cursor.fetchone()

        if row:

            await db.execute(
                "DELETE FROM bug_reports WHERE bug_id=?",
                (bug_id.upper(),)
            )

            await db.commit()

    embed = discord.Embed(
        title="🗑️ Bug Deleted",
        description=f"Bug **{bug_id.upper()}** has been removed.",
        color=0xED4245
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Bugs By Status
# ==========================

@app_commands.command(
    name="bugsbystatus",
    description="List bugs by status."
)
@app_commands.default_permissions(manage_messages=True)
@app_commands.choices(
    status=[
        app_commands.Choice(name="🟢 Open", value="Open"),
        app_commands.Choice(name="🟡 In Progress", value="In Progress"),
        app_commands.Choice(name="✅ Fixed", value="Fixed"),
        app_commands.Choice(name="🔴 Closed", value="Closed"),
    ]
)
async def bugsbystatus(
    self,
    interaction: discord.Interaction,
    status: app_commands.Choice[str]
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT bug_id,title,priority
            FROM bug_reports
            WHERE status=?
            LIMIT 15
            """,
            (status.value,)
        )

        bugs = await cursor.fetchall()

    embed = discord.Embed(
        title=f"📂 {status.value} Bugs",
        color=0x5865F2
    )

    if not bugs:

        embed.description = "No bug reports found."

    else:

        for bug_id, title, priority in bugs:

            embed.add_field(
                name=f"{bug_id} • {title}",
                value=f"⚠️ {priority}",
                inline=False
            )

    await interaction.response.send_message(embed=embed)


# ==========================
# Bug Log Helper
# ==========================

async def bug_log(
    self,
    guild: discord.Guild,
    embed: discord.Embed
):

    channel = discord.utils.get(
        guild.text_channels,
        name="bug-logs"
    )

    if channel:

        try:
            await channel.send(embed=embed)
        except Exception:
            pass
        # ==========================
# Notify Reporter
# ==========================

@app_commands.command(
    name="notifybug",
    description="Notify the reporter about a bug update."
)
@app_commands.default_permissions(manage_messages=True)
async def notifybug(
    self,
    interaction: discord.Interaction,
    bug_id: str,
    message: str
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT reporter_id
            FROM bug_reports
            WHERE bug_id=?
            """,
            (bug_id.upper(),)
        )

        result = await cursor.fetchone()

    if result is None:

        return await interaction.response.send_message(
            "❌ Bug report not found.",
            ephemeral=True
        )

    reporter = self.bot.get_user(result[0])

    if reporter is None:

        try:
            reporter = await self.bot.fetch_user(result[0])
        except Exception:
            reporter = None

    if reporter:

        embed = discord.Embed(
            title=f"🐞 Update for Bug {bug_id.upper()}",
            description=message,
            color=0x5865F2,
            timestamp=discord.utils.utcnow()
        )

        try:
            await reporter.send(embed=embed)
        except discord.Forbidden:
            pass

    await interaction.response.send_message(
        "✅ Reporter notified.",
        ephemeral=True
    )


# ==========================
# Bug History
# ==========================

@app_commands.command(
    name="bughistory",
    description="View all bugs reported by a user."
)
@app_commands.default_permissions(manage_messages=True)
async def bughistory(
    self,
    interaction: discord.Interaction,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT bug_id,title,status
            FROM bug_reports
            WHERE reporter_id=?
            ORDER BY rowid DESC
            LIMIT 10
            """,
            (member.id,)
        )

        bugs = await cursor.fetchall()

    embed = discord.Embed(
        title=f"📜 Bug History • {member}",
        color=0x8A2BE2
    )

    if not bugs:

        embed.description = "No bug reports found."

    else:

        for bug_id, title, status in bugs:

            embed.add_field(
                name=f"{bug_id} • {title}",
                value=f"📊 {status}",
                inline=False
            )

    await interaction.response.send_message(embed=embed)


# ==========================
# Bug Configuration
# ==========================

@app_commands.command(
    name="bugconfig",
    description="Set the bug reports channel."
)
@app_commands.default_permissions(administrator=True)
async def bugconfig(
    self,
    interaction: discord.Interaction,
    channel: discord.TextChannel
):

    # Replace this with database storage if preferred.
    self.bug_channel_id = channel.id

    await interaction.response.send_message(
        f"✅ Bug report channel set to {channel.mention}.",
        ephemeral=True
    )


# ==========================
# Setup
# ==========================

async def setup(bot):
    await bot.add_cog(BugReport(bot))  
