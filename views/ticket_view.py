import asyncio
import discord
from discord.ext import commands
import aiosqlite
import config

DATABASE = config.DATABASE_PATH


class CreateTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Create Ticket",
            emoji="🎫",
            style=discord.ButtonStyle.green,
            custom_id="create_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        guild = interaction.guild

        async with aiosqlite.connect(DATABASE) as db:

            cursor = await db.execute(
                """
                SELECT
                    category_id,
                    support_role
                FROM ticket_settings
                WHERE guild_id=?
                """,
                (guild.id,)
            )

            settings = await cursor.fetchone()

        if settings is None:

            return await interaction.response.send_message(
                "❌ Ticket system has not been configured.",
                ephemeral=True
            )

        category_id, support_role = settings

        category = guild.get_channel(category_id)

        if category is None:

            return await interaction.response.send_message(
                "❌ Ticket category not found.",
                ephemeral=True
            )

        overwrites = {

            guild.default_role: discord.PermissionOverwrite(
                view_channel=False
            ),

            interaction.user: discord.PermissionOverwrite(
                view_channel=True,
                send_messages=True,
                attach_files=True,
                read_message_history=True
            )
        }

        if support_role:

            role = guild.get_role(support_role)

            if role:

                overwrites[role] = discord.PermissionOverwrite(
                    view_channel=True,
                    send_messages=True
                )

        channel = await guild.create_text_channel(
            name=f"ticket-{interaction.user.name}",
            category=category,
            overwrites=overwrites
        )

        embed = discord.Embed(
            title="🎫 Ticket Created",
            description=(
                f"Welcome {interaction.user.mention}!\n\n"
                "Please explain your issue and wait for staff."
            ),
            color=0x8A2BE2
        )

        await channel.send(
            interaction.user.mention,
            embed=embed,
            view=TicketView()
        )

        await interaction.response.send_message(
            f"✅ Your ticket has been created: {channel.mention}",
            ephemeral=True
        )


class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(CreateTicketButton())
      # ==========================
# Close Ticket Button
# ==========================

class CloseTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Close Ticket",
            emoji="🔒",
            style=discord.ButtonStyle.red,
            custom_id="close_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        embed = discord.Embed(
            title="🔒 Ticket Closed",
            description=(
                "This ticket has been closed.\n"
                "It will be deleted in **10 seconds**."
            ),
            color=0xED4245
        )

        await interaction.response.send_message(embed=embed)

        await asyncio.sleep(10)

        await interaction.channel.delete()


# ==========================
# Delete Ticket Button
# ==========================

class DeleteTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Delete Ticket",
            emoji="🗑️",
            style=discord.ButtonStyle.danger,
            custom_id="delete_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "🗑️ Deleting ticket...",
            ephemeral=True
        )

        await asyncio.sleep(3)

        await interaction.channel.delete()


# ==========================
# Lock Ticket Button
# ==========================

class LockTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Lock Ticket",
            emoji="🔐",
            style=discord.ButtonStyle.secondary,
            custom_id="lock_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.channel.guild.default_role
        )

        overwrite.send_messages = False

        await interaction.channel.set_permissions(
            interaction.channel.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "🔐 Ticket locked."
        )


# ==========================
# Unlock Ticket Button
# ==========================

class UnlockTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Unlock Ticket",
            emoji="🔓",
            style=discord.ButtonStyle.success,
            custom_id="unlock_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        overwrite = interaction.channel.overwrites_for(
            interaction.channel.guild.default_role
        )

        overwrite.send_messages = None

        await interaction.channel.set_permissions(
            interaction.channel.guild.default_role,
            overwrite=overwrite
        )

        await interaction.response.send_message(
            "🔓 Ticket unlocked."
        )
      class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(CreateTicketButton())
        self.add_item(CloseTicketButton())
        self.add_item(DeleteTicketButton())
        self.add_item(LockTicketButton())
        self.add_item(UnlockTicketButton())
      import io
import html

# ==========================
# Add User Button
# ==========================

class AddUserButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Add User",
            emoji="➕",
            style=discord.ButtonStyle.success,
            custom_id="ticket_add_user"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "ℹ️ Use the `/ticket add @user` command to add a member to this ticket.",
            ephemeral=True
        )


# ==========================
# Remove User Button
# ==========================

class RemoveUserButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Remove User",
            emoji="➖",
            style=discord.ButtonStyle.secondary,
            custom_id="ticket_remove_user"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "ℹ️ Use the `/ticket remove @user` command to remove a member from this ticket.",
            ephemeral=True
        )


# ==========================
# Transcript Button
# ==========================

class TranscriptButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Transcript",
            emoji="📝",
            style=discord.ButtonStyle.primary,
            custom_id="ticket_transcript"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.defer(ephemeral=True)

        messages = []

        async for message in interaction.channel.history(
            oldest_first=True,
            limit=None
        ):

            content = html.escape(message.content or "")

            messages.append(
                f"""
<p>
<b>{html.escape(str(message.author))}</b>
({message.created_at})<br>
{content}
</p>
<hr>
"""
            )

        document = f"""
<html>
<head>
<meta charset="utf-8">
<title>Ticket Transcript</title>
</head>
<body>
<h2>{html.escape(interaction.channel.name)}</h2>
{''.join(messages)}
</body>
</html>
"""

        file = discord.File(
            io.BytesIO(document.encode("utf-8")),
            filename=f"{interaction.channel.name}.html"
        )

        await interaction.followup.send(
            "📝 Transcript generated.",
            file=file,
            ephemeral=True
)
                    class TicketView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)

        self.add_item(CreateTicketButton())
        self.add_item(CloseTicketButton())
        self.add_item(DeleteTicketButton())
        self.add_item(LockTicketButton())
        self.add_item(UnlockTicketButton())
        self.add_item(AddUserButton())
        self.add_item(RemoveUserButton())
        self.add_item(TranscriptButton())
class CreateTicketButton(discord.ui.Button):

    def __init__(self):
        super().__init__(
            label="Create Ticket",
            emoji="🎫",
            style=discord.ButtonStyle.green,
            custom_id="create_ticket"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        await interaction.response.send_message(
            "Select the type of ticket you want to create.",
            view=TicketTypeView(),
            ephemeral=True
        )
      class TicketTypeSelect(discord.ui.Select):

    def __init__(self):

        options = [

            discord.SelectOption(
                label="Support",
                emoji="🛠️",
                description="General support"
            ),

            discord.SelectOption(
                label="Billing",
                emoji="💰",
                description="Payment & Premium"
            ),

            discord.SelectOption(
                label="Report",
                emoji="🚨",
                description="Report a user"
            ),

            discord.SelectOption(
                label="Partnership",
                emoji="🤝",
                description="Server partnership"
            )

        ]

        super().__init__(
            placeholder="Choose a ticket category...",
            min_values=1,
            max_values=1,
            options=options,
            custom_id="ticket_type"
        )

    async def callback(
        self,
        interaction: discord.Interaction
    ):

        ticket_type = self.values[0]

        # Save for next step
        self.view.ticket_type = ticket_type

        await self.view.create_ticket(interaction)


class TicketTypeView(discord.ui.View):

    def __init__(self):

        super().__init__(timeout=120)

        self.ticket_type = None

        self.add_item(TicketTypeSelect())

    async def create_ticket(
        self,
        interaction: discord.Interaction
    ):

        # Ticket creation will be completed in Part 5.
        await interaction.response.send_message(
            f"✅ Creating a **{self.ticket_type}** ticket...",
            ephemeral=True
            )
      async def create_ticket(
    self,
    interaction: discord.Interaction
):

    guild = interaction.guild
    ticket_type = self.ticket_type

    async with aiosqlite.connect(DATABASE) as db:

        cursor = await db.execute(
            """
            SELECT
                category_id,
                support_role
            FROM ticket_settings
            WHERE guild_id=?
            """,
            (guild.id,)
        )

        settings = await cursor.fetchone()

    if settings is None:

        return await interaction.response.send_message(
            "❌ Ticket system is not configured.",
            ephemeral=True
        )

    category_id, support_role = settings

    category = guild.get_channel(category_id)

    if category is None:

        return await interaction.response.send_message(
            "❌ Ticket category was not found.",
            ephemeral=True
        )

    overwrites = {

        guild.default_role: discord.PermissionOverwrite(
            view_channel=False
        ),

        interaction.user: discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            attach_files=True,
            read_message_history=True
        )

    }

    staff_role = guild.get_role(support_role)

    if staff_role:

        overwrites[staff_role] = discord.PermissionOverwrite(
            view_channel=True,
            send_messages=True,
            manage_messages=True
        )

    channel = await guild.create_text_channel(
        name=f"{ticket_type.lower()}-{interaction.user.name}",
        category=category,
        overwrites=overwrites
    )

    embed = discord.Embed(
        title=f"🎫 {ticket_type} Ticket",
        color=0x8A2BE2
    )

    embed.description = (
        f"Welcome {interaction.user.mention}!\n\n"
        "A staff member will assist you shortly."
    )

    embed.add_field(
        name="Ticket Type",
        value=ticket_type,
        inline=True
    )

    embed.add_field(
        name="Status",
        value="🟢 Open",
        inline=True
    )

    embed.add_field(
        name="Created By",
        value=interaction.user.mention,
        inline=False
    )

    if staff_role:

        ping = await channel.send(staff_role.mention)

        try:
            await ping.delete(delay=5)
        except Exception:
            pass

    await channel.send(
        embed=embed,
        view=TicketView()
    )

    await interaction.response.send_message(
        f"✅ Your **{ticket_type}** ticket has been created!\n{channel.mention}",
        ephemeral=True
      )
