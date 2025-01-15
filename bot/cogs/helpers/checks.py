import discord
from discord import app_commands

# discord.ext.commands.is_owner() already exists but doesn't seem to work for
# app commands. shrug
def is_owner():
	async def predicate(interaction: discord.Interaction) -> bool:
		"""Check if a user owns the bot. Used as a permission gate for some commands."""
		if await interaction.client.is_owner(interaction.user):
			print(f'[is_owner] allowing {interaction.user.name} to run /{interaction.command.name}')
			return True
		else:
			print(f'[is_owner] {interaction.user.name} denied access to /{interaction.command.name}')
			return False
	return app_commands.check(predicate)
