import json
import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class BracketBot(commands.Bot):
	def __init__(self) -> None:
		intents = discord.Intents.default()
		intents.message_content = True

		super().__init__(
			command_prefix=commands.when_mentioned_or("b."),
			intents=intents,
			owner_ids=self.get_owner_ids(),
			allowed_contexts=app_commands.AppCommandContext(guild=True, private_channel=False),
			allowed_installs=app_commands.AppInstallationType(guild=True, user=False),
			# TODO (audrey): Add description/help command
			description=None,
			help_command=None,
		)

		self._data_file_folder = os.path.relpath(os.path.join(os.getcwd(), "..", "data"))

		self.read_tourney_data_file()
		self.read_episode_data_file()

	@property
	def tourney_data(self) -> dict:
		return self._tourney_data

	@property
	def episode_data(self) -> dict:
		return self._episode_data

	def get_owner_ids(self) -> list[int]:
		return list(map(int, os.getenv("BOT_OWNERS").split(",")))

	def read_tourney_data_file(self) -> None:
		structure_file = os.path.join(self._data_file_folder, "structure.json")
		logger.debug("Loading tournament data from %s ...", structure_file)

		with open(structure_file, encoding="utf8") as sj:
			self._tourney_data = json.load(sj)
			logger.debug("Tournament data loaded.")

	def read_episode_data_file(self) -> None:
		episodes_file = os.path.join(self._data_file_folder, "episodes.json")
		logger.debug("Loading episode data from %s ...", episodes_file)

		with open(episodes_file, encoding="utf8") as ej:
			self._episode_data = json.load(ej)
			logger.debug("Episode data loaded.")

	# We're only present in one guild so just sync commands on startup
	async def setup_hook(self) -> None:
		guild_id = int(os.getenv("GUILD_ID"))
		target_guild = await self.fetch_guild(guild_id)

		logger.debug("Syncing commands to %s (%s)...", target_guild.name, target_guild.id)

		self.tree.copy_global_to(guild=target_guild)
		await self.tree.sync(guild=target_guild)

		logger.info("Commands synced to %s (%s).", target_guild.name, target_guild.id)
