import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select, Button

import config

DATABASE = config.DATABASE_PATH

# ==========================
# Ticket Categories
# ==========================

TICKET_TYPES = [
    "Support",
    "Premium",
    "Purchase",
    "Bug Report",
    "Partnership",
    "Staff Application"
]

# ==========================
# Ticket Dropdown
# ==========================

class TicketDropdown(discord.ui.Select):

    def __init__(self):

        options = [
            discord.SelectOption(
                label="Support",
                emoji="🎫",
                description="General support."
            ),
            discord.SelectOption(
                label="Premium",
                emoji="💎",
                description="Premium help."
            ),
            discord.SelectOption(
                label="Purchase",
                emoji="🛒",
                description="Purchase support."
            ),
            discord.SelectOption(
                label="Bug Report",
                emoji="🐞",
                description="Report a bug."
            ),
            discord.SelectOption(
                label="Partnership",
                emoji="🤝",
                description="Partner with us."
            ),
            discord.SelectOption(
                label="Staff Application",
                emoji="👮",
                description="Apply for staff."
            )
        ]

        super().__init__(
            placeholder="Select a ticket type...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        ticket_type = self.values[0]

        guild = interaction.guild

        category = discord.utils.get(
            guild.categories,
            name="Tickets"
        )

        overwrites = {

            guild.default_role:
                discord.PermissionOverwrite(
                    view_channel=False
                ),

            interaction.user:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True,
                    attach_files=True
                ),

            guild.me:
                discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )
        }

        channel = await guild.create_text_channel(
            name=f"{ticket_type.lower()}-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title=f"{ticket_type} Ticket",
            description=(
                "A staff member will assist you shortly."
            ),
            color=0x8A2BE2
        )

        await channel.send(
            interaction.user.mention,
            embed=embed
        )

        await interaction.response.send_message(
            f"✅ Ticket created: {channel.mention}",
            ephemeral=True
        )

# ==========================
# Ticket View
# ==========================

class TicketView(View):

    def __init__(self):

        super().__init__(
            timeout=None
        )

        self.add_item(
            TicketDropdown()
      )
      # ==========================
# Close Ticket Button
# ==========================

class CloseButton(Button):

    def __init__(self):

        super().__init__(
            label="Close",
            emoji="🔒",
            style=discord.ButtonStyle.red
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "🔒 Closing ticket in 5 seconds..."
        )

        await asyncio.sleep(5)

        await interaction.channel.delete()

# ==========================
# Claim Ticket Button
# ==========================

class ClaimButton(Button):

    def __init__(self):

        super().__init__(
            label="Claim",
            emoji="👤",
            style=discord.ButtonStyle.green
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="👤 Ticket Claimed",
            description=f"{interaction.user.mention} has claimed this ticket.",
            color=0x57F287
        )

        await interaction.response.send_message(embed=embed)

# ==========================
# Rename Ticket Button
# ==========================

class RenameButton(Button):

    def __init__(self):

        super().__init__(
            label="Rename",
            emoji="✏️",
            style=discord.ButtonStyle.blurple
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "Use `/rename_ticket <new_name>` to rename this ticket.",
            ephemeral=True
        )

# ==========================
# Delete Ticket Button
# ==========================

class DeleteButton(Button):

    def __init__(self):

        super().__init__(
            label="Delete",
            emoji="🗑️",
            style=discord.ButtonStyle.danger
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "🗑️ Deleting ticket in 3 seconds..."
        )

        await asyncio.sleep(3)

        await interaction.channel.delete()

# ==========================
# Ticket Control View
# ==========================

class TicketControls(View):

    def __init__(self):

        super().__init__(timeout=None)

        self.add_item(ClaimButton())
        self.add_item(RenameButton())
        self.add_item(CloseButton())
        self.add_item(DeleteButton())

# ==========================
# Ticket Panel Command
# ==========================

class Tickets(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(
        name="ticketpanel",
        description="Send the ticket panel."
    )
    @app_commands.default_permissions(administrator=True)
    async def ticketpanel(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="🎫 Galaxy AI Ticket System",
            description=(
                "Select a ticket type below to create a ticket."
            ),
            color=0x8A2BE2
        )

        embed.set_footer(
            text="Galaxy AI V2"
        )

        await interaction.response.send_message(
            embed=embed,
            view=TicketView()
        )
      # ==========================
# Transcript Generator
# ==========================

async def create_transcript(channel):

    messages = []

    async for message in channel.history(limit=None, oldest_first=True):

        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")

        messages.append(
            f"[{timestamp}] {message.author}: {message.content}"
        )

    transcript = "\n".join(messages)

    filename = f"transcript-{channel.id}.txt"

    with open(filename, "w", encoding="utf-8") as file:
        file.write(transcript)

    return filename


# ==========================
# Save Ticket
# ==========================

async def save_ticket(
    guild_id,
    channel_id,
    creator_id,
    ticket_type
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            INSERT INTO tickets
            (
                guild_id,
                channel_id,
                creator_id,
                ticket_type,
                status
            )
            VALUES
            (?, ?, ?, ?, ?)
            """,
            (
                guild_id,
                channel_id,
                creator_id,
                ticket_type,
                "Open"
            )
        )

        await db.commit()


# ==========================
# Close Ticket
# ==========================

async def close_ticket(channel):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE tickets
            SET status = 'Closed'
            WHERE channel_id = ?
            """,
            (
                channel.id,
            )
        )

        await db.commit()


# ==========================
# Ticket Logs
# ==========================

async def send_ticket_log(
    guild,
    title,
    description
):

    log_channel = discord.utils.get(
        guild.text_channels,
        name="ticket-logs"
    )

    if log_channel is None:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=0x8A2BE2
    )

    embed.timestamp = discord.utils.utcnow()

    await log_channel.send(
        embed=embed
    )


