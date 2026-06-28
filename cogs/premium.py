import discord
import aiosqlite

from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands

import config

DATABASE = config.DATABASE_PATH


class Premium(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Add Premium
    # ==========================

    @app_commands.command(
        name="premium_add",
        description="Give premium to a member."
    )
    @app_commands.default_permissions(administrator=True)
    async def premium_add(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        plan: str
    ):

        plan = plan.lower()

        if plan not in config.PREMIUM_PLANS:

            await interaction.response.send_message(
                "❌ Invalid premium plan.",
                ephemeral=True
            )

            return

        purchase = datetime.utcnow()

        days = config.PREMIUM_PLANS[plan]

        if days is None:
            expiry = "Lifetime"
        else:
            expiry = purchase + timedelta(days=days)

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                INSERT OR REPLACE INTO premium
                (
                    user_id,
                    plan,
                    purchase_date,
                    expiry_date
                )
                VALUES
                (?, ?, ?, ?)
                """,
                (
                    member.id,
                    plan,
                    purchase.isoformat(),
                    expiry if expiry == "Lifetime"
                    else expiry.isoformat()
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="💎 Premium Activated",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Plan",
            value=plan.title(),
            inline=True
        )

        embed.add_field(
            name="Purchase",
            value=f"<t:{int(purchase.timestamp())}:F>",
            inline=False
        )

        if expiry == "Lifetime":

            embed.add_field(
                name="Expires",
                value="Never",
                inline=False
            )

        else:

            embed.add_field(
                name="Expires",
                value=f"<t:{int(expiry.timestamp())}:F>",
                inline=False
            )

        await interaction.response.send_message(
            embed=embed
        )

        try:

            await member.send(
                embed=embed
            )

        except:

            pass
          
          # ==========================
    # Remove Premium
    # ==========================

    @app_commands.command(
        name="premium_remove",
        description="Remove premium from a member."
    )
    @app_commands.default_permissions(administrator=True)
    async def premium_remove(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                "DELETE FROM premium WHERE user_id = ?",
                (member.id,)
            )

            await db.commit()

        embed = discord.Embed(
            title="❌ Premium Removed",
            color=0xED4245
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )

        try:
            await member.send(
                "❌ Your premium membership has been removed."
            )
        except:
            pass

    # ==========================
    # Premium Info
    # ==========================

    @app_commands.command(
        name="premium_info",
        description="View a user's premium information."
    )
    async def premium_info(
        self,
        interaction: discord.Interaction,
        member: discord.Member
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT plan,
                       purchase_date,
                       expiry_date
                FROM premium
                WHERE user_id = ?
                """,
                (member.id,)
            )

            data = await cursor.fetchone()

        if not data:

            await interaction.response.send_message(
                "❌ This member does not have premium.",
                ephemeral=True
            )

            return

        plan, purchase, expiry = data

        embed = discord.Embed(
            title="💎 Premium Information",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Plan",
            value=plan.title(),
            inline=True
        )

        embed.add_field(
            name="Purchased",
            value=purchase,
            inline=False
        )

        embed.add_field(
            name="Expiry",
            value=expiry,
            inline=False
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ==========================
    # Premium Role
    # ==========================

    async def give_premium_role(
        self,
        member,
        role_name="Premium"
    ):

        role = discord.utils.get(
            member.guild.roles,
            name=role_name
        )

        if role:

            try:
                await member.add_roles(
                    role,
                    reason="Premium Activated"
                )
            except:
                pass
              # ==========================
    # Premium Extend
    # ==========================

    @app_commands.command(
        name="premium_extend",
        description="Extend a user's premium subscription."
    )
    @app_commands.default_permissions(administrator=True)
    async def premium_extend(
        self,
        interaction: discord.Interaction,
        member: discord.Member,
        days: app_commands.Range[int, 1, 3650]
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                "SELECT expiry_date FROM premium WHERE user_id = ?",
                (member.id,)
            )

            result = await cursor.fetchone()

            if not result:

                await interaction.response.send_message(
                    "❌ This member does not have premium.",
                    ephemeral=True
                )
                return

            expiry = result[0]

            if expiry == "Lifetime":

                await interaction.response.send_message(
                    "❌ Lifetime premium cannot be extended.",
                    ephemeral=True
                )
                return

            expiry_date = datetime.fromisoformat(expiry)
            new_expiry = expiry_date + timedelta(days=days)

            await db.execute(
                """
                UPDATE premium
                SET expiry_date = ?
                WHERE user_id = ?
                """,
                (
                    new_expiry.isoformat(),
                    member.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="💎 Premium Extended",
            color=0x57F287
        )

        embed.add_field(
            name="Member",
            value=member.mention,
            inline=False
        )

        embed.add_field(
            name="Added",
            value=f"{days} days",
            inline=True
        )

        embed.add_field(
            name="New Expiry",
            value=f"<t:{int(new_expiry.timestamp())}:F>",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

        try:
            await member.send(embed=embed)
        except:
            pass

    # ==========================
    # Premium Expiry Checker
    # ==========================

    async def check_expired_premium(self):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                "SELECT user_id, expiry_date FROM premium"
            )

            users = await cursor.fetchall()

            for user_id, expiry in users:

                if expiry == "Lifetime":
                    continue

                expiry_date = datetime.fromisoformat(expiry)

                if datetime.utcnow() >= expiry_date:

                    await db.execute(
                        "DELETE FROM premium WHERE user_id = ?",
                        (user_id,)
                    )

            await db.commit()

    # ==========================
    # Remove Premium Role
    # ==========================

    async def remove_premium_role(
        self,
        member,
        role_name="Premium"
    ):

        role = discord.utils.get(
            member.guild.roles,
            name=role_name
        )

        if role:

            try:
                await member.remove_roles(
                    role,
                    reason="Premium Expired"
                )
            except:
                pass
              # ==========================
    # Premium List
    # ==========================

    @app_commands.command(
        name="premium_list",
        description="View all premium members."
    )
    @app_commands.default_permissions(administrator=True)
    async def premium_list(
        self,
        interaction: discord.Interaction
    ):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT user_id, plan, expiry_date
                FROM premium
                ORDER BY user_id
                """
            )

            rows = await cursor.fetchall()

        if not rows:

            await interaction.response.send_message(
                "❌ No premium members found.",
                ephemeral=True
            )

            return

        embed = discord.Embed(
            title="💎 Premium Members",
            color=0x8A2BE2
        )

        for user_id, plan, expiry in rows:

            user = self.bot.get_user(user_id)

            name = user.name if user else str(user_id)

            embed.add_field(
                name=name,
                value=(
                    f"**Plan:** {plan.title()}\n"
                    f"**Expiry:** {expiry}"
                ),
                inline=False
            )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Remaining Time
    # ==========================

    def get_remaining_time(self, expiry):

        if expiry == "Lifetime":
            return "Lifetime"

        expiry_date = datetime.fromisoformat(expiry)

        remaining = expiry_date - datetime.utcnow()

        if remaining.total_seconds() <= 0:
            return "Expired"

        days = remaining.days
        hours = remaining.seconds // 3600

        return f"{days} Days, {hours} Hours"

    # ==========================
    # Premium Expiry DM
    # ==========================

    async def send_expiry_dm(self, member):

        embed = discord.Embed(
            title="💎 Premium Expired",
            description=(
                "Your Galaxy AI Premium has expired.\n"
                "Renew it to continue enjoying premium benefits."
            ),
            color=0xED4245
        )

        try:
            await member.send(embed=embed)
        except:
            pass

    # ==========================
    # Premium Log
    # ==========================

    async def premium_log(
        self,
        guild,
        description
    ):

        channel = discord.utils.get(
            guild.text_channels,
            name="premium-logs"
        )

        if channel is None:
            return

        embed = discord.Embed(
            title="💎 Premium Log",
            description=description,
            color=0x8A2BE2
        )

        await channel.send(embed=embed)

    # ==========================
    # Notify Server Owner
    # ==========================

    async def notify_owner(
        self,
        guild,
        member
    ):

        owner = guild.owner

        if owner is None:
            return

        try:

            embed = discord.Embed(
                title="⚠ Premium Expired",
                description=(
                    f"{member.mention}'s premium has expired."
                ),
                color=0xFEE75C
            )

            await owner.send(embed=embed)

        except:
            pass
          from discord.ext import tasks

# ==========================
# Premium Background Task
# ==========================

    @tasks.loop(minutes=5)
    async def premium_checker(self):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT user_id, expiry_date
                FROM premium
                """
            )

            users = await cursor.fetchall()

            for user_id, expiry in users:

                if expiry == "Lifetime":
                    continue

                expiry_date = datetime.fromisoformat(expiry)

                if datetime.utcnow() >= expiry_date:

                    # Remove from database
                    await db.execute(
                        "DELETE FROM premium WHERE user_id=?",
                        (user_id,)
                    )

                    guild = self.bot.guilds[0]

                    member = guild.get_member(user_id)

                    if member:

                        # Remove Premium Role
                        await self.remove_premium_role(member)

                        # DM User
                        await self.send_expiry_dm(member)

                        # Premium Log
                        await self.premium_log(
                            guild,
                            f"{member.mention}'s premium has expired."
                        )

                        # Notify Owner
                        await self.notify_owner(
                            guild,
                            member
                        )

            await db.commit()

# ==========================
# Cog Ready
# ==========================

    @commands.Cog.listener()
    async def on_ready(self):

        if not self.premium_checker.is_running():
            self.premium_checker.start()

        print("✅ Premium System Loaded")

# ==========================
# Cog Unload
# ==========================

    def cog_unload(self):

        self.premium_checker.cancel()

# ==========================
# Setup
# ==========================

async def setup(bot):

    await bot.add_cog(
        Premium(bot)
          )
