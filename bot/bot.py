#!/usr/bin/env python3

import discord
import json
import os
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv


load_dotenv()

for env_var in ['DISCORD_TOKEN', 'GUILD_ID', 'BOT_OWNERS']:
	if not os.getenv(env_var):
		raise RuntimeError(f"No value found in ${env_var}! Did you edit .env/compose.yaml?")


class BracketBot(commands.Bot):
	# We're only present in one guild so just sync commands on startup
	async def setup_hook(self):
		guild_id = int(os.getenv('GUILD_ID'))
		target_guild = await self.fetch_guild(guild_id)

		print(f'> Syncing commands to {target_guild.name} ({target_guild.id})...')

		self.tree.copy_global_to(guild=target_guild)
		await self.tree.sync(guild=target_guild)

		print(f'> Commands synced to {target_guild.name} ({target_guild.id})!')


def get_owner_ids() -> list[int]:
	return list(map(int, os.getenv('BOT_OWNERS').split(',')))


async def check_is_owner(interaction: discord.Interaction) -> bool:
	"""Check if a user owns the bot. Used as a permission gate for some commands."""
	if await interaction.client.is_owner(interaction.user):
		print(f'> allowing {interaction.user.name} to run /{interaction.command.name}')
		return True
	else:
		print(f'> {interaction.user.name} denied access to /{interaction.command.name}')
		return False


intents = discord.Intents.default()
intents.message_content = True

bot = BracketBot(command_prefix='b.', intents=intents, owner_ids=get_owner_ids())


@bot.event
async def on_ready():
	print(f'> logged in as {bot.user} ({bot.user.id})')


@bot.command(name='ping')
async def txt_ping(ctx: commands.Context):
	await ctx.reply('pong!')


@bot.tree.command(name='ping', description='Test if the bot is working!')
@app_commands.allowed_contexts(app_commands.AppCommandContext(private_channel=False))
@app_commands.check(check_is_owner)
async def cmd_ping(interaction: discord.Interaction):
		await interaction.response.send_message('pong!')


@cmd_ping.error
async def cmd_ping_handler(interaction: discord.Interaction, error: app_commands.AppCommandError):
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(":no_entry: You don't have permission to do that!", ephemeral=True)


if __name__ == '__main__':
	bot.run(os.getenv('DISCORD_TOKEN'))
