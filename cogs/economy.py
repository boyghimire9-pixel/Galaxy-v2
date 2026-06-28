import discord
import aiosqlite
import random

from discord.ext import commands
from discord import app_commands
from datetime import datetime

import config

DATABASE = config.DATABASE_PATH


class Economy(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # ==========================
    # Create Account
    # ==========================

    async def create_account(self, user_id):

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT user_id
                FROM economy
                WHERE user_id=?
                """,
                (user_id,)
            )

            data = await cursor.fetchone()

            if data is None:

                await db.execute(
                    """
                    INSERT INTO economy
                    (
                        user_id,
                        wallet,
                        bank,
                        daily_streak,
                        job
                    )
                    VALUES
                    (?, ?, ?, ?, ?)
                    """,
                    (
                        user_id,
                        500,
                        0,
                        0,
                        "Unemployed"
                    )
                )

                await db.commit()

    # ==========================
    # Balance
    # ==========================

    @app_commands.command(
        name="balance",
        description="View your wallet and bank."
    )
    async def balance(
        self,
        interaction: discord.Interaction,
        member: discord.Member=None
    ):

        if member is None:
            member = interaction.user

        await self.create_account(member.id)

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT wallet,
                       bank,
                       daily_streak,
                       job
                FROM economy
                WHERE user_id=?
                """,
                (member.id,)
            )

            wallet, bank, streak, job = await cursor.fetchone()

        embed = discord.Embed(
            title="💰 Galaxy Economy",
            color=0x8A2BE2
        )

        embed.add_field(
            name="👛 Wallet",
            value=f"${wallet:,}",
            inline=True
        )

        embed.add_field(
            name="🏦 Bank",
            value=f"${bank:,}",
            inline=True
        )

        embed.add_field(
            name="🔥 Daily Streak",
            value=streak,
            inline=True
        )

        embed.add_field(
            name="💼 Job",
            value=job,
            inline=False
        )

        embed.set_thumbnail(
            url=member.display_avatar.url
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ==========================
    # Daily Reward
    # ==========================

    @app_commands.command(
        name="daily",
        description="Claim your daily reward."
    )
    async def daily(
        self,
        interaction: discord.Interaction
    ):

        await self.create_account(
            interaction.user.id
        )

        reward = random.randint(500, 1000)

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE economy
                SET wallet = wallet + ?,
                    daily_streak = daily_streak + 1
                WHERE user_id = ?
                """,
                (
                    reward,
                    interaction.user.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="🎁 Daily Reward",
            description=f"You received **${reward:,}**!",
            color=0x57F287
        )

        await interaction.response.send_message(
            embed=embed
        )

    # ==========================
    # Work
    # ==========================

    @app_commands.command(
        name="work",
        description="Work to earn money."
    )
    async def work(
        self,
        interaction: discord.Interaction
    ):

        await self.create_account(
            interaction.user.id
        )

        jobs = [
            "Developer",
            "Police",
            "Doctor",
            "Designer",
            "Mechanic",
            "Gamer",
            "YouTuber"
        ]

        job = random.choice(jobs)

        earnings = random.randint(
            300,
            1200
        )

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                """
                UPDATE economy
                SET wallet = wallet + ?,
                    job = ?
                WHERE user_id = ?
                """,
                (
                    earnings,
                    job,
                    interaction.user.id
                )
            )

            await db.commit()

        embed = discord.Embed(
            title="💼 Work Complete",
            color=0x8A2BE2
        )

        embed.add_field(
            name="Job",
            value=job
        )

        embed.add_field(
            name="Earned",
            value=f"${earnings:,}"
        )

        await interaction.response.send_message(
            embed=embed
      )
      # ==========================
# Deposit Money
# ==========================

@app_commands.command(
    name="deposit",
    description="Deposit money into your bank."
)
async def deposit(
    self,
    interaction: discord.Interaction,
    amount: str
):

    await self.create_account(interaction.user.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet, bank FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet, bank = await cursor.fetchone()

        if amount.lower() == "all":
            amount = wallet
        else:
            amount = int(amount)

        if amount <= 0:
            return await interaction.response.send_message(
                "❌ Amount must be greater than 0.",
                ephemeral=True
            )

        if amount > wallet:
            return await interaction.response.send_message(
                "❌ You don't have that much money.",
                ephemeral=True
            )

        await db.execute(
            """
            UPDATE economy
            SET wallet = wallet - ?,
                bank = bank + ?
            WHERE user_id = ?
            """,
            (amount, amount, interaction.user.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="🏦 Deposit Successful",
        description=f"Deposited **${amount:,}** into your bank.",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Withdraw Money
# ==========================

@app_commands.command(
    name="withdraw",
    description="Withdraw money from your bank."
)
async def withdraw(
    self,
    interaction: discord.Interaction,
    amount: str
):

    await self.create_account(interaction.user.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet, bank FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet, bank = await cursor.fetchone()

        if amount.lower() == "all":
            amount = bank
        else:
            amount = int(amount)

        if amount <= 0:
            return await interaction.response.send_message(
                "❌ Amount must be greater than 0.",
                ephemeral=True
            )

        if amount > bank:
            return await interaction.response.send_message(
                "❌ You don't have enough money in your bank.",
                ephemeral=True
            )

        await db.execute(
            """
            UPDATE economy
            SET wallet = wallet + ?,
                bank = bank - ?
            WHERE user_id = ?
            """,
            (amount, amount, interaction.user.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="💵 Withdrawal Successful",
        description=f"Withdrew **${amount:,}** from your bank.",
        color=0x3498DB
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Pay Another User
# ==========================

@app_commands.command(
    name="pay",
    description="Send money to another member."
)
async def pay(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: app_commands.Range[int, 1, 100000000]
):

    if member.bot:
        return await interaction.response.send_message(
            "❌ You cannot pay bots.",
            ephemeral=True
        )

    if member.id == interaction.user.id:
        return await interaction.response.send_message(
            "❌ You cannot pay yourself.",
            ephemeral=True
        )

    await self.create_account(interaction.user.id)
    await self.create_account(member.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet = (await cursor.fetchone())[0]

        if wallet < amount:
            return await interaction.response.send_message(
                "❌ You don't have enough money.",
                ephemeral=True
            )

        await db.execute(
            "UPDATE economy SET wallet = wallet - ? WHERE user_id=?",
            (amount, interaction.user.id)
        )

        await db.execute(
            "UPDATE economy SET wallet = wallet + ? WHERE user_id=?",
            (amount, member.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="💸 Payment Sent",
        description=f"You sent **${amount:,}** to {member.mention}.",
        color=0x8A2BE2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Richest Members
# ==========================

@app_commands.command(
    name="baltop",
    description="View the richest members."
)
async def baltop(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT user_id,
                   wallet,
                   bank
            FROM economy
            ORDER BY (wallet + bank) DESC
            LIMIT 10
            """
        )

        data = await cursor.fetchall()

    embed = discord.Embed(
        title="💎 Richest Members",
        color=0xFFD700
    )

    rank = 1

    for user_id, wallet, bank in data:

        member = interaction.guild.get_member(user_id)

        if member:

            total = wallet + bank

            embed.add_field(
                name=f"#{rank} • {member.display_name}",
                value=f"💰 ${total:,}",
                inline=False
            )

            rank += 1

    await interaction.response.send_message(embed=embed)
  # ==========================
