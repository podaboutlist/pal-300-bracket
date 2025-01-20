#!/usr/bin/env python3

# Ignore "import not at top of file" because we want to import and execute load_dotenv() BEOFRE
# we import any modules (otherwise LOG_LEVEL isn't properly set.)
# ruff: noqa: E402

from dotenv import load_dotenv

load_dotenv()

import asyncio
import logging
import os
import sys

import discord

# TODO (audrey): fix __init__.py lol
from bracketbot import BracketBot
from bracketbot.cogs.ping import Ping
from bracketbot.cogs.round_info import RoundInfo
from bracketbot.cogs.tourney_management import TourneyManager

discord.utils.setup_logging()
logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))
logger.info("Log level set to %s", logging.getLevelName(logger.getEffectiveLevel()))

# don't really need to see this CRAP!
logging.getLogger("discord.gateway").setLevel(logging.WARNING)


for env_var in ["DISCORD_TOKEN", "GUILD_ID", "BOT_OWNERS"]:
	if not os.getenv(env_var):
		logger.error("No value defined for %s ! Did you edit .env or compose.yaml?", env_var)
		sys.exit(1)


def get_owner_ids() -> list[int]:
	return list(map(int, os.getenv("BOT_OWNERS").split(",")))


bot = BracketBot()


@bot.event
async def on_ready() -> None:
	logger.info("logged in as %s (%s)", bot.user, bot.user.id)


async def main() -> None:
	async with bot:
		await bot.add_cog(Ping(bot))
		await bot.add_cog(RoundInfo(bot))
		await bot.add_cog(TourneyManager(bot))
		await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
	logger.info("Firing up the bot!")
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logger.warning("Caught Ctrl+C, exiting...")
		sys.exit(0)
