import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from .checks.owner_only import owner_only

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class Ping(commands.Cog):
	def __init__(self, bot: commands.Bot) -> None:
		self.bot = bot

		logger.debug("cog initialized")

	@commands.command(name="ping")
	@commands.is_owner()
	async def txt_ping(self, ctx: commands.Context) -> None:
		await ctx.reply("pong!")

	@app_commands.command(name="ping", description="Test if the bot is working!")
	@owner_only()
	async def cmd_ping(self, interaction: discord.Interaction) -> None:
		await interaction.response.send_message("pong!")

	@cmd_ping.error
	async def cmd_ping_handler(
		self,
		interaction: discord.Interaction,
		error: app_commands.AppCommandError,
	) -> None:
		if isinstance(error, app_commands.errors.CheckFailure):
			await interaction.response.send_message(
				":no_entry: You don't have permission to do that!",
				ephemeral=True,
			)
