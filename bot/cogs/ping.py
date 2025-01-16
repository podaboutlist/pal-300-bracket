import discord
from discord import app_commands
from discord.ext import commands

from .helpers.checks import is_owner


class Ping(commands.Cog):
	def __init__(self, bot: commands.Bot):
		self.bot = bot

	@commands.command(name="ping")
	@commands.is_owner()
	async def txt_ping(self, ctx: commands.Context):
		await ctx.reply("pong!")

	@app_commands.command(name="ping", description="Test if the bot is working!")
	@is_owner()
	async def cmd_ping(self, interaction: discord.Interaction):
		await interaction.response.send_message("pong!")

	@cmd_ping.error
	async def cmd_ping_handler(
		self, interaction: discord.Interaction, error: app_commands.AppCommandError,
	):
		if isinstance(error, app_commands.errors.CheckFailure):
			await interaction.response.send_message(
				":no_entry: You don't have permission to do that!", ephemeral=True,
			)
