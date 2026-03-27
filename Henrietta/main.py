import os
from dotenv import load_dotenv
load_dotenv()

import discord
from discord.ext import commands
import aiomysql

from mod import set_bot as set_warn_bot, mod_group
from log import setup_logging
# from funwarns import setup_funwarns
from automod import setup_automod

import tickets
from tickets import (
    ticket_group,
    set_bot as set_ticket_bot,
    TicketPanelView,
    CloseTicketView,
    ConfirmCloseView,
)


class Client(commands.Bot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.pool = None

    async def setup_hook(self):
        self.pool = await aiomysql.create_pool(
            host=os.getenv("DB_HOST"),
            port=int(os.getenv("DB_PORT", 3306)),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            db=os.getenv("DB_NAME"),
            autocommit=True,
        )

        # Ticket system setup
        set_ticket_bot(self)
        self.add_view(TicketPanelView())
        self.add_view(CloseTicketView())
        self.add_view(ConfirmCloseView())

        # Other bot systems
        # setup_funwarns(self)
        self.tree.add_command(mod_group)
        self.tree.add_command(ticket_group)

        await self.tree.sync()

    async def on_ready(self):
        print(f"Logged on as {self.user}")


intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.voice_states = True

bot = Client(command_prefix="?", intents=intents)

set_warn_bot(bot)
setup_logging(bot)
setup_automod(bot)

bot.run(os.getenv("DISCORD_TOKEN"))
