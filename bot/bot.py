#!/usr/bin/env python3

import asyncio
import json
import logging
import os
import sys

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

from cogs.ping import Ping
from cogs.round_info import RoundInfo

load_dotenv()

discord.utils.setup_logging()
logger = logging.getLogger(__name__)
# TODO: Write logic to control this with os.getenv('LOG_LEVEL')
logger.setLevel(logging.DEBUG)
# don't really need to see this CRAP!
logging.getLogger("discord.gateway").setLevel(logging.WARNING)

for env_var in ["DISCORD_TOKEN", "GUILD_ID", "BOT_OWNERS"]:
	if not os.getenv(env_var):
		logger.error("No value defined for {env_var} ! Did you edit .env or compose.yaml?", extra={
			env_var: env_var,
		})
		sys.exit(1)


def get_owner_ids() -> list[int]:
	return list(map(int, os.getenv("BOT_OWNERS").split(",")))


class BracketBot(commands.Bot):
	def __init__(self):
		intents = discord.Intents.default()
		intents.message_content = True

		super().__init__(
			command_prefix=commands.when_mentioned_or("b."),
			intents=intents,
			owner_ids=get_owner_ids(),
			allowed_contexts=app_commands.AppCommandContext(guild=True, private_channel=False),
			allowed_installs=app_commands.AppInstallationType(guild=True, user=False),
			# TODO: Add description/help command
			description=None,
			help_command=None,
		)

		self.read_tourney_data_file()
		self.read_episode_data_file()

	def read_tourney_data_file(self):
		with open("../data/structure.json", "r", encoding="utf8") as sj:
			self._tourney_data = json.load(sj)
			logger.debug("Tournament data loaded.")

	def read_episode_data_file(self):
		with open("../data/episodes.json", "r", encoding="utf8") as ej:
			self._episode_data = json.load(ej)
			logger.debug("Episode data loaded.")

	# We're only present in one guild so just sync commands on startup
	async def setup_hook(self):
		guild_id = int(os.getenv("GUILD_ID"))
		target_guild = await self.fetch_guild(guild_id)

		logger.debug(f"Syncing commands to {target_guild.name} ({target_guild.id})...")

		self.tree.copy_global_to(guild=target_guild)
		await self.tree.sync(guild=target_guild)

		logger.info(f"Commands synced to {target_guild.name} ({target_guild.id}).")


bot = BracketBot()


@bot.event
async def on_ready():
	logger.info(f"logged in as {bot.user} ({bot.user.id})")


async def main():
	async with bot:
		await bot.add_cog(Ping(bot))
		await bot.add_cog(RoundInfo(bot))
		await bot.start(os.getenv("DISCORD_TOKEN"))


if __name__ == "__main__":
	logger.debug("Firing up the bot!")
	try:
		asyncio.run(main())
	except KeyboardInterrupt:
		logger.warning("Caught Ctrl+C, exiting...")
		sys.exit(0)
