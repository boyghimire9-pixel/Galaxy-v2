import discord
from discord.ext import commands
import aiosqlite
import config

DATABASE = config.DATABASE_PATH


class MemberEvents(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Member Join
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
                    channel_id,
                    message,
                    auto_role
                FROM welcome_settings
                WHERE guild_id=?
                """,
                (member.guild.id,)
            )

            data = await cursor.fetchone()

        if data:

            channel_id, message, auto_role = data

            channel = member.guild.get_channel(channel_id)

            if channel:

                text = (
                    message
                    .replace("{user}", member.mention)
                    .replace("{server}", member.guild.name)
                    .replace("{membercount}", str(member.guild.member_count))
                )

                embed = discord.Embed(
                    title="👋 Welcome!",
                    description=text,
                    color=0x57F287
                )

                embed.set_thumbnail(
                    url=member.display_avatar.url
                )

                await channel.send(embed=embed)

            if auto_role:

                role = member.guild.get_role(auto_role)

                if role:

                    try:
                        await member.add_roles(
                            role,
                            reason="Automatic welcome role"
                        )
                    except discord.Forbidden:
                        pass

    # ==========================
    # Member Leave
    # ==========================

    @commands.Cog.listener()
    async def on_member_remove(
        self,
        member: discord.Member
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT channel_id
                FROM welcome_settings
                WHERE guild_id=?
                """,
                (member.guild.id,)
            )

            data = await cursor.fetchone()

        if not data:
            return

        channel = member.guild.get_channel(data[0])

        if channel:

            embed = discord.Embed(
                title="👋 Goodbye!",
                description=(
                    f"**{member}** has left the server.\n\n"
                    f"We now have **{member.guild.member_count}** members."
                ),
                color=0xED4245
            )

            embed.set_thumbnail(
                url=member.display_avatar.url
            )

            await channel.send(embed=embed)


async def setup(bot):
    await bot.add_cog(MemberEvents(bot))
  # ==========================
# Member Update
# ==========================

@commands.Cog.listener()
async def on_member_update(
    self,
    before: discord.Member,
    after: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT log_channel_id
            FROM logging_settings
            WHERE guild_id=?
            """,
            (after.guild.id,)
        )

        data = await cursor.fetchone()

    if not data:
        return

    log_channel = after.guild.get_channel(data[0])

    if log_channel is None:
        return

    # ==========================
    # Nickname Changed
    # ==========================

    if before.nick != after.nick:

        embed = discord.Embed(
            title="✏️ Nickname Updated",
            color=0xFEE75C,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Member",
            value=after.mention,
            inline=False
        )

        embed.add_field(
            name="Old Nickname",
            value=before.nick or "None",
            inline=True
        )

        embed.add_field(
            name="New Nickname",
            value=after.nick or "None",
            inline=True
        )

        await log_channel.send(embed=embed)

    # ==========================
    # Roles Changed
    # ==========================

    if before.roles != after.roles:

        added_roles = [
            role.mention
            for role in after.roles
            if role not in before.roles
        ]

        removed_roles = [
            role.mention
            for role in before.roles
            if role not in after.roles
        ]

        embed = discord.Embed(
            title="🎭 Member Roles Updated",
            color=0x5865F2,
            timestamp=discord.utils.utcnow()
        )

        embed.add_field(
            name="Member",
            value=after.mention,
            inline=False
        )

        embed.add_field(
            name="➕ Added Roles",
            value="\n".join(added_roles) if added_roles else "None",
            inline=False
        )

        embed.add_field(
            name="➖ Removed Roles",
            value="\n".join(removed_roles) if removed_roles else "None",
            inline=False
        )

        await log_channel.send(embed=embed)

    # ==========================
    # Server Boost
    # ==========================

    if before.premium_since != after.premium_since:

        if after.premium_since:

            embed = discord.Embed(
                title="🚀 Server Boost!",
                description=(
                    f"{after.mention} has boosted the server!\n"
                    "Thank you for your support! 💜"
                ),
                color=0xFF73FA,
                timestamp=discord.utils.utcnow()
            )

            await log_channel.send(embed=embed)

        else:

            embed = discord.Embed(
                title="💔 Boost Removed",
                description=(
                    f"{after.mention} is no longer boosting the server."
                ),
                color=0xED4245,
                timestamp=discord.utils.utcnow()
            )

            await log_channel.send(embed=embed)
          # ==========================
# MESSAGE DELETE LOG
# ==========================

@commands.Cog.listener()
async def on_message_delete(self, message: discord.Message):

    if message.author.bot:
        return

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT channel_id
            FROM log_settings
            WHERE guild_id=?
            """,
            (message.guild.id,)
        )
        data = await cursor.fetchone()

    if not data:
        return

    channel = message.guild.get_channel(data[0])

    if channel:

        embed = discord.Embed(
            title="🗑️ Message Deleted",
            color=0xED4245
        )

        embed.add_field(name="User", value=f"{message.author} ({message.author.id})", inline=False)
        embed.add_field(name="Channel", value=message.channel.mention, inline=False)
        embed.add_field(
            name="Content",
            value=message.content[:1024] if message.content else "No text / embed-only message",
            inline=False
        )

        if message.attachments:
            embed.add_field(
                name="Attachments",
                value="\n".join([a.url for a in message.attachments]),
                inline=False
            )

        await channel.send(embed=embed)


# ==========================
# MESSAGE EDIT LOG
# ==========================

