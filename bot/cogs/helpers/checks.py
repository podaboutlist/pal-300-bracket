import discord
import logging
from discord import app_commands


logger = logging.getLogger(__name__)


# discord.ext.commands.is_owner() already exists but doesn't seem to work for
# app commands. shrug
def is_owner():
	async def predicate(interaction: discord.Interaction) -> bool:
		"""Check if a user owns the bot. Used as a permission gate for some commands."""
		if await interaction.client.is_owner(interaction.user):
			logger.info(f'is_owner(): allowing {interaction.user.name} to run /{interaction.command.name}')
			return True
		else:
			logger.warning(f'is_owner(): {interaction.user.name}  access to /{interaction.command.name}')
			return False
	return app_commands.check(predicate)
