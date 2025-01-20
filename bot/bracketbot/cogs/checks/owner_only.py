import logging
import os

import discord
from discord import app_commands

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


# TODO (audrey): figure out what this returns instead of 'any'
def owner_only() -> any:
	async def predicate(interaction: discord.Interaction) -> bool:
		"""Check if a user owns the bot. Used as a permission gate for some commands."""
		if await interaction.client.is_owner(interaction.user):
			logger.debug(
				"is_owner(): allowing @%s to run /%s",
				interaction.user.name,
				interaction.command.name,
			)
			return True

		logger.debug(
			"is_owner(): %s denied access to /%s",
			interaction.user.name,
			interaction.command.name,
		)
		return False

	return app_commands.check(predicate)
