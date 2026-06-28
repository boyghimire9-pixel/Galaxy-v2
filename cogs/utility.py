import asyncio
import discord
import platform
import time

from discord.ext import commands
from discord import app_commands

import config


class Utility(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.start_time = time.time()

    # ==========================
    # Ping
    # ==========================

    @app_commands.command(
        name="ping",
        description="Shows the bot latency."
    )
    async def ping(
        self,
        interaction: discord.Interaction
    ):

        latency = round(self.bot.latency * 1000)

        embed = discord.Embed(
            title="🏓 Pong!",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Bot Latency",
            value=f"**{latency} ms**",
            inline=False
        )

        embed.set_footer(
            text="Galaxy AI V2"
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Uptime
    # ==========================

    @app_commands.command(
        name="uptime",
        description="Shows the bot uptime."
    )
    async def uptime(
        self,
        interaction: discord.Interaction
    ):

        seconds = int(time.time() - self.start_time)

        days = seconds // 86400
        hours = (seconds % 86400) // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60

        embed = discord.Embed(
            title="⏱️ Bot Uptime",
            color=0x5865F2
        )

        embed.description = (
            f"**{days}d {hours}h {minutes}m {seconds}s**"
        )

        await interaction.response.send_message(embed=embed)

    # ==========================
    # Bot Info
    # ==========================

    @app_commands.command(
        name="botinfo",
        description="Shows information about Galaxy AI V2."
    )
    async def botinfo(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="🌌 Galaxy AI V2",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Python",
            value=platform.python_version(),
            inline=True
        )

        embed.add_field(
            name="discord.py",
            value=discord.__version__,
            inline=True
        )

        embed.add_field(
            name="Servers",
            value=len(self.bot.guilds),
            inline=True
        )

        embed.add_field(
            name="Users",
            value=len(self.bot.users),
            inline=True
        )

        embed.set_thumbnail(
            url=self.bot.user.display_avatar.url
        )

        await interaction.response.send_message(embed=embed)
      # ==========================
# User Info
# ==========================

@app_commands.command(
    name="userinfo",
    description="View detailed information about a user."
)
async def userinfo(
    self,
    interaction: discord.Interaction,
    member: discord.Member | None = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title=f"👤 {member}",
        color=0x8A2BE2
    )

    embed.set_thumbnail(
        url=member.display_avatar.url
    )

    embed.add_field(
        name="🆔 User ID",
        value=str(member.id),
        inline=False
    )

    embed.add_field(
        name="📅 Account Created",
        value=f"<t:{int(member.created_at.timestamp())}:F>",
        inline=False
    )

    embed.add_field(
        name="📥 Joined Server",
        value=f"<t:{int(member.joined_at.timestamp())}:F>",
        inline=False
    )

    embed.add_field(
        name="🤖 Bot",
        value="Yes" if member.bot else "No",
        inline=True
    )

    roles = [role.mention for role in member.roles[1:]]

    embed.add_field(
        name="🎭 Roles",
        value=", ".join(roles[:20]) if roles else "None",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Avatar
# ==========================

@app_commands.command(
    name="avatar",
    description="View a user's avatar."
)
async def avatar(
    self,
    interaction: discord.Interaction,
    member: discord.Member | None = None
):

    member = member or interaction.user

    embed = discord.Embed(
        title=f"🖼️ {member.display_name}'s Avatar",
        color=0x5865F2
    )

    embed.set_image(
        url=member.display_avatar.url
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Banner
# ==========================

@app_commands.command(
    name="banner",
    description="View a user's banner."
)
async def banner(
    self,
    interaction: discord.Interaction,
    member: discord.Member | None = None
):

    member = member or interaction.user

    user = await self.bot.fetch_user(member.id)

    embed = discord.Embed(
        title=f"🎨 {member.display_name}'s Banner",
        color=0x8A2BE2
    )

    if user.banner:

        embed.set_image(url=user.banner.url)

    else:

        embed.description = "This user does not have a banner."

    await interaction.response.send_message(embed=embed)


# ==========================
# Role Info
# ==========================

@app_commands.command(
    name="roleinfo",
    description="View information about a role."
)
async def roleinfo(
    self,
    interaction: discord.Interaction,
    role: discord.Role
):

    embed = discord.Embed(
        title=f"🎭 {role.name}",
        color=role.color if role.color.value else 0x8A2BE2
    )

    embed.add_field(
        name="🆔 Role ID",
        value=str(role.id),
        inline=False
    )

    embed.add_field(
        name="👥 Members",
        value=str(len(role.members)),
        inline=True
    )

    embed.add_field(
        name="📍 Position",
        value=str(role.position),
        inline=True
    )

    embed.add_field(
        name="📅 Created",
        value=f"<t:{int(role.created_at.timestamp())}:F>",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Channel Info
# ==========================

@app_commands.command(
    name="channelinfo",
    description="View information about a channel."
)
async def channelinfo(
    self,
    interaction: discord.Interaction,
    channel: discord.TextChannel | None = None
):

    channel = channel or interaction.channel

    embed = discord.Embed(
        title=f"📺 #{channel.name}",
        color=0x5865F2
    )

    embed.add_field(
        name="🆔 Channel ID",
        value=str(channel.id),
        inline=False
    )

    embed.add_field(
        name="📂 Category",
        value=channel.category.name if channel.category else "None",
        inline=True
    )

    embed.add_field(
        name="🐌 Slowmode",
        value=f"{channel.slowmode_delay}s",
        inline=True
    )

    embed.add_field(
        name="📅 Created",
        value=f"<t:{int(channel.created_at.timestamp())}:F>",
        inline=False
    )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Server Info
# ==========================

@app_commands.command(
    name="serverinfo",
    description="Shows information about this server."
)
async def serverinfo(
    self,
    interaction: discord.Interaction
):

    guild = interaction.guild

    humans = len([m for m in guild.members if not m.bot])
    bots = len([m for m in guild.members if m.bot])

    embed = discord.Embed(
        title=f"🌌 {guild.name}",
        color=0x8A2BE2
    )

    if guild.icon:
        embed.set_thumbnail(url=guild.icon.url)

    embed.add_field(
        name="👑 Owner",
        value=guild.owner.mention if guild.owner else "Unknown",
        inline=True
    )

    embed.add_field(
        name="👥 Members",
        value=str(guild.member_count),
        inline=True
    )

    embed.add_field(
        name="🤖 Bots",
        value=str(bots),
        inline=True
    )

    embed.add_field(
        name="👤 Humans",
        value=str(humans),
        inline=True
    )

    embed.add_field(
        name="💬 Channels",
        value=str(len(guild.channels)),
        inline=True
    )

    embed.add_field(
        name="🎭 Roles",
        value=str(len(guild.roles)),
        inline=True
    )

    embed.add_field(
        name="😀 Emojis",
        value=str(len(guild.emojis)),
        inline=True
    )

    embed.add_field(
        name="🚀 Boost Level",
        value=str(guild.premium_tier),
        inline=True
    )

    embed.add_field(
        name="📅 Created",
        value=f"<t:{int(guild.created_at.timestamp())}:F>",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Invite
# ==========================

@app_commands.command(
    name="invite",
    description="Get the bot invite link."
)
async def invite(
    self,
    interaction: discord.Interaction
):

    permissions = discord.Permissions(administrator=True)

    invite = discord.utils.oauth_url(
        self.bot.user.id,
        permissions=permissions,
        scopes=("bot", "applications.commands")
    )

    embed = discord.Embed(
        title="🔗 Invite Galaxy AI V2",
        description=f"[Click Here To Invite]({invite})",
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Emoji Info
# ==========================

@app_commands.command(
    name="emojiinfo",
    description="View information about a custom emoji."
)
async def emojiinfo(
    self,
    interaction: discord.Interaction,
    emoji: discord.Emoji
):

    embed = discord.Embed(
        title=f"😀 {emoji.name}",
        color=0x8A2BE2
    )

    embed.set_thumbnail(url=emoji.url)

    embed.add_field(
        name="🆔 ID",
        value=str(emoji.id),
        inline=False
    )

    embed.add_field(
        name="🎭 Animated",
        value="Yes" if emoji.animated else "No",
        inline=True
    )

    embed.add_field(
        name="📅 Created",
        value=f"<t:{int(emoji.created_at.timestamp())}:F>",
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Sticker Info
# ==========================

@app_commands.command(
    name="stickerinfo",
    description="View information about a sticker."
)
async def stickerinfo(
    self,
    interaction: discord.Interaction,
    sticker: discord.GuildSticker
):

    embed = discord.Embed(
        title=f"📌 {sticker.name}",
        color=0x5865F2
    )

    embed.add_field(
        name="🆔 Sticker ID",
        value=str(sticker.id),
        inline=False
    )

    embed.add_field(
        name="📄 Description",
        value=sticker.description or "No description",
        inline=False
    )

    embed.add_field(
        name="😀 Emoji",
        value=sticker.emoji or "None",
        inline=True
    )

    await interaction.response.send_message(embed=embed)
  class HelpMenu(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=300)

    @discord.ui.select(
        placeholder="📚 Select a command category...",
        options=[
            discord.SelectOption(label="Moderation", emoji="🛡️"),
            discord.SelectOption(label="Utility", emoji="🛠️"),
            discord.SelectOption(label="Economy", emoji="💰"),
            discord.SelectOption(label="Levels", emoji="⭐"),
            discord.SelectOption(label="Tickets", emoji="🎫"),
            discord.SelectOption(label="Giveaways", emoji="🎉"),
            discord.SelectOption(label="Premium", emoji="💎"),
        ]
    )
    async def category_select(
        self,
        interaction: discord.Interaction,
        select: discord.ui.Select
    ):

        embed = discord.Embed(
            title=f"📚 {select.values[0]} Commands",
            description=(
                f"Here are the available **{select.values[0]}** commands.\n"
                "More detailed help will be added in the next part."
            ),
            color=0x8A2BE2
        )

        await interaction.response.edit_message(
            embed=embed,
            view=self
  )
    # ==========================
# Help Command
# ==========================

@app_commands.command(
    name="help",
    description="View all Galaxy AI V2 commands."
)
async def help(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🌌 Galaxy AI V2 Help Center",
        description=(
            "Welcome to **Galaxy AI V2**!\n\n"
            "📚 Use the dropdown menu below to browse command categories.\n\n"
            "**Available Categories:**\n"
            "🛡️ Moderation\n"
            "🛠️ Utility\n"
            "💰 Economy\n"
            "⭐ Levels\n"
            "🎫 Tickets\n"
            "🎉 Giveaways\n"
            "💎 Premium\n"
            "🤖 AI\n"
            "👑 Owner"
        ),
        color=0x8A2BE2
    )

    embed.set_thumbnail(url=self.bot.user.display_avatar.url)

    embed.set_footer(
        text="Galaxy AI V2 • Interactive Help Menu"
    )

    await interaction.response.send_message(
        embed=embed,
        view=HelpMenu()
    )


# ==========================
# Command Search
# ==========================

@app_commands.command(
    name="command",
    description="Search for a command."
)
async def command(
    self,
    interaction: discord.Interaction,
    name: str
):

    cmd = self.bot.tree.get_command(name)

    if cmd is None:

        return await interaction.response.send_message(
            "❌ Command not found.",
            ephemeral=True
        )

    embed = discord.Embed(
        title=f"📖 /{cmd.name}",
        color=0x5865F2
    )

    embed.description = cmd.description or "No description available."

    await interaction.response.send_message(embed=embed)


# ==========================
# Command Count
# ==========================

@app_commands.command(
    name="commandcount",
    description="Shows the total number of slash commands."
)
async def commandcount(
    self,
    interaction: discord.Interaction
):

    total = len(self.bot.tree.get_commands())

    embed = discord.Embed(
        title="📊 Command Statistics",
        color=0x8A2BE2
    )

    embed.add_field(
        name="Total Slash Commands",
        value=str(total),
        inline=False
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Support
# ==========================

@app_commands.command(
    name="support",
    description="Get the support server."
)
async def support(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🆘 Support",
        description=(
            "Need help?\n\n"
            "Join the official Galaxy AI V2 support server.\n"
            "Replace the link below with your Discord invite."
        ),
        color=0x5865F2
    )

    embed.add_field(
        name="Support Server",
        value="https://discord.gg/YOUR_INVITE"
    )

    await interaction.response.send_message(embed=embed)
  import random

# ==========================
# Snowflake Info
# ==========================

@app_commands.command(
    name="snowflake",
    description="Get the creation date of a Discord snowflake ID."
)
async def snowflake(
    self,
    interaction: discord.Interaction,
    snowflake_id: str
):

    try:
        snowflake = discord.Object(id=int(snowflake_id))
        created = discord.utils.snowflake_time(snowflake.id)

        embed = discord.Embed(
            title="❄️ Snowflake Information",
            color=0x8A2BE2
        )

        embed.add_field(
            name="🆔 ID",
            value=str(snowflake.id),
            inline=False
        )

        embed.add_field(
            name="📅 Created",
            value=f"<t:{int(created.timestamp())}:F>",
            inline=False
        )

        await interaction.response.send_message(embed=embed)

    except ValueError:
        await interaction.response.send_message(
            "❌ Invalid snowflake ID.",
            ephemeral=True
        )


# ==========================
# Timestamp Generator
# ==========================

@app_commands.command(
    name="timestamp",
    description="Generate a Discord timestamp."
)
async def timestamp(
    self,
    interaction: discord.Interaction
):

    now = int(discord.utils.utcnow().timestamp())

    embed = discord.Embed(
        title="⏰ Discord Timestamp",
        color=0x5865F2
    )

    embed.description = (
        f"Default:\n"
        f"`<t:{now}>`\n\n"
        f"Relative:\n"
        f"`<t:{now}:R>`"
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Poll
# ==========================

@app_commands.command(
    name="poll",
    description="Create a simple yes/no poll."
)
async def poll(
    self,
    interaction: discord.Interaction,
    question: str
):

    embed = discord.Embed(
        title="📊 Poll",
        description=question,
        color=0x8A2BE2
    )

    embed.set_footer(
        text=f"Started by {interaction.user}"
    )

    await interaction.response.send_message(embed=embed)

    message = await interaction.original_response()

    await message.add_reaction("👍")
    await message.add_reaction("👎")


# ==========================
# Random Number
# ==========================

@app_commands.command(
    name="random",
    description="Generate a random number."
)
async def random_number(
    self,
    interaction: discord.Interaction,
    minimum: int,
    maximum: int
):

    if minimum >= maximum:

        return await interaction.response.send_message(
            "❌ Minimum must be less than maximum.",
            ephemeral=True
        )

    number = random.randint(minimum, maximum)

    embed = discord.Embed(
        title="🎲 Random Number",
        description=f"**{number}**",
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Choose
# ==========================

@app_commands.command(
    name="choose",
    description="Choose one option from a list."
)
async def choose(
    self,
    interaction: discord.Interaction,
    options: str
):

    items = [item.strip() for item in options.split(",") if item.strip()]

    if len(items) < 2:

        return await interaction.response.send_message(
            "❌ Enter at least two options separated by commas.",
            ephemeral=True
        )

    choice = random.choice(items)

    embed = discord.Embed(
        title="🎯 Choice Selected",
        description=f"**{choice}**",
        color=0x8A2BE2
    )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Embed Creator
# ==========================

@app_commands.command(
    name="embed",
    description="Create a simple embed."
)
@app_commands.default_permissions(manage_messages=True)
async def embed(
    self,
    interaction: discord.Interaction,
    title: str,
    description: str,
    color: str = "#8A2BE2"
):

    try:
        embed_color = discord.Color.from_str(color)
    except ValueError:
        embed_color = discord.Color(0x8A2BE2)

    embed = discord.Embed(
        title=title,
        description=description,
        color=embed_color,
        timestamp=discord.utils.utcnow()
    )

    embed.set_footer(text=f"Created by {interaction.user}")

    await interaction.response.send_message(embed=embed)


# ==========================
# Reminder
# ==========================

@app_commands.command(
    name="remind",
    description="Set a reminder."
)
async def remind(
    self,
    interaction: discord.Interaction,
    minutes: app_commands.Range[int, 1, 10080],
    reminder: str
):

    await interaction.response.send_message(
        f"⏰ Reminder set! I'll remind you in **{minutes}** minute(s).",
        ephemeral=True
    )

    await asyncio.sleep(minutes * 60)

    try:
        reminder_embed = discord.Embed(
            title="⏰ Reminder",
            description=reminder,
            color=0x8A2BE2,
            timestamp=discord.utils.utcnow()
        )

        await interaction.user.send(embed=reminder_embed)

    except discord.Forbidden:
        pass


# ==========================
# Translate Info
# ==========================

@app_commands.command(
    name="translateinfo",
    description="Information about the AI translation feature."
)
async def translateinfo(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🌍 Translation",
        description=(
            "Use the AI translation commands to translate text between "
            "multiple languages.\n\n"
            "Supported languages depend on the AI service configured "
            "for Galaxy AI V2."
        ),
        color=0x5865F2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# About
# ==========================

@app_commands.command(
    name="about",
    description="About Galaxy AI V2."
)
async def about(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🌌 About Galaxy AI V2",
        description=(
            "**Galaxy AI V2** is a modular Discord bot featuring:\n\n"
            "🛡️ Moderation\n"
            "🤖 AI Tools\n"
            "🎫 Ticket System\n"
            "💰 Economy\n"
            "⭐ Levels\n"
            "🎉 Giveaways\n"
            "💎 Premium System\n"
            "📊 Logging\n"
            "🛠️ Utility Commands"
        ),
        color=0x8A2BE2
    )

    embed.set_thumbnail(url=self.bot.user.display_avatar.url)

    embed.set_footer(text="Galaxy AI V2")

    await interaction.response.send_message(embed=embed)


# ==========================
# Setup
# ==========================

async def setup(bot):
    await bot.add_cog(Utility(bot))
