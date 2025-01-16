import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from bracketbot.bracketbot import BracketBot

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


# TODO (audrey): Might wanna move all the logic for traversing my insane weird data
# structure to its own class/file
# https://stackoverflow.com/a/65418112
def find_key_nonrecursive(the_dict: dict, key: any) -> any:
	stack = [the_dict]
	while stack:
		d = stack.pop()

		# python gets angry when we try to iterate over these
		if type(d) is list or type(d) is int:
			continue

		if key in d:
			return d[key]
		for v in d.values():
			if isinstance(v, dict):
				stack.append(v)
			if isinstance(v, list):
				stack += v

	return None


class RoundInfo(commands.Cog):
	def __init__(self, bot: BracketBot) -> None:
		self.bot = bot

		logger.debug("cog initialized")

	@app_commands.command(
		name="round_info",
		description="Display info about a round in the bracket",
	)
	@app_commands.rename(round_id="round_number")
	@app_commands.describe(round_id="A specific round to inspect")
	async def cmd_round_info(
		self,
		interaction: discord.Interaction,
		round_id: app_commands.Range[int, 1, 141] | None = None,
	) -> None:
		if not round_id:
			logger.debug("Looking up information for the current round...")
			await interaction.response.send_message("not implemented yet", ephemeral=True)
			return

		round_key = str(round_id)

		logger.debug("Looking up info for round %s", round_key)

		round_info = find_key_nonrecursive(self.bot.tourney_data, round_key)
		winner_id = round_info["winner"]

		if winner_id == -1:
			await interaction.response.send_message(f"Round {round_key} doesn't have a winner yet!")
		else:
			winner = self.bot.episode_data[str(winner_id)]

			# TODO (audrey): send a cool embed instead of whatever this is

			msg = (
				f"### __Info for Round {round_key}__\n"
				f"Winner: Episode {winner['episode']} - [{winner['title']}]({winner['link']})\n"
				f"-# [_Click here to see the bracket online!_](https://bracket.podaboutli.st/#round-{round_id})"
			)

			await interaction.response.send_message(msg, suppress_embeds=True)
