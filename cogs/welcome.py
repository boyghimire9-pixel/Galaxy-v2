import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands

import config

DATABASE = config.DATABASE_PATH


class Welcome(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Set Welcome Channel
    # ==========================

    @app_commands.command(
        name="setwelcomechannel",
        description="Set the welcome channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setwelcomechannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                INSERT OR REPLACE INTO welcome_settings
                (guild_id, welcome_channel)
                VALUES (?, ?)
                """,
                (
                    interaction.guild.id,
                    channel.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="✅ Welcome Channel Updated",
            description=f"Welcome messages will be sent in {channel.mention}.",
            color=0x57F287
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Set Goodbye Channel
    # ==========================

    @app_commands.command(
        name="setgoodbyechannel",
        description="Set the goodbye channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setgoodbyechannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE welcome_settings
                SET goodbye_channel=?
                WHERE guild_id=?
                """,
                (
                    channel.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="👋 Goodbye Channel Updated",
            description=f"Goodbye messages will be sent in {channel.mention}.",
            color=0x3498DB
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Set Auto Role
    # ==========================

    @app_commands.command(
        name="setautorole",
        description="Set the auto role."
    )
    @app_commands.default_permissions(administrator=True)
    async def setautorole(
        self,
        interaction: discord.Interaction,
        role: discord.Role
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE welcome_settings
                SET autorole=?
                WHERE guild_id=?
                """,
                (
                    role.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="🎉 Auto Role Updated",
            description=f"New members will receive {role.mention}.",
            color=0x8A2BE2
        )

        await interaction.response.send_message(embed=embed)
      # ==========================
# Member Join Event
# ==========================

@commands.Cog.listener()
async def on_member_join(
    self,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
            welcome_channel,
            autorole
            FROM welcome_settings
            WHERE guild_id=?
            """,
            (member.guild.id,)
        )

        data = await cursor.fetchone()

    if not data:
        return

    welcome_channel_id, autorole_id = data

    # --------------------------
    # Give Auto Role
    # --------------------------

    if autorole_id:

        role = member.guild.get_role(autorole_id)

        if role:

            try:
                await member.add_roles(
                    role,
                    reason="Galaxy AI Auto Role"
                )
            except discord.Forbidden:
                pass

    # --------------------------
    # Welcome Channel
    # --------------------------

    channel = member.guild.get_channel(
        welcome_channel_id
    )

    if not channel:
        return

    account_age = (
        discord.utils.utcnow() - member.created_at
    ).days

    embed = discord.Embed(
        title="🌌 Welcome to the Galaxy!",
        description=(
            f"Welcome {member.mention}!\n\n"
            f"Enjoy your stay in **{member.guild.name}**."
        ),
        color=0x8A2BE2
    )

    embed.add_field(
        name="👤 Member",
        value=member.mention,
        inline=True
    )

    embed.add_field(
        name="🆔 Member ID",
        value=str(member.id),
        inline=True
    )

    embed.add_field(
        name="📅 Discord Account Age",
        value=f"{account_age} days",
        inline=True
    )

    embed.add_field(
        name="👥 Member Count",
        value=str(member.guild.member_count),
        inline=True
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="Galaxy AI V2 • Welcome System"
    )

    await channel.send(embed=embed)

    # --------------------------
    # Welcome DM
    # --------------------------

    try:

        dm = discord.Embed(
            title="🎉 Welcome!",
            description=(
                f"Welcome to **{member.guild.name}**!\n\n"
                "Please read the rules and have fun!"
            ),
            color=0x57F287
        )

        await member.send(embed=dm)

    except:
        pass


# ==========================
# Member Leave Event
# ==========================

@commands.Cog.listener()
async def on_member_remove(
    self,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT goodbye_channel
            FROM welcome_settings
            WHERE guild_id=?
            """,
            (member.guild.id,)
        )

        data = await cursor.fetchone()

    if not data:
        return

    goodbye_channel = member.guild.get_channel(
        data[0]
    )

    if not goodbye_channel:
        return

    embed = discord.Embed(
        title="😢 Goodbye!",
        description=(
            f"**{member}** has left the server.\n"
            "We hope to see them again someday."
        ),
        color=0xED4245
    )

    embed.add_field(
        name="👥 Members Remaining",
        value=str(member.guild.member_count)
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.set_footer(
        text="Galaxy AI V2"
    )

    await goodbye_channel.send(embed=embed)
  # ==========================
# Set Custom Welcome Message
# ==========================

@app_commands.command(
    name="setwelcomemessage",
    description="Set a custom welcome message."
)
@app_commands.default_permissions(administrator=True)
async def setwelcomemessage(
    self,
    interaction: discord.Interaction,
    message: str
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE welcome_settings
            SET welcome_message=?
            WHERE guild_id=?
            """,
            (
                message,
                interaction.guild.id
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="✅ Welcome Message Updated",
        description="Your custom welcome message has been saved.",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Set Custom Goodbye Message
# ==========================

@app_commands.command(
    name="setgoodbyemessage",
    description="Set a custom goodbye message."
)
@app_commands.default_permissions(administrator=True)
async def setgoodbyemessage(
    self,
    interaction: discord.Interaction,
    message: str
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE welcome_settings
            SET goodbye_message=?
            WHERE guild_id=?
            """,
            (
                message,
                interaction.guild.id
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="👋 Goodbye Message Updated",
        description="Your custom goodbye message has been saved.",
        color=0x3498DB
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Welcome Log
# ==========================

async def send_welcome_log(
    self,
    guild,
    title,
    description
):

    log_channel = discord.utils.get(
        guild.text_channels,
        name="welcome-logs"
    )

    if not log_channel:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=0x8A2BE2
    )

    embed.timestamp = discord.utils.utcnow()

    await log_channel.send(embed=embed)


# ==========================
# Anti-Alt Detection
# ==========================

async def check_alt_account(
    self,
    member
):

    account_age = (
        discord.utils.utcnow() -
        member.created_at
    ).days

    if account_age < 7:

        warning = discord.Embed(
            title="⚠️ Possible Alt Account",
            description=(
                f"{member.mention}'s Discord account "
                f"is only **{account_age} days** old."
            ),
            color=0xFAA61A
        )

        log_channel = discord.utils.get(
            member.guild.text_channels,
            name="welcome-logs"
        )

        if log_channel:
            await log_channel.send(embed=warning)


# ==========================
# Welcome Banner
# ==========================

WELCOME_BANNER = (
    "https://your-domain.com/assets/welcome_banner.png"
)

GOODBYE_BANNER = (
    "https://your-domain.com/assets/goodbye_banner.png"
  )
# ==========================
# Test Welcome Message
# ==========================

@app_commands.command(
    name="testwelcome",
    description="Preview the welcome message."
)
@app_commands.default_permissions(administrator=True)
async def testwelcome(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🌌 Welcome to the Galaxy!",
        description=f"Welcome {interaction.user.mention}!",
        color=0x8A2BE2
    )

    embed.add_field(
        name="👥 Member Count",
        value=str(interaction.guild.member_count),
        inline=True
    )

    embed.set_thumbnail(
        url=interaction.user.display_avatar.url
    )

    if WELCOME_BANNER:
        embed.set_image(url=WELCOME_BANNER)

    await interaction.response.send_message(embed=embed)


# ==========================
# Test Goodbye Message
# ==========================

@app_commands.command(
    name="testgoodbye",
    description="Preview the goodbye message."
)
@app_commands.default_permissions(administrator=True)
async def testgoodbye(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="👋 Goodbye!",
        description=f"{interaction.user.mention} has left the server.",
        color=0xED4245
    )

    embed.set_thumbnail(
        url=interaction.user.display_avatar.url
    )

    if GOODBYE_BANNER:
        embed.set_image(url=GOODBYE_BANNER)

    await interaction.response.send_message(embed=embed)


# ==========================
# Toggle Welcome System
# ==========================

@app_commands.command(
    name="togglewelcome",
    description="Enable or disable the welcome system."
)
@app_commands.default_permissions(administrator=True)
async def togglewelcome(
    self,
    interaction: discord.Interaction,
    enabled: bool
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE welcome_settings
            SET welcome_enabled=?
            WHERE guild_id=?
            """,
            (int(enabled), interaction.guild.id)
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ Welcome system {'enabled' if enabled else 'disabled'}."
    )


# ==========================
# Toggle Welcome DM
# ==========================

@app_commands.command(
    name="togglewelcomedm",
    description="Enable or disable welcome DMs."
)
@app_commands.default_permissions(administrator=True)
async def togglewelcomedm(
    self,
    interaction: discord.Interaction,
    enabled: bool
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE welcome_settings
            SET welcome_dm=?
            WHERE guild_id=?
            """,
            (int(enabled), interaction.guild.id)
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ Welcome DM {'enabled' if enabled else 'disabled'}."
    )


# ==========================
# Placeholders
# ==========================

def format_message(
    self,
    message,
    member
):

    return (
        message
        .replace("{user}", member.mention)
        .replace("{username}", member.name)
        .replace("{server}", member.guild.name)
        .replace("{membercount}", str(member.guild.member_count))
    )


# ==========================
# Setup
# ==========================

async def setup(bot):

    await bot.add_cog(
        Welcome(bot)
    )
