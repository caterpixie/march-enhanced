import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
import aiomysql

from starboard import setup_starboard
from mod import set_bot as set_warn_bot, mod_group
from log import setup_logging
from automod import setup_automod
from tickets import (
    ticket_group,
    set_bot as set_ticket_bot,
    TicketPanelView,
    CloseTicketView,
    ConfirmCloseView,
)

GUILD_ID = 1480390027593777287

class Client(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pool = None

    async def setup_hook(self):
        # MySQL pool
        self.pool = await aiomysql.create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            autocommit=True,
        )

        set_ticket_bot(self)

        self.add_view(TicketPanelView())
        self.add_view(CloseTicketView())
        self.add_view(ConfirmCloseView())

        self.tree.add_command(mod_group)
        self.tree.add_command(ticket_group)
        
        guild = discord.Object(id=GUILD_ID)
        self.tree.copy_global_to(guild=guild)
        synced = await self.tree.sync(guild=guild)
        setup_starboard(self)

        print(f"Synced commands to guild {GUILD_ID}: {[cmd.name for cmd in synced]}")

    async def on_ready(self):
        print(f"Logged on as {self.user} (ID: {self.user.id})")
        print("Bot is ready.")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = Client(
    command_prefix="?",
    intents=intents
)

set_warn_bot(bot)
setup_logging(bot)
setup_automod(bot)


bot.run(os.getenv("DISCORD_TOKEN"))