# Coin Flip
# ==========================

@app_commands.command(
    name="coinflip",
    description="Bet money on Heads or Tails."
)
@app_commands.describe(
    side="heads or tails",
    bet="Amount to bet"
)
async def coinflip(
    self,
    interaction: discord.Interaction,
    side: str,
    bet: app_commands.Range[int, 100, 1000000]
):

    side = side.lower()

    if side not in ["heads", "tails"]:
        return await interaction.response.send_message(
            "❌ Choose **heads** or **tails**.",
            ephemeral=True
        )

    await self.create_account(interaction.user.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet = (await cursor.fetchone())[0]

        if wallet < bet:
            return await interaction.response.send_message(
                "❌ You don't have enough money.",
                ephemeral=True
            )

        result = random.choice(["heads", "tails"])

        if result == side:

            winnings = bet

            await db.execute(
                "UPDATE economy SET wallet = wallet + ? WHERE user_id=?",
                (winnings, interaction.user.id)
            )

            message = f"🪙 It landed on **{result.title()}**!\nYou won **${winnings:,}**!"

            color = 0x57F287

        else:

            await db.execute(
                "UPDATE economy SET wallet = wallet - ? WHERE user_id=?",
                (bet, interaction.user.id)
            )

            message = f"🪙 It landed on **{result.title()}**!\nYou lost **${bet:,}**."

            color = 0xED4245

        await db.commit()

    embed = discord.Embed(
        title="🪙 Coin Flip",
        description=message,
        color=color
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Dice
# ==========================

@app_commands.command(
    name="dice",
    description="Roll a dice."
)
async def dice(
    self,
    interaction: discord.Interaction
):

    roll = random.randint(1, 6)

    embed = discord.Embed(
        title="🎲 Dice Roll",
        description=f"You rolled **{roll}**!",
        color=0x8A2BE2
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Slots
# ==========================

@app_commands.command(
    name="slots",
    description="Play the slot machine."
)
async def slots(
    self,
    interaction: discord.Interaction,
    bet: app_commands.Range[int, 100, 1000000]
):

    await self.create_account(interaction.user.id)

    symbols = ["🍒", "🍋", "💎", "⭐", "7️⃣"]

    result = [random.choice(symbols) for _ in range(3)]

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet = (await cursor.fetchone())[0]

        if wallet < bet:
            return await interaction.response.send_message(
                "❌ You don't have enough money.",
                ephemeral=True
            )

        if result[0] == result[1] == result[2]:

            winnings = bet * 5

            await db.execute(
                "UPDATE economy SET wallet = wallet + ? WHERE user_id=?",
                (winnings, interaction.user.id)
            )

            description = f"{' '.join(result)}\n\n🎉 Jackpot!\nYou won **${winnings:,}**!"
            color = 0xFFD700

        else:

            await db.execute(
                "UPDATE economy SET wallet = wallet - ? WHERE user_id=?",
                (bet, interaction.user.id)
            )

            description = f"{' '.join(result)}\n\n😢 You lost **${bet:,}**."
            color = 0xED4245

        await db.commit()

    embed = discord.Embed(
        title="🎰 Galaxy Slots",
        description=description,
        color=color
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Guess Number
# ==========================

@app_commands.command(
    name="guess",
    description="Guess a number from 1 to 10."
)
async def guess(
    self,
    interaction: discord.Interaction,
    number: app_commands.Range[int, 1, 10]
):

    answer = random.randint(1, 10)

    if number == answer:

        reward = 1000

        async with aiosqlite.connect(DATABASE) as db:

            await db.execute(
                "UPDATE economy SET wallet = wallet + ? WHERE user_id=?",
                (reward, interaction.user.id)
            )

            await db.commit()

        embed = discord.Embed(
            title="🎉 Correct!",
            description=f"You guessed **{answer}** and won **${reward:,}**!",
            color=0x57F287
        )

    else:

        embed = discord.Embed(
            title="❌ Wrong Guess",
            description=f"The correct number was **{answer}**.",
            color=0xED4245
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Rock Paper Scissors
# ==========================

@app_commands.command(
    name="rps",
    description="Play Rock, Paper, Scissors."
)
async def rps(
    self,
    interaction: discord.Interaction,
    choice: str
):

    choice = choice.lower()

    options = ["rock", "paper", "scissors"]

    if choice not in options:

        return await interaction.response.send_message(
            "❌ Choose rock, paper, or scissors.",
            ephemeral=True
        )

    bot_choice = random.choice(options)

    if choice == bot_choice:
        result = "🤝 It's a draw!"
    elif (
        (choice == "rock" and bot_choice == "scissors") or
        (choice == "paper" and bot_choice == "rock") or
        (choice == "scissors" and bot_choice == "paper")
    ):
        result = "🎉 You win!"
    else:
        result = "😢 You lose!"

    embed = discord.Embed(
        title="✂️ Rock Paper Scissors",
        description=(
            f"**You:** {choice.title()}\n"
            f"**Galaxy AI:** {bot_choice.title()}\n\n"
            f"{result}"
        ),
        color=0x8A2BE2
    )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Economy Limits
# ==========================

MAX_CREDITS = 100_000_000_000_000_000_000  # 100 Quintillion

SHOP_ITEMS = {

    "apple": {
        "price": 500,
        "sell": 250,
        "rarity": "Common",
        "emoji": "🍎"
    },

    "pizza": {
        "price": 2500,
        "sell": 1250,
        "rarity": "Common",
        "emoji": "🍕"
    },

    "lucky_box": {
        "price": 10000,
        "sell": 5000,
        "rarity": "Rare",
        "emoji": "🎁"
    },

    "xp_booster": {
        "price": 50000,
        "sell": 25000,
        "rarity": "Epic",
        "emoji": "⚡"
    },

    "galaxy_crate": {
        "price": 1000000,
        "sell": 500000,
        "rarity": "Galaxy",
        "emoji": "🌌",
        "premium": True
    }

}


# ==========================
# Shop
# ==========================

@app_commands.command(
    name="shop",
    description="View the Galaxy Shop."
)
async def shop(
    self,
    interaction: discord.Interaction
):

    embed = discord.Embed(
        title="🛒 Galaxy Shop",
        color=0x8A2BE2
    )

    for item, data in SHOP_ITEMS.items():

        premium = " 💎 Premium" if data.get("premium") else ""

        embed.add_field(
            name=f"{data['emoji']} {item.replace('_',' ').title()}",
            value=(
                f"Price: **${data['price']:,}**\n"
                f"Rarity: **{data['rarity']}**{premium}"
            ),
            inline=False
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Buy Item
# ==========================

@app_commands.command(
    name="buy",
    description="Buy an item from the shop."
)
async def buy(
    self,
    interaction: discord.Interaction,
    item: str,
    amount: app_commands.Range[int, 1, 1000] = 1
):

    item = item.lower()

    if item not in SHOP_ITEMS:

        return await interaction.response.send_message(
            "❌ Item not found.",
            ephemeral=True
        )

    await self.create_account(interaction.user.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet = (await cursor.fetchone())[0]

        cost = SHOP_ITEMS[item]["price"] * amount

        if wallet < cost:

            return await interaction.response.send_message(
                "❌ You don't have enough credits.",
                ephemeral=True
            )

        wallet -= cost

        await db.execute(
            """
            UPDATE economy
            SET wallet=?
            WHERE user_id=?
            """,
            (
                wallet,
                interaction.user.id
            )
        )

        await db.execute(
            """
            INSERT INTO inventory
            (user_id,item,amount)
            VALUES(?,?,?)
            ON CONFLICT(user_id,item)
            DO UPDATE SET
            amount=amount+excluded.amount
            """,
            (
                interaction.user.id,
                item,
                amount
            )
        )

        await db.commit()

    embed = discord.Embed(
        title="🛍️ Purchase Successful",
        description=f"You bought **{amount}x {item.replace('_',' ').title()}**.",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Inventory
# ==========================

@app_commands.command(
    name="inventory",
    description="View your inventory."
)
async def inventory(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT item,amount
            FROM inventory
            WHERE user_id=?
            """,
            (interaction.user.id,)
        )

        items = await cursor.fetchall()

    embed = discord.Embed(
        title="🎒 Inventory",
        color=0x8A2BE2
    )

    if not items:

        embed.description = "Your inventory is empty."

    else:

        for item, amount in items:

            info = SHOP_ITEMS.get(item)

            if info:

                embed.add_field(
                    name=f"{info['emoji']} {item.replace('_',' ').title()}",
                    value=f"Quantity: **{amount}**",
                    inline=False
                )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Sell Item
# ==========================

@app_commands.command(
    name="sell",
    description="Sell an item from your inventory."
)
async def sell(
    self,
    interaction: discord.Interaction,
    item: str,
    amount: app_commands.Range[int, 1, 1000] = 1
):

    item = item.lower()

    if item not in SHOP_ITEMS:
        return await interaction.response.send_message(
            "❌ That item doesn't exist.",
            ephemeral=True
        )

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT amount
            FROM inventory
            WHERE user_id=? AND item=?
            """,
            (interaction.user.id, item)
        )

        data = await cursor.fetchone()

        if data is None or data[0] < amount:
            return await interaction.response.send_message(
                "❌ You don't own enough of that item.",
                ephemeral=True
            )

        sell_price = SHOP_ITEMS[item]["sell"] * amount

        wallet_cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet = (await wallet_cursor.fetchone())[0]
        wallet = min(wallet + sell_price, MAX_CREDITS)

        await db.execute(
            """
            UPDATE economy
            SET wallet=?
            WHERE user_id=?
            """,
            (wallet, interaction.user.id)
        )

        await db.execute(
            """
            UPDATE inventory
            SET amount=amount-?
            WHERE user_id=? AND item=?
            """,
            (amount, interaction.user.id, item)
        )

        await db.execute(
            """
            DELETE FROM inventory
            WHERE user_id=? AND item=? AND amount<=0
            """,
            (interaction.user.id, item)
        )

        await db.commit()

    embed = discord.Embed(
        title="💸 Item Sold",
        description=f"You sold **{amount}x {item.replace('_',' ').title()}** for **${sell_price:,}**.",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Use Item
# ==========================

@app_commands.command(
    name="use",
    description="Use an item from your inventory."
)
async def use(
    self,
    interaction: discord.Interaction,
    item: str
):

    item = item.lower()

    if item == "xp_booster":

        reward = random.randint(500, 2500)

        embed = discord.Embed(
            title="⚡ XP Booster",
            description=f"You activated an XP Booster!\n**+{reward} XP**",
            color=0x8A2BE2
        )

    elif item == "lucky_box":

        reward = random.randint(1000, 10000)

        embed = discord.Embed(
            title="🎁 Lucky Box",
            description=f"You opened a Lucky Box and found **${reward:,}**!",
            color=0xFFD700
        )

    elif item == "galaxy_crate":

        reward = random.randint(50000, 500000)

        embed = discord.Embed(
            title="🌌 Galaxy Crate",
            description=f"You received **${reward:,}** and a rare collectible!",
            color=0x9B59B6
        )

    else:

        embed = discord.Embed(
            title="❌",
            description="That item can't be used.",
            color=0xED4245
        )

    await interaction.response.send_message(embed=embed)


# ==========================
# Open Crate
# ==========================

@app_commands.command(
    name="crate",
    description="Open a premium crate."
)
async def crate(
    self,
    interaction: discord.Interaction
):

    rewards = [
        50000,
        75000,
        100000,
        250000,
        500000,
        1000000
    ]

    reward = random.choice(rewards)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (interaction.user.id,)
        )

        wallet = (await cursor.fetchone())[0]
        wallet = min(wallet + reward, MAX_CREDITS)

        await db.execute(
            """
            UPDATE economy
            SET wallet=?
            WHERE user_id=?
            """,
            (wallet, interaction.user.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="📦 Galaxy Crate",
        description=f"Congratulations! You found **${reward:,}**!",
        color=0x9B59B6
    )

    await interaction.response.send_message(embed=embed)
  # ==========================
# Economy Constants
# ==========================

MAX_CREDITS = 100_000_000_000_000_000_000  # 100 Quintillion
PREMIUM_MULTIPLIER = 1.5


# ==========================
# Add Money
# ==========================

@app_commands.command(
    name="addmoney",
    description="Add money to a user's wallet."
)
@app_commands.default_permissions(administrator=True)
async def addmoney(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: app_commands.Range[int, 1, 100_000_000_000]
):

    await self.create_account(member.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (member.id,)
        )

        wallet = (await cursor.fetchone())[0]
        wallet = min(wallet + amount, MAX_CREDITS)

        await db.execute(
            "UPDATE economy SET wallet=? WHERE user_id=?",
            (wallet, member.id)
        )

        await db.commit()

    embed = discord.Embed(
        title="💰 Money Added",
        description=f"Added **${amount:,}** to {member.mention}.",
        color=0x57F287
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Remove Money
# ==========================

@app_commands.command(
    name="removemoney",
    description="Remove money from a user's wallet."
)
@app_commands.default_permissions(administrator=True)
async def removemoney(
    self,
    interaction: discord.Interaction,
    member: discord.Member,
    amount: app_commands.Range[int, 1, 100_000_000_000]
):

    await self.create_account(member.id)

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            "SELECT wallet FROM economy WHERE user_id=?",
            (member.id,)
        )

        wallet = (await cursor.fetchone())[0]
        wallet = max(wallet - amount, 0)

        await db.execute(
            "UPDATE economy SET wallet=? WHERE user_id=?",
            (wallet, member.id)
        )

        await db.commit()

    await interaction.response.send_message(
        f"✅ Removed **${amount:,}** from {member.mention}."
    )


# ==========================
# Economy Statistics
# ==========================

@app_commands.command(
    name="economystats",
    description="View economy statistics."
)
async def economystats(
    self,
    interaction: discord.Interaction
):

    async with aiosqlite.connect(DATABASE) as db:

        total_users = await (
            await db.execute(
                "SELECT COUNT(*) FROM economy"
            )
        ).fetchone()

        total_money = await (
            await db.execute(
                "SELECT SUM(wallet + bank) FROM economy"
            )
        ).fetchone()

    embed = discord.Embed(
        title="📊 Galaxy Economy Stats",
        color=0x8A2BE2
    )

    embed.add_field(
        name="👥 Users",
        value=f"{total_users[0]:,}",
        inline=True
    )

    embed.add_field(
        name="💰 Total Credits",
        value=f"${(total_money[0] or 0):,}",
        inline=True
    )

    await interaction.response.send_message(embed=embed)


# ==========================
# Reset Economy
# ==========================

@app_commands.command(
    name="reseteconomy",
    description="Reset a member's economy."
)
@app_commands.default_permissions(administrator=True)
async def reseteconomy(
    self,
    interaction: discord.Interaction,
    member: discord.Member
):

    async with aiosqlite.connect(DATABASE) as db:

        await db.execute(
            """
            UPDATE economy
            SET wallet=500,
                bank=0,
                daily_streak=0,
                job='Unemployed'
            WHERE user_id=?
            """,
            (member.id,)
        )

        await db.commit()

    await interaction.response.send_message(
        f"🔄 Economy reset for {member.mention}."
    )


# ==========================
# Setup
# ==========================

async def setup(bot):
    await bot.add_cog(Economy(bot))
