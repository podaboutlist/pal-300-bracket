import logging
import os

import discord
from discord import app_commands
from discord.ext import commands

from bracketbot import BracketBot
from bracketbot.helpers import find_key_nonrecursive

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


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

		round_info = find_key_nonrecursive(round_key, self.bot.tourney_data)
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
