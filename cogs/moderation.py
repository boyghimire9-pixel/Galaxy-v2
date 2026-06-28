import discord
from discord.ext import commands
from discord import app_commands

class Moderation(commands.Cog):
    """Galaxy AI V2 Moderation Commands"""

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # BAN
    # ==========================

    @app_commands.command(
        name="ban",
        description="Ban a member from the server."
    )
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot ban yourself.",
                ephemeral=True
            )
            return

        await member.ban(reason=reason)

        embed = discord.Embed(
            title="🔨 Member Banned",
            color=0x8A2BE2
        )

        embed.add_field(name="Member", value=member.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

    # ==========================
    # KICK
    # ==========================

    @app_commands.command(
        name="kick",
        description="Kick a member."
    )
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str = "No reason provided."
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot kick yourself.",
                ephemeral=True
            )
            return

        await member.kick(reason=reason)

        embed = discord.Embed(
            title="👢 Member Kicked",
            color=0x8A2BE2
        )

        embed.add_field(name="Member", value=member.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)
      # ==========================
    # TIMEOUT
    # ==========================

    @app_commands.command(
        name="timeout",
        description="Timeout a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def timeout(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        minutes: app_commands.Range[int, 1, 10080],
        reason: str = "No reason provided."
    ):

        if member == interaction.user:
            await interaction.response.send_message(
                "❌ You cannot timeout yourself.",
                ephemeral=True
            )
            return

        duration = discord.utils.utcnow() + discord.timedelta(minutes=minutes)

        await member.edit(
            timed_out_until=duration,
            reason=reason
        )

        embed = discord.Embed(
            title="⏱️ Member Timed Out",
            color=0x8A2BE2
        )

        embed.add_field(name="Member", value=member.mention)
        embed.add_field(name="Duration", value=f"{minutes} minutes")
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

    # ==========================
    # CLEAR
    # ==========================

    @app_commands.command(
        name="clear",
        description="Delete messages."
    )
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(
        self,
        interaction: discord.Interaction,
        amount: app_commands.Range[int, 1, 100]
    ):

        await interaction.response.defer(ephemeral=True)

        deleted = await interaction.channel.purge(limit=amount)

        await interaction.followup.send(
            f"🧹 Deleted **{len(deleted)}** messages.",
            ephemeral=True
        )

    # ==========================
    # WARN
    # ==========================

    @app_commands.command(
        name="warn",
        description="Warn a member."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        reason: str
    ):

        embed = discord.Embed(
            title="⚠️ Member Warned",
            color=0xFEE75C
        )

        embed.add_field(name="Member", value=member.mention)
        embed.add_field(name="Moderator", value=interaction.user.mention)
        embed.add_field(name="Reason", value=reason, inline=False)

        await interaction.response.send_message(embed=embed)

        try:
            await member.send(
                f"You were warned in **{interaction.guild.name}**.\nReason: {reason}"
            )
        except:
            pass
          # ==========================
    # LOCK
    # ==========================

    @app_commands.command(
        name="lock",
        description="Lock the current channel."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(
        self,
        interaction: discord.Interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = False

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "🔒 Channel locked."
        )

    # ==========================
    # UNLOCK
    # ==========================

    @app_commands.command(
        name="unlock",
        description="Unlock the current channel."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(
        self,
        interaction: discord.Interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.guild.default_role
        )

        overwrite.send_messages = None

        await interaction.channel.set_permissions(
            interaction.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "🔓 Channel unlocked."
        )

    # ==========================
    # SLOWMODE
    # ==========================

    @app_commands.command(
        name="slowmode",
        description="Set channel slowmode."
    )
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(
        self,
        interaction: discord.Interaction,
        seconds: app_commands.Range[int, 0, 21600]
    ):

        await interaction.channel.edit(
            slowmode_delay=seconds
        )

        await interaction.response.send_message(
            f"🐌 Slowmode set to **{seconds}** seconds."
        )

    # ==========================
    # NICKNAME
    # ==========================

    @app_commands.command(
        name="nickname",
        description="Change a member's nickname."
    )
    @app_commands.checks.has_permissions(manage_nicknames=True)
    async def nickname(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        nickname: str
    ):

        await member.edit(
            nick=nickname
        )

        await interaction.response.send_message(
            f"✏️ Changed {member.mention}'s nickname to **{nickname}**."
        )

    # ==========================
    # WARNINGS
    # ==========================

    @app_commands.command(
        name="warnings",
        description="View a member's warnings."
    )
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warnings(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        embed = discord.Embed(
            title="⚠️ Warning History",
            description=(
                f"Warning history for {member.mention}\n\n"
                "**Coming soon:** Database integration."
            ),
            color=0xFEE75C
        )

        await interaction.response.send_message(embed=embed)


async def setup(bot: commands.Bot):
    await bot.add_cog(Moderation(bot))