@commands.Cog.listener()
async def on_message_edit(self, before: discord.Message, after: discord.Message):

    if before.author.bot:
        return

    if before.content == after.content:
        return

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT channel_id
            FROM log_settings
            WHERE guild_id=?
            """,
            (before.guild.id,)
        )
        data = await cursor.fetchone()

    if not data:
        return

    channel = before.guild.get_channel(data[0])

    if channel:

        embed = discord.Embed(
            title="✏️ Message Edited",
            color=0xFEE75C
        )

        embed.add_field(name="User", value=f"{before.author} ({before.author.id})", inline=False)
        embed.add_field(name="Channel", value=before.channel.mention, inline=False)

        embed.add_field(
            name="Before",
            value=before.content[:1024] if before.content else "None",
            inline=False
        )

        embed.add_field(
            name="After",
            value=after.content[:1024] if after.content else "None",
            inline=False
        )

        await channel.send(embed=embed)
        # ==========================
# ROLE UPDATE LOG
# ==========================

@commands.Cog.listener()
async def on_member_update(self, before: discord.Member, after: discord.Member):

    if before.bot:
        return

    if before.roles == after.roles:
        return

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT channel_id
            FROM log_settings
            WHERE guild_id=?
            """,
            (before.guild.id,)
        )
        data = await cursor.fetchone()

    if not data:
        return

    channel = before.guild.get_channel(data[0])

    if channel:

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = after_roles - before_roles
        removed = before_roles - after_roles

        embed = discord.Embed(
            title="🎭 Role Update",
            color=0x5865F2
        )

        embed.add_field(
            name="User",
            value=f"{before} ({before.id})",
            inline=False
        )

        if added:
            embed.add_field(
                name="➕ Added Roles",
                value=", ".join(r.mention for r in added if r.name != "@everyone"),
                inline=False
            )

        if removed:
            embed.add_field(
                name="➖ Removed Roles",
                value=", ".join(r.mention for r in removed if r.name != "@everyone"),
                inline=False
            )

        await channel.send(embed=embed)


# ==========================
# BOOST TRACKING
# ==========================

@commands.Cog.listener()
async def on_member_update(self, before: discord.Member, after: discord.Member):

    if before.guild.premium_subscriber_role in after.roles and before.guild.premium_subscriber_role not in before.roles:

        async with aiosqlite.connect(DATABASE) as db:
            cursor = await db.execute(
                """
                SELECT channel_id
                FROM log_settings
                WHERE guild_id=?
                """,
                (after.guild.id,)
            )
            data = await cursor.fetchone()

        if not data:
            return

        channel = after.guild.get_channel(data[0])

        if channel:

            embed = discord.Embed(
                title="🚀 Server Boost!",
                description=f"Thanks {after.mention} for boosting the server!",
                color=0xF47FFF
            )

            embed.set_thumbnail(url=after.display_avatar.url)

            await channel.send(embed=embed)


# ==========================
# MEMBER STATUS UPDATE (optional simple log)
# ==========================

@commands.Cog.listener()
async def on_presence_update(self, before: discord.Member, after: discord.Member):

    if before.bot:
        return

    if before.status != after.status:

        async with aiosqlite.connect(DATABASE) as db:
            cursor = await db.execute(
                """
                SELECT channel_id
                FROM log_settings
                WHERE guild_id=?
                """,
                (after.guild.id,)
            )
            data = await cursor.fetchone()

        if not data:
            return

        channel = after.guild.get_channel(data[0])

        if channel:

            await channel.send(
                f"🟡 **{after}** status changed: `{before.status}` ➜ `{after.status}`"
                )
        @commands.Cog.listener()
async def on_member_update(self, before: discord.Member, after: discord.Member):

    if before.bot:
        return

    async with aiosqlite.connect(DATABASE) as db:
        cursor = await db.execute(
            """
            SELECT channel_id
            FROM log_settings
            WHERE guild_id=?
            """,
            (after.guild.id,)
        )
        data = await cursor.fetchone()

    if not data:
        return

    channel = after.guild.get_channel(data[0])
    if not channel:
        return

    # ==========================
    # ROLE CHANGE LOG
    # ==========================
    if before.roles != after.roles:

        before_roles = set(before.roles)
        after_roles = set(after.roles)

        added = after_roles - before_roles
        removed = before_roles - after_roles

        embed = discord.Embed(
            title="🎭 Role Update",
            color=0x5865F2
        )

        embed.add_field(name="User", value=f"{after} ({after.id})", inline=False)

        if added:
            embed.add_field(
                name="➕ Added Roles",
                value=", ".join(r.mention for r in added if r.name != "@everyone"),
                inline=False
            )

        if removed:
            embed.add_field(
                name="➖ Removed Roles",
                value=", ".join(r.mention for r in removed if r.name != "@everyone"),
                inline=False
            )

        await channel.send(embed=embed)

    # ==========================
    # BOOST CHECK
    # ==========================
    if before.guild.premium_subscriber_role:

        if (before.guild.premium_subscriber_role not in before.roles and
            before.guild.premium_subscriber_role in after.roles):

            embed = discord.Embed(
                title="🚀 Server Boost!",
                description=f"Thanks {after.mention} for boosting the server!",
                color=0xF47FFF
            )

            embed.set_thumbnail(url=after.display_avatar.url)

            await channel.send(embed=embed)

    # ==========================
    # STATUS CHANGE LOG
    # ==========================
    if before.status != after.status:

        await channel.send(
            f"🟡 **{after}** status changed: `{before.status}` ➜ `{after.status}`"
            )
