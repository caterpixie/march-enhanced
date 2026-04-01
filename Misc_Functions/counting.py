import discord
import asyncio
import json
import os
import random

# =========================
# CONFIGURATION
# =========================

COUNTING_CHANNEL_ID = 

LOSER_ROLE_ID = 
LOSER_ROLE_DURATION = 300 

DATA_FILE = "counting_data.json"

FINAL_MILESTONE = 3000
FUNNY_NUMBERS = [69, 420, 666, 8008]

EMBED_COLOR = ""

TRIGGER_BYPASS_MESSAGE = "!zliwpj"

# Random milestone spacing
RANDOM_MILESTONE_MIN = 25
RANDOM_MILESTONE_MAX = 75

# =========================
# BOT HOOKUP
# =========================

bot = None
current_count = 0
last_user_id = None
next_milestone = 0


def generate_next_milestone(current):
    return current + random.randint(RANDOM_MILESTONE_MIN, RANDOM_MILESTONE_MAX)


def load_count_data():
    global current_count, last_user_id, next_milestone
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    raise ValueError("Empty DATA_FILE")
                data = json.loads(content)
                current_count = data.get("current_count", 0)
                last_user_id = data.get("last_user_id", None)
                next_milestone = data.get("next_milestone", generate_next_milestone(current_count))
        except (json.JSONDecodeError, ValueError):
            print(f"Warning: {DATA_FILE} is empty or invalid. Resetting count.")
            current_count = 0
            last_user_id = None
            next_milestone = generate_next_milestone(0)
            save_count_data()
    else:
        current_count = 0
        last_user_id = None
        next_milestone = generate_next_milestone(0)
        save_count_data()


def save_count_data():
    with open(DATA_FILE, "w") as f:
        json.dump({
            "current_count": current_count,
            "last_user_id": last_user_id,
            "next_milestone": next_milestone
        }, f)


async def counting_on_message(message: discord.Message):
    global current_count, last_user_id, next_milestone

    if message.author.bot or message.channel.id != COUNTING_CHANNEL_ID:
        return

    guild = message.guild
    loser_role = guild.get_role(LOSER_ROLE_ID)

    try:
        number = int(message.content.strip())
    except ValueError:
        await message.delete()
        return

    if number == current_count + 1 and message.author.id != last_user_id:
        current_count = number
        last_user_id = message.author.id

        if current_count >= next_milestone and current_count < FINAL_MILESTONE:
            embed = discord.Embed(
                title=f"Milestone Reached: {number}",
                description=(
                    f"{message.author.mention} hit the random milestone. "
                    "Congratulations on counting again."
                ),
                color=discord.Color.from_str(EMBED_COLOR),
            )
            await message.channel.send(embed=embed)

            msg = await message.channel.send(TRIGGER_BYPASS_MESSAGE)
            await msg.delete()

            next_milestone = generate_next_milestone(current_count)

        elif number in FUNNY_NUMBERS:
            embed = discord.Embed(
                title=f"Funny Number: {number}",
                description="Nice.",
                color=discord.Color.from_str(EMBED_COLOR),
            )
            await message.channel.send(embed=embed)

            msg = await message.channel.send(TRIGGER_BYPASS_MESSAGE)
            await msg.delete()

        elif number == FINAL_MILESTONE:
            embed = discord.Embed(
                title=f"Milestone Reached: {number}",
                description=(
                    f"{message.author.mention} reached the final milestone. "
                    "This counting channel has gotten out of hand."
                ),
                color=discord.Color.from_str(EMBED_COLOR),
            )
            await message.channel.send(embed=embed)

            msg = await message.channel.send(TRIGGER_BYPASS_MESSAGE)
            await msg.delete()

        save_count_data()

    else:
        await message.delete()

        embed = discord.Embed(
            title="Counting Reset",
            description=(
                f"{message.author.mention} messed up the count at **{current_count}** and has been given the "
                f"{loser_role.mention} role! The count has been reset to **0**."
            ),
            color=discord.Color.from_str(EMBED_COLOR),
        )
        await message.channel.send(embed=embed)

        current_count = 0
        last_user_id = None
        next_milestone = generate_next_milestone(0)
        save_count_data()

        if loser_role:
            await message.author.add_roles(loser_role)
            await asyncio.sleep(LOSER_ROLE_DURATION)
            await message.author.remove_roles(loser_role)


def set_bot(bot_instance):
    global bot
    bot = bot_instance
    load_count_data()
    bot.add_listener(counting_on_message, "on_message")
