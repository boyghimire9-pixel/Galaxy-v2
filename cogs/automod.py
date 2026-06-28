import re
import discord
from discord.ext import commands

# ==========================
# SETTINGS
# ==========================

SPAM_LIMIT = 5
SPAM_INTERVAL = 7

MAX_CAPS_PERCENT = 70
MAX_MENTIONS = 5

BAD_WORDS = {
    "badword1",
    "badword2",
    "badword3"
}

SCAM_KEYWORDS = [
    "free nitro",
    "steam gift",
    "claim reward",
    "free robux",
    "airdrop",
    "crypto giveaway"
]

INVITE_REGEX = r"(discord\.gg|discord\.com/invite)/"

LINK_REGEX = r"https?://"

# ==========================
# COG
# ==========================

class AutoMod(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.user_messages = {}

    # ==========================
    # Message Event
    # ==========================

    @commands.Cog.listener()
    async def on_message(self, message):

        if message.author.bot:
            return

        if not message.guild:
            return

        await self.check_spam(message)
        await self.check_links(message)
        await self.check_invites(message)
        await self.check_caps(message)
        await self.check_mentions(message)
        await self.check_bad_words(message)
        await self.check_scam(message)
      # ==========================
    # Anti Spam
    # ==========================

    async def check_spam(self, message):

        uid = message.author.id

        if uid not in self.user_messages:
            self.user_messages[uid] = []

        self.user_messages[uid].append(message.created_at)

        self.user_messages[uid] = [
            t for t in self.user_messages[uid]
            if (message.created_at - t).seconds <= SPAM_INTERVAL
        ]

        if len(self.user_messages[uid]) >= SPAM_LIMIT:

            await message.delete()

            await message.channel.send(
                f"⚠️ {message.author.mention} please stop spamming.",
                delete_after=5
            )

            self.user_messages[uid].clear()
          # ==========================
    # Anti Links
    # ==========================

    async def check_links(self, message):

        if message.author.guild_permissions.manage_messages:
            return

        if re.search(LINK_REGEX, message.content.lower()):

            await message.delete()

            await message.channel.send(
                f"🔗 {message.author.mention}, links are not allowed.",
                delete_after=5
            )

    # ==========================
    # Anti Invites
    # ==========================

    async def check_invites(self, message):

        if message.author.guild_permissions.manage_messages:
            return

        if re.search(INVITE_REGEX, message.content.lower()):

            await message.delete()

            await message.channel.send(
                f"🚫 {message.author.mention}, Discord invites are not allowed.",
                delete_after=5
            )

    # ==========================
    # Anti Caps
    # ==========================

    async def check_caps(self, message):

        if len(message.content) < 10:
            return

        letters = [c for c in message.content if c.isalpha()]

        if not letters:
            return

        caps = sum(1 for c in letters if c.isupper())

        percent = (caps / len(letters)) * 100

        if percent >= MAX_CAPS_PERCENT:

            await message.delete()

            await message.channel.send(
                f"🔠 {message.author.mention}, please avoid excessive capital letters.",
                delete_after=5
            )

    # ==========================
    # Anti Mass Mention
    # ==========================

    async def check_mentions(self, message):

        if len(message.mentions) >= MAX_MENTIONS:

            await message.delete()

            await message.channel.send(
                f"👥 {message.author.mention}, mass mentioning is not allowed.",
                delete_after=5
          )
          # ==========================
    # Anti Bad Words
    # ==========================

    async def check_bad_words(self, message):

        if message.author.guild_permissions.manage_messages:
            return

        content = message.content.lower()

        for word in BAD_WORDS:

            if word in content:

                await message.delete()

                await message.channel.send(
                    f"🤬 {message.author.mention}, inappropriate language is not allowed.",
                    delete_after=5
                )

                return

    # ==========================
    # Anti Scam
    # ==========================

    async def check_scam(self, message):

        if message.author.guild_permissions.manage_messages:
            return

        content = message.content.lower()

        for keyword in SCAM_KEYWORDS:

            if keyword in content:

                await message.delete()

                await message.channel.send(
                    f"🚨 {message.author.mention}, possible scam message detected.",
                    delete_after=5
                )

                return

    # ==========================
    # Auto Warn
    # ==========================

    async def auto_warn(self, member, reason):

        try:
            await member.send(
                f"⚠️ You have been automatically warned.\nReason: **{reason}**"
            )
        except:
            pass

    # ==========================
    # Auto Timeout
    # ==========================

    async def auto_timeout(self, member, minutes=10):

        try:

            from datetime import timedelta

            until = discord.utils.utcnow() + timedelta(minutes=minutes)

            await member.edit(
                timed_out_until=until,
                reason="Galaxy AI AutoMod"
            )

        except Exception as e:

            print(e)

    # ==========================
    # Whitelist Check
    # ==========================

    def is_whitelisted(self, member):

        if member.guild_permissions.administrator:
            return True

        if member.guild_permissions.manage_guild:
            return True

        return False
      # ==========================
    # Auto Kick
    # ==========================

    async def auto_kick(self, member, reason="Galaxy AI AutoMod"):

        try:
            await member.kick(reason=reason)
        except Exception as e:
            print(e)

    # ==========================
    # Auto Ban
    # ==========================

    async def auto_ban(self, member, reason="Galaxy AI AutoMod"):

        try:
            await member.ban(reason=reason)
        except Exception as e:
            print(e)

    # ==========================
    # AutoMod Logs
    # ==========================

    async def send_log(self, guild, title, description):

        # TODO:
        # Replace with database-configured log channel.

        channel = discord.utils.get(
            guild.text_channels,
            name="automod-logs"
        )

        if channel is None:
            return

        embed = discord.Embed(
            title=title,
            description=description,
            color=0x8A2BE2
        )

        embed.set_footer(text="Galaxy AI V2 AutoMod")

        await channel.send(embed=embed)

    # ==========================
    # Error Handler
    # ==========================

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):

        print(error)

    # ==========================
    # Ready Event
    # ==========================

    @commands.Cog.listener()
    async def on_ready(self):

        print("✅ AutoMod Loaded")


# ==========================
# Setup
# ==========================

async def setup(bot):

    await bot.add_cog(
        AutoMod(bot)
      )
