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
          
