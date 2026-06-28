import discord
import aiosqlite

from discord.ext import commands
from discord import app_commands

import config

DATABASE = config.DATABASE_PATH


class Logging(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Set Log Channel
    # ==========================

    @app_commands.command(
        name="setlogchannel",
        description="Set the main logging channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setlogchannel(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                INSERT OR REPLACE INTO logging_settings
                (guild_id, log_channel)
                VALUES (?, ?)
                """,
                (
                    interaction.guild.id,
                    channel.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="✅ Logging Channel Updated",
            description=f"Logs will now be sent to {channel.mention}.",
            color=0x8A2BE2
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Set Moderation Log Channel
    # ==========================

    @app_commands.command(
        name="setmodlog",
        description="Set the moderation log channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setmodlog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE logging_settings
                SET mod_log=?
                WHERE guild_id=?
                """,
                (
                    channel.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        await interaction.response.send_message(
            f"✅ Moderation logs will be sent to {channel.mention}."
        )

    # ==========================
    # Set Message Log Channel
    # ==========================

    @app_commands.command(
        name="setmessagelog",
        description="Set the message log channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setmessagelog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE logging_settings
                SET message_log=?
                WHERE guild_id=?
                """,
                (
                    channel.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        await interaction.response.send_message(
            f"✅ Message logs will be sent to {channel.mention}."
        )

    # ==========================
    # Set Voice Log Channel
    # ==========================

    @app_commands.command(
        name="setvoicelog",
        description="Set the voice log channel."
    )
    @app_commands.default_permissions(administrator=True)
    async def setvoicelog(
        self,
        interaction: discord.Interaction,
        channel: discord.TextChannel
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE logging_settings
                SET voice_log=?
                WHERE guild_id=?
                """,
                (
                    channel.id,
                    interaction.guild.id
                )
            )

            await db.commit()

        await interaction.response.send_message(
            f"✅ Voice logs will be sent to {channel.mention}."
      )
      # ==========================
# Get Log Channel
# ==========================

async def get_log_channel(
    self,
    guild,
    column
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            f"SELECT {column} FROM logging_settings WHERE guild_id=?",
            (guild.id,)
        )

        data = await cursor.fetchone()

    if not data or data[0] is None:
        return None

    return guild.get_channel(data[0])


# ==========================
# Message Delete
# ==========================

@commands.Cog.listener()
async def on_message_delete(
    self,
    message: discord.Message
):

    if message.author.bot:
        return

    channel = await self.get_log_channel(
        message.guild,
        "message_log"
    )

    if channel is None:
        return

    embed = discord.Embed(
        title="🗑️ Message Deleted",
        color=0xED4245,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="👤 Author",
        value=message.author.mention,
        inline=True
    )

    embed.add_field(
        name="📍 Channel",
        value=message.channel.mention,
        inline=True
    )

    embed.add_field(
        name="📝 Content",
        value=message.content[:1024] if message.content else "*No text*",
        inline=False
    )

    if message.attachments:

        files = "\n".join(
            attachment.url
            for attachment in message.attachments
        )

        embed.add_field(
            name="📎 Attachments",
            value=files[:1024],
            inline=False
        )

    embed.set_thumbnail(
        url=message.author.display_avatar.url
    )

    await channel.send(embed=embed)


# ==========================
# Message Edit
# ==========================

@commands.Cog.listener()
async def on_message_edit(
    self,
    before: discord.Message,
    after: discord.Message
):

    if before.author.bot:
        return

    if before.content == after.content:
        return

    channel = await self.get_log_channel(
        before.guild,
        "message_log"
    )

    if channel is None:
        return

    embed = discord.Embed(
        title="✏️ Message Edited",
        color=0xFAA61A,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="👤 Author",
        value=before.author.mention,
        inline=True
    )

    embed.add_field(
        name="📍 Channel",
        value=before.channel.mention,
        inline=True
    )

    embed.add_field(
        name="📄 Before",
        value=before.content[:1024] if before.content else "*Empty*",
        inline=False
    )

    embed.add_field(
        name="🆕 After",
        value=after.content[:1024] if after.content else "*Empty*",
        inline=False
    )

    embed.set_thumbnail(
        url=before.author.display_avatar.url
    )

    await channel.send(embed=embed)
  # ==========================
# Voice State Logs
# ==========================

@commands.Cog.listener()
async def on_voice_state_update(
    self,
    member: discord.Member,
    before: discord.VoiceState,
    after: discord.VoiceState
):

    channel = await self.get_log_channel(
        member.guild,
        "voice_log"
    )

    if channel is None:
        return

    embed = discord.Embed(
        color=0x5865F2,
        timestamp=discord.utils.utcnow()
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    # Joined
    if before.channel is None and after.channel is not None:

        embed.title = "🎤 Voice Channel Joined"

        embed.description = (
            f"{member.mention} joined {after.channel.mention}"
        )

    # Left
    elif before.channel is not None and after.channel is None:

        embed.title = "📤 Voice Channel Left"

        embed.description = (
            f"{member.mention} left {before.channel.mention}"
        )

    # Moved
    elif before.channel != after.channel:

        embed.title = "🔄 Voice Channel Moved"

        embed.description = (
            f"{member.mention}\n\n"
            f"**From:** {before.channel.mention}\n"
            f"**To:** {after.channel.mention}"
        )

    else:
        return

    await channel.send(embed=embed)


# ==========================
# Member Update Logs
# ==========================

@commands.Cog.listener()
async def on_member_update(
    self,
    before: discord.Member,
    after: discord.Member
):

    log_channel = await self.get_log_channel(
        before.guild,
        "log_channel"
    )

    if log_channel is None:
        return

    # --------------------------
    # Nickname Changed
    # --------------------------

    if before.nick != after.nick:

        embed = discord.Embed(
            title="✏️ Nickname Changed",
            color=0xFAA61A,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Member",
            value=after.mention,
            inline=False
        )

        embed.add_field(
            name="Before",
            value=before.nick or before.name,
            inline=True
        )

        embed.add_field(
            name="After",
            value=after.nick or after.name,
            inline=True
        )

        embed.set_thumbnail(
            url=after.display_avatar.url
        )

        await log_channel.send(embed=embed)

    # --------------------------
    # Roles Changed
    # --------------------------

    if before.roles != after.roles:

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = after_roles - before_roles
        removed = before_roles - after_roles

        embed = discord.Embed(
            title="🎭 Roles Updated",
            color=0x8A2BE2,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Member",
            value=after.mention,
            inline=False
        )

        if added:
            embed.add_field(
                name="➕ Added",
                value="\n".join(role.mention for role in added),
                inline=False
            )

        if removed:
            embed.add_field(
                name="➖ Removed",
                value="\n".join(role.mention for role in removed),
                inline=False
            )

        embed.set_thumbnail(
            url=after.display_avatar.url
        )

        await log_channel.send(embed=embed)


# ==========================
# Member Join Log
# ==========================

@commands.Cog.listener()
async def on_member_join(
    self,
    member: discord.Member
):

    channel = await self.get_log_channel(
        member.guild,
        "log_channel"
    )

    if channel is None:
        return

    embed = discord.Embed(
        title="📥 Member Joined",
        color=0x57F287,
        timestamp=discord.utils.utcnow()
    )

    embed.description = (
        f"{member.mention} joined the server."
    )

    embed.add_field(
        name="👥 Member Count",
        value=str(member.guild.member_count)
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await channel.send(embed=embed)


# ==========================
# Member Leave Log
# ==========================

@commands.Cog.listener()
async def on_member_remove(
    self,
    member: discord.Member
):

    channel = await self.get_log_channel(
        member.guild,
        "log_channel"
    )

    if channel is None:
        return

    embed = discord.Embed(
        title="📤 Member Left",
        color=0xED4245,
        timestamp=discord.utils.utcnow()
    )

    embed.description = (
        f"**{member}** left the server."
    )

    embed.add_field(
        name="👥 Members Remaining",
        value=str(member.guild.member_count)
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    await channel.send(embed=embed)
  # ==========================
# Channel Create
# ==========================

@commands.Cog.listener()
async def on_guild_channel_create(
    self,
    channel: discord.abc.GuildChannel
):

    log_channel = await self.get_log_channel(
        channel.guild,
        "log_channel"
    )

    if not log_channel:
        return

    embed = discord.Embed(
        title="📁 Channel Created",
        color=0x57F287,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="Channel",
        value=channel.mention,
        inline=False
    )

    embed.add_field(
        name="Type",
        value=str(channel.type).title(),
        inline=True
    )

    await log_channel.send(embed=embed)


# ==========================
# Channel Delete
# ==========================

@commands.Cog.listener()
async def on_guild_channel_delete(
    self,
    channel: discord.abc.GuildChannel
):

    log_channel = await self.get_log_channel(
        channel.guild,
        "log_channel"
    )

    if not log_channel:
        return

    embed = discord.Embed(
        title="🗑️ Channel Deleted",
        color=0xED4245,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="Channel Name",
        value=channel.name,
        inline=False
    )

    embed.add_field(
        name="Type",
        value=str(channel.type).title(),
        inline=True
    )

    await log_channel.send(embed=embed)


# ==========================
# Channel Update
# ==========================

@commands.Cog.listener()
async def on_guild_channel_update(
    self,
    before: discord.abc.GuildChannel,
    after: discord.abc.GuildChannel
):

    log_channel = await self.get_log_channel(
        before.guild,
        "log_channel"
    )

    if not log_channel:
        return

    if before.name != after.name:

        embed = discord.Embed(
            title="✏️ Channel Renamed",
            color=0xFAA61A,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Before",
            value=before.name,
            inline=True
        )

        embed.add_field(
            name="After",
            value=after.name,
            inline=True
        )

        await log_channel.send(embed=embed)


# ==========================
# Role Create
# ==========================

@commands.Cog.listener()
async def on_guild_role_create(
    self,
    role: discord.Role
):

    log_channel = await self.get_log_channel(
        role.guild,
        "log_channel"
    )

    if not log_channel:
        return

    embed = discord.Embed(
        title="🎭 Role Created",
        color=0x57F287,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="Role",
        value=role.mention,
        inline=False
    )

    await log_channel.send(embed=embed)


# ==========================
# Role Delete
# ==========================

@commands.Cog.listener()
async def on_guild_role_delete(
    self,
    role: discord.Role
):

    log_channel = await self.get_log_channel(
        role.guild,
        "log_channel"
    )

    if not log_channel:
        return

    embed = discord.Embed(
        title="🗑️ Role Deleted",
        color=0xED4245,
        timestamp=discord.utils.utcnow()
    )

    embed.add_field(
        name="Role Name",
        value=role.name,
        inline=False
    )

    await log_channel.send(embed=embed)


# ==========================
# Emoji Create
# ==========================

@commands.Cog.listener()
async def on_guild_emojis_update(
    self,
    guild: discord.Guild,
    before,
    after
):

    log_channel = await self.get_log_channel(
        guild,
        "log_channel"
    )

    if not log_channel:
        return

    if len(after) > len(before):

        embed = discord.Embed(
            title="😀 Emoji Added",
            color=0x57F287,
            timestamp=discord.utils.utcnow()
        )

        await log_channel.send(embed=embed)

    elif len(before) > len(after):

        embed = discord.Embed(
            title="❌ Emoji Removed",
            color=0xED4245,
            timestamp=discord.utils.utcnow()
        )

        await log_channel.send(embed=embed)


# ==========================
# Sticker Update
# ==========================

@commands.Cog.listener()
async def on_guild_stickers_update(
    self,
    guild,
    before,
    after
):

    log_channel = await self.get_log_channel(
        guild,
        "log_channel"
    )

    if not log_channel:
        return

    embed = discord.Embed(
        title="🎨 Stickers Updated",
        description="The server stickers have changed.",
        color=0x8A2BE2,
        timestamp=discord.utils.utcnow()
    )

    await log_channel.send(embed=embed)
  # ==========================
# Log Helper
# ==========================

async def send_log(
    self,
    guild: discord.Guild,
    title: str,
    description: str,
    color: int = 0x5865F2
):

    channel = await self.get_log_channel(
        guild,
        "log_channel"
    )

    if channel is None:
        return

    embed = discord.Embed(
        title=title,
        description=description,
        color=color,
        timestamp=discord.utils.utcnow()
    )

    embed.set_footer(
        text="Galaxy AI V2 Logging System"
    )

    await channel.send(embed=embed)


# ==========================
# Manual Moderation Log
# ==========================

@app_commands.command(
    name="logmod",
    description="Create a moderation log entry."
)
@app_commands.default_permissions(administrator=True)
async def logmod(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    action: str,
    reason: str = "No reason provided."
):

    await self.send_log(
        interaction.guild,
        "🛡️ Moderation Action",
        (
            f"**Member:** {member.mention}\n"
            f"**Action:** {action}\n"
            f"**Moderator:** {interaction.user.mention}\n"
            f"**Reason:** {reason}"
        ),
        0xED4245
    )

    await interaction.response.send_message(
        "✅ Moderation action logged.",
        ephemeral=True
    )


# ==========================
# Toggle Logging
# ==========================

@app_commands.command(
    name="togglelogs",
    description="Enable or disable all logging."
)
@app_commands.default_permissions(administrator=True)
async def togglelogs(
    self,
    interaction: discord.Interaction,
    enabled: bool
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE logging_settings
            SET enabled=?
            WHERE guild_id=?
            """,
            (
                int(enabled),
                interaction.guild.id
            )
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ Logging has been {'enabled' if enabled else 'disabled'}."
    )


# ==========================
# Log Statistics
# ==========================

@app_commands.command(
    name="logstats",
    description="View current logging configuration."
)
@app_commands.default_permissions(administrator=True)
async def logstats(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
            log_channel,
            mod_log,
            message_log,
            voice_log
            FROM logging_settings
            WHERE guild_id=?
            """,
            (interaction.guild.id,)
        )

        data = await cursor.fetchone()

    embed = discord.Embed(
        title="📊 Logging Configuration",
        color=0x8A2BE2
    )

    labels = [
        ("📜 Main Log", data[0]),
        ("🛡️ Moderation", data[1]),
        ("💬 Message", data[2]),
        ("🎤 Voice", data[3]),
    ]

    for name, channel_id in labels:

        if channel_id:
            channel = interaction.guild.get_channel(channel_id)
            value = channel.mention if channel else "Deleted Channel"
        else:
            value = "Not Configured"

        embed.add_field(
            name=name,
            value=value,
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Setup
# ==========================

async def setup(bot):
    await bot.add_cog(Logging(bot))
