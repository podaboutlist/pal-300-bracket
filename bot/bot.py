#!/usr/bin/env python3

import discord
import json
import os
import sys
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv
from typing import Optional


load_dotenv()

for env_var in ['DISCORD_TOKEN', 'GUILD_ID', 'BOT_OWNERS']:
	if not os.getenv(env_var):
		print(f'ERROR: No value found in ${env_var}! Did you edit .env or compose.yaml?')
		sys.exit(1)


TOURNEY_DATA = None
EPISODE_DATA = None

with open('../data/structure.json', 'r', encoding='utf8') as sj:
	TOURNEY_DATA = json.load(sj)

with open('../data/episodes.json', 'r', encoding='utf8') as ej:
	EPISODE_DATA = json.load(ej)


# https://stackoverflow.com/a/65418112
def find_key_nonrecursive(adict: dict, key: any) -> any:
	stack = [adict]
	while stack:
		d = stack.pop()

		if type(d) is list or type(d) is int:
			continue

		if key in d:
			return d[key]
		for v in d.values():
			if isinstance(v, dict):
				stack.append(v)
			if isinstance(v, list):
				stack += v


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
@is_owner()
@app_commands.allowed_contexts(app_commands.AppCommandContext(private_channel=False))
async def cmd_ping(interaction: discord.Interaction):
		await interaction.response.send_message('pong!')


@cmd_ping.error
async def cmd_ping_handler(interaction: discord.Interaction, error: app_commands.AppCommandError):
	if isinstance(error, app_commands.errors.CheckFailure):
		await interaction.response.send_message(":no_entry: You don't have permission to do that!", ephemeral=True)


@bot.tree.command(name='round', description='Display info about a round in the bracket')
@app_commands.rename(round_id='round_number')
@app_commands.describe(round_id='A specific round to inspect')
async def cmd_round_info(
	interaction: discord.Interaction,
	round_id: Optional[app_commands.Range[int, 1, 141]] = None
):
	if not round_id:
		await interaction.response.send_message('not implemented yet', ephemeral=True)
		return

	round_info = find_key_nonrecursive(TOURNEY_DATA, str(round_id))
	winner_id = round_info['winner']

	if winner_id == -1:
		await interaction.response.send_message(f"Round {round_id} doesn't have a winner yet!")
	else:
		winner = EPISODE_DATA[str(winner_id)]

		# TODO: turn this into a cool embed or whatever
		msg = (
			f"### __Info for Round {round_id}__\n"
			"Winner: " + f"Episode {winner['episode']} - [{winner['title']}]({winner['link']})\n"
			f"-# [_Click here to see the bracket online!_](https://bracket.podaboutli.st/#round-{round_id})"
		)

		await interaction.response.send_message(msg, suppress_embeds=True)


if __name__ == '__main__':
	bot.run(os.getenv('DISCORD_TOKEN'))
