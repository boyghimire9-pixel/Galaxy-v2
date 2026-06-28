import io
import os
import shutil
import platform
import psutil
import asyncio
import discord
from discord.ext import commands
from discord import app_commands

import config


class Owner(commands.Cog):
    """Owner-only commands for Galaxy AI V2."""

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Owner Check
    # ==========================

    async def owner_only(self, interaction: discord.Interaction):

        app = await self.bot.application_info()

        if interaction.user.id != app.owner.id:

            await interaction.response.send_message(
                "❌ Only the bot owner can use this command.",
                ephemeral=True
            )

            return False

        return True

    # ==========================
    # Shutdown
    # ==========================

    @app_commands.command(
        name="shutdown",
        description="Safely shut down Galaxy AI V2."
    )
    async def shutdown(
        self,
        interaction: discord.Interaction
    ):

        if not await self.owner_only(interaction):
            return

        embed = discord.Embed(
            title="🔴 Shutting Down",
            description="Galaxy AI V2 is shutting down safely...",
            color=0xED4245
        )

        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(2)

        await self.bot.close()

    # ==========================
    # Restart
    # ==========================

    @app_commands.command(
        name="restart",
        description="Restart Galaxy AI V2."
    )
    async def restart(
        self,
        interaction: discord.Interaction
    ):

        if not await self.owner_only(interaction):
            return

        embed = discord.Embed(
            title="🔄 Restart Requested",
            description=(
                "Restart command received.\n"
                "Configure your host (Railway, Replit, etc.) "
                "to automatically restart the bot process."
            ),
            color=0x5865F2
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Bot Status
    # ==========================

    @app_commands.command(
        name="botstatus",
        description="View the current bot status."
    )
    async def botstatus(
        self,
        interaction: discord.Interaction
    ):

        if not await self.owner_only(interaction):
            return

        embed = discord.Embed(
            title="🤖 Galaxy AI V2 Status",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Latency",
            value=f"{round(self.bot.latency * 1000)} ms",
            inline=True
        )

        embed.add_field(
            name="Servers",
            value=str(len(self.bot.guilds)),
            inline=True
        )

        embed.add_field(
            name="Users",
            value=str(len(self.bot.users)),
            inline=True
        )

        await interaction.response.send_message(embed=embed)
      # ==========================
# Reload Cog
# ==========================

@app_commands.command(
    name="reload",
    description="Reload a cog."
)
async def reload(
    self,
    interaction: discord.Interaction,
    cog: str
):

    if not await self.owner_only(interaction):
        return

    try:

        await self.bot.reload_extension(f"cogs.{cog}")

        embed = discord.Embed(
            title="✅ Cog Reloaded",
            description=f"Successfully reloaded **{cog}**.",
            color=0x57F287
        )

    except Exception as e:

        embed = discord.Embed(
            title="❌ Reload Failed",
            description=f"```{e}```",
            color=0xED4245
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Load Cog
# ==========================

@app_commands.command(
    name="load",
    description="Load a cog."
)
async def load(
    self,
    interaction: discord.Interaction,
    cog: str
):

    if not await self.owner_only(interaction):
        return

    try:

        await self.bot.load_extension(f"cogs.{cog}")

        embed = discord.Embed(
            title="✅ Cog Loaded",
            description=f"Successfully loaded **{cog}**.",
            color=0x57F287
        )

    except Exception as e:

        embed = discord.Embed(
            title="❌ Load Failed",
            description=f"```{e}```",
            color=0xED4245
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Unload Cog
# ==========================

@app_commands.command(
    name="unload",
    description="Unload a cog."
)
async def unload(
    self,
    interaction: discord.Interaction,
    cog: str
):

    if not await self.owner_only(interaction):
        return

    if cog.lower() == "owner":

        return await interaction.response.send_message(
            "❌ You cannot unload the owner cog.",
            ephemeral=True
        )

    try:

        await self.bot.unload_extension(f"cogs.{cog}")

        embed = discord.Embed(
            title="✅ Cog Unloaded",
            description=f"Successfully unloaded **{cog}**.",
            color=0x57F287
        )

    except Exception as e:

        embed = discord.Embed(
            title="❌ Unload Failed",
            description=f"```{e}```",
            color=0xED4245
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Sync Slash Commands
# ==========================

@app_commands.command(
    name="sync",
    description="Sync slash commands."
)
async def sync(
    self,
    interaction: discord.Interaction
):

    if not await self.owner_only(interaction):
        return

    synced = await self.bot.tree.sync()

    embed = discord.Embed(
        title="🔄 Slash Commands Synced",
        description=f"Successfully synced **{len(synced)}** command(s).",
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Maintenance Mode
# ==========================

maintenance_mode = False


@app_commands.command(
    name="maintenance",
    description="Enable or disable maintenance mode."
)
async def maintenance(
    self,
    interaction: discord.Interaction,
    enabled: bool
):

    if not await self.owner_only(interaction):
        return

    self.maintenance_mode = enabled

    embed = discord.Embed(
        title="🚧 Maintenance Mode",
        description=(
            "✅ Maintenance Mode Enabled"
            if enabled
            else "❌ Maintenance Mode Disabled"
        ),
        color=0xFEE75C if enabled else 0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Broadcast Message
# ==========================

@app_commands.command(
    name="broadcast",
    description="Broadcast a message to every server."
)
async def broadcast(
    self,
    interaction: discord.Interaction,
    message: str
):

    if not await self.owner_only(interaction):
        return

    sent = 0

    embed = discord.Embed(
        title="📢 Galaxy AI V2 Announcement",
        description=message,
        color=0x8A2BE2,
        timestamp=discord.utils.utcnow()
    )

    embed.set_footer(text="Official Galaxy AI V2 Broadcast")

    for guild in self.bot.guilds:

        target_channel = discord.utils.get(
            guild.text_channels,
            permissions_for=guild.me).send_messages
      channel = None

        for c in guild.text_channels:

            if c.permissions_for(guild.me).send_messages:
                channel = c
                break

        if channel:

            try:
                await channel.send(embed=embed)
                sent += 1
            except Exception:
                pass

    await interaction.response.send_message(
        f"✅ Broadcast sent to **{sent}** server(s).",
        ephemeral=True
    )


# ==========================
# DM User
# ==========================

@app_commands.command(
    name="dmuser",
    description="Send a DM to a user."
)
async def dmuser(
    self,
    interaction: discord.Interaction,
    member: discord.User,
    message: str
):

    if not await self.owner_only(interaction):
        return

    embed = discord.Embed(
        title="💌 Message from Galaxy AI V2",
        description=message,
        color=0x5865F2
    )

    try:
        await member.send(embed=embed)

        await interaction.response.send_message(
            f"✅ Message sent to **{member}**.",
            ephemeral=True
        )

    except discord.Forbidden:

        await interaction.response.send_message(
            "❌ Unable to DM that user.",
            ephemeral=True
        )


# ==========================
# Server List
# ==========================

@app_commands.command(
    name="servers",
    description="View all servers the bot is in."
)
async def servers(
    self,
    interaction: discord.Interaction
):

    if not await self.owner_only(interaction):
        return

    embed = discord.Embed(
        title="🌍 Connected Servers",
        color=0x8A2BE2
    )

    server_list = []

    for guild in self.bot.guilds[:25]:
        server_list.append(
            f"• **{guild.name}** ({guild.member_count} members)"
        )

    embed.description = "\n".join(server_list)

    embed.set_footer(
        text=f"Total Servers: {len(self.bot.guilds)}"
    )

    await interaction.response.send_message(embed=embed)
# ==========================
# Reload All Cogs
# ==========================

@app_commands.command(
    name="reloadall",
    description="Reload every loaded cog."
)
async def reloadall(
    self,
    interaction: discord.Interaction
):

    if not await self.owner_only(interaction):
        return

    successful = 0
    failed = []

    for extension in list(self.bot.extensions.keys()):

        try:
            await self.bot.reload_extension(extension)
            successful += 1

        except Exception as e:
            failed.append(f"{extension}: {e}")

    embed = discord.Embed(
        title="🔄 Reload All Complete",
        color=0x57F287
    )

    embed.add_field(
        name="✅ Reloaded",
        value=str(successful),
        inline=True
    )

    embed.add_field(
        name="❌ Failed",
        value=str(len(failed)),
        inline=True
    )

    if failed:
        embed.add_field(
            name="Errors",
            value="```" + "\n".join(failed[:10]) + "```",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Clear Internal Cache
# ==========================

@app_commands.command(
    name="clearcache",
    description="Run Python garbage collection."
)
async def clearcache(
    self,
    interaction: discord.Interaction
):

    if not await self.owner_only(interaction):
        return

    import gc

    collected = gc.collect()

    embed = discord.Embed(
        title="🧹 Cache Cleared",
        description=f"Collected **{collected}** unused objects.",
        color=0x57F287
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ==========================
# Owner Audit Log
# ==========================

async def owner_log(
    self,
    action: str,
    user: discord.User
):

    print(
        f"[OWNER] {user} ({user.id}) -> {action}"
    )


# ==========================
# Emergency Stop
# ==========================

@app_commands.command(
    name="emergency",
    description="Disable the bot immediately."
)
async def emergency(
    self,
    interaction: discord.Interaction
):

    if not await self.owner_only(interaction):
        return

    embed = discord.Embed(
        title="🚨 Emergency Shutdown",
        description="Galaxy AI V2 is entering emergency shutdown.",
        color=0xED4245
    )

    await interaction.response.send_message(embed=embed)

    await self.bot.close()


# ==========================
# About Owner Commands
# ==========================

@app_commands.command(
    name="ownerhelp",
    description="List all owner commands."
)
async def ownerhelp(
    self,
    interaction: discord.Interaction
):

    if not await self.owner_only(interaction):
        return

    embed = discord.Embed(
        title="👑 Galaxy AI V2 Owner Commands",
        color=0x8A2BE2
    )

    embed.description = (
        "**Available Commands:**\n\n"
        "🔴 /shutdown\n"
        "🔄 /restart\n"
        "🤖 /botstatus\n"
        "📥 /load\n"
        "📤 /unload\n"
        "🔄 /reload\n"
        "🔄 /reloadall\n"
        "🔁 /sync\n"
        "📢 /broadcast\n"
        "💌 /dmuser\n"
        "🌍 /servers\n"
        "📊 /botstats\n"
        "💾 /backupdb\n"
        "📁 /exportserver\n"
        "⚡ /performance\n"
        "🧹 /clearcache\n"
        "🚨 /emergency\n"
        "🚧 /maintenance"
    )

    await interaction.response.send_message(
        embed=embed,
        ephemeral=True
    )


# ==========================
# Setup
# ==========================

async def setup(bot):
    await bot.add_cog(Owner(bot))