# ==========================
# Ticket Counter
# ==========================

async def get_ticket_number():

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT COUNT(*) FROM tickets"
        )

        total = await cursor.fetchone()

        return total[0] + 1
      # ==========================
# Rename Ticket Command
# ==========================

    @app_commands.command(
        name="rename_ticket",
        description="Rename the current ticket."
    )
    @app_commands.default_permissions(manage_channels=True)
    async def rename_ticket(
        self,
        interaction: discord.Interaction,
        new_name: str
    ):

        await interaction.channel.edit(
            name=new_name
        )

        await interaction.response.send_message(
            f"✅ Ticket renamed to **{new_name}**."
        )

# ==========================
# Transcript Command
# ==========================

    @app_commands.command(
        name="transcript",
        description="Generate a ticket transcript."
    )
    async def transcript(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer()

        file = await create_transcript(
            interaction.channel
        )

        await interaction.followup.send(
            "📄 Ticket Transcript",
            file=discord.File(file)
        )

# ==========================
# Ticket Statistics
# ==========================

    @app_commands.command(
        name="ticketstats",
        description="View ticket statistics."
    )
    @app_commands.default_permissions(administrator=True)
    async def ticketstats(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                "SELECT COUNT(*) FROM tickets"
            )

            total = (await cursor.fetchone())[0]

            cursor = await db.execute(
                "SELECT COUNT(*) FROM tickets WHERE status='Open'"
            )

            open_tickets = (await cursor.fetchone())[0]

            cursor = await db.execute(
                "SELECT COUNT(*) FROM tickets WHERE status='Closed'"
            )

            closed = (await cursor.fetchone())[0]

        embed = discord.Embed(
            title="🎫 Ticket Statistics",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Total",
            value=str(total)
        )

        embed.add_field(
            name="Open",
            value=str(open_tickets)
        )

        embed.add_field(
            name="Closed",
            value=str(closed)
        )

        await interaction.response.send_message(
            embed=embed
        )

# ==========================
# Ticket Permission Check
# ==========================

    async def interaction_check(
        self,
        interaction: discord.Interaction
    ):

        if interaction.guild is None:

            await interaction.response.send_message(
                "❌ This command can only be used in a server.",
                ephemeral=True
            )

            return False

        return True

# ==========================
# Ticket Number Generator
# ==========================

    async def next_ticket_name(
        self,
        ticket_type
    ):

        number = await get_ticket_number()

        return f"{ticket_type.lower()}-{number:04d}"
      # ==========================
# Find/Create Tickets Category
# ==========================

async def get_ticket_category(guild):

    category = discord.utils.get(
        guild.categories,
        name="📂 Tickets"
    )

    if category is None:

        category = await guild.create_category(
            "📂 Tickets"
        )

    return category


# ==========================
# Check Existing Ticket
# ==========================

async def user_has_ticket(user_id):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT channel_id
            FROM tickets
            WHERE creator_id=?
            AND status='Open'
            """,
            (user_id,)
        )

        return await cursor.fetchone()


# ==========================
# Create Professional Ticket
# ==========================

async def create_ticket(
    interaction: discord.Interaction,
    ticket_type: str
):

    existing = await user_has_ticket(
        interaction.user.id
    )

    if existing:

        await interaction.response.send_message(
            "❌ You already have an open ticket.",
            ephemeral=True
        )

        return

    guild = interaction.guild

    category = await get_ticket_category(
        guild
    )

    ticket_number = await get_ticket_number()

    overwrites = {

        guild.default_role:
            discord.PermissionOverwrite(
                view_channel=False
            ),

        interaction.user:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                embed_links=True
            ),

        guild.me:
            discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                manage_channels=True
            )
    }

    channel = await guild.create_text_channel(

        name=f"ticket-{ticket_number:04d}",

        category=category,

        overwrites=overwrites

    )

    await save_ticket(

        guild.id,

        channel.id,

        interaction.user.id,

        ticket_type

    )

    embed = discord.Embed(

        title="🌌 Galaxy AI Ticket",

        color=0x8A2BE2

    )

    embed.add_field(

        name="🎫 Ticket ID",

        value=f"#{ticket_number:04d}",

        inline=True

    )

    embed.add_field(

        name="📂 Type",

        value=ticket_type,

        inline=True

    )

    embed.add_field(

        name="👤 Owner",

        value=interaction.user.mention,

        inline=False

    )

    embed.add_field(

        name="⭐ Priority",

        value="🟡 Medium",

        inline=True

    )

    embed.add_field(

        name="📌 Status",

        value="🟢 Open",

        inline=True

    )

    embed.set_footer(
        text="Galaxy AI V2"
    )

    await channel.send(

        content=interaction.user.mention,

        embed=embed,

        view=TicketControls()

    )

    await send_ticket_log(

        guild,

        "🎫 Ticket Created",

        f"{interaction.user.mention} created **ticket-{ticket_number:04d}**"

    )

    await interaction.response.send_message(

        f"✅ Your ticket has been created: {channel.mention}",

        ephemeral=True

    )


# ==========================
# Staff Claim
# ==========================

claimed_by = {}


async def claim_ticket(

    interaction: discord.Interaction

):

    claimed_by[interaction.channel.id] = interaction.user.id

    embed = discord.Embed(

        title="👮 Ticket Claimed",

        description=f"{interaction.user.mention} is now handling this ticket.",

        color=0x57F287

    )

    await interaction.channel.send(
        embed=embed
      )
  import os
import io
from datetime import datetime

# ==========================
# HTML Transcript Generator
# ==========================

async def create_html_transcript(channel):

    messages = []

    async for message in channel.history(limit=None, oldest_first=True):

        timestamp = message.created_at.strftime("%Y-%m-%d %H:%M:%S")

        content = message.content.replace("<", "&lt;").replace(">", "&gt;")

        messages.append(f"""
        <div class="message">
            <b>{message.author}</b>
            <small>{timestamp}</small>
            <p>{content}</p>
        </div>
        """)

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Galaxy AI Ticket Transcript</title>

        <style>

        body{{
            background:#111827;
            color:white;
            font-family:Arial;
            padding:20px;
        }}

        .message{{
            background:#1f2937;
            margin:10px;
            padding:12px;
            border-radius:10px;
        }}

        </style>

    </head>

    <body>

    <h1>Galaxy AI V2 Ticket Transcript</h1>

    {''.join(messages)}

    </body>
    </html>
    """

    file = io.BytesIO(html.encode())

    file.name = f"ticket-{channel.id}.html"

    return discord.File(file)


# ==========================
# Reopen Ticket
# ==========================

@app_commands.command(
    name="reopen_ticket",
    description="Reopen a closed ticket."
)
@app_commands.default_permissions(manage_channels=True)
async def reopen_ticket(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE tickets
            SET status='Open'
            WHERE channel_id=?
            """,
            (interaction.channel.id,)
        )

        await db.commit()

    embed = discord.Embed(
        title="🔓 Ticket Reopened",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Close Ticket
# ==========================

@app_commands.command(
    name="close_ticket",
    description="Close the current ticket."
)
async def close_ticket_cmd(
    self,
    interaction: discord.Interaction
):

    await close_ticket(interaction.channel)

    transcript = await create_html_transcript(
        interaction.channel
    )

    await interaction.channel.send(
        "📄 Ticket transcript generated.",
        file=transcript
    )

    await send_ticket_log(

        interaction.guild,

        "🔒 Ticket Closed",

        f"{interaction.channel.mention} closed by {interaction.user.mention}"

    )

    embed = discord.Embed(

        title="🔒 Ticket Closed",

        description="This ticket will be deleted in 10 seconds.",

        color=0xED4245

    )

    await interaction.response.send_message(
        embed=embed
    )

    await asyncio.sleep(10)

    await interaction.channel.delete()


# ==========================
# Ticket Analytics
# ==========================

@app_commands.command(
    name="ticket_analytics",
    description="Show ticket analytics."
)
@app_commands.default_permissions(administrator=True)
async def analytics(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        total = await (
            await db.execute(
                "SELECT COUNT(*) FROM tickets"
            )
        ).fetchone()

        open_count = await (
            await db.execute(
                "SELECT COUNT(*) FROM tickets WHERE status='Open'"
            )
        ).fetchone()

        closed = await (
            await db.execute(
                "SELECT COUNT(*) FROM tickets WHERE status='Closed'"
            )
        ).fetchone()

    embed = discord.Embed(

        title="📊 Ticket Analytics",

        color=0x8A2BE2

    )

    embed.add_field(
        name="🎫 Total Tickets",
        value=str(total[0])
    )

    embed.add_field(
        name="🟢 Open",
        value=str(open_count[0])
    )

    embed.add_field(
        name="🔴 Closed",
        value=str(closed[0])
    )

    await interaction.response.send_message(
        embed=embed
    )


# ==========================
# Ready Event
# ==========================

@commands.Cog.listener()
async def on_ready(self):

    print("✅ Ticket System Loaded")


# ==========================
# Setup
# ==========================

async def setup(bot):

    await bot.add_cog(
        Tickets(bot)
  )
