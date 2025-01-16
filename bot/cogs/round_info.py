import logging
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

logger = logging.getLogger(__name__)


# TODO: Might wanna move all the logic for traversing my insane weird data
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
	def __init__(self, bot):
		self.bot = bot

		if type(self.bot._tourney_data) is not dict:
			logger.warning(f"self.bot._tourney_data is {type(self.bot._tourney_data)}!")

		if type(self.bot._episode_data) is not dict:
			logger.warning(f"self.bot._tourney_data is {type(self.bot._episode_data)}!")

	@app_commands.command(
		name="round_info", description="Display info about a round in the bracket",
	)
	@app_commands.rename(round_id="round_number")
	@app_commands.describe(round_id="A specific round to inspect")
	async def cmd_round_info(
		self,
		interaction: discord.Interaction,
		round_id: Optional[app_commands.Range[int, 1, 141]] = None,
	):
		if not round_id:
			await interaction.response.send_message("not implemented yet", ephemeral=True)
			return

		round_info = find_key_nonrecursive(self.bot._tourney_data, str(round_id))
		winner_id = round_info["winner"]

		if winner_id == -1:
			await interaction.response.send_message(f"Round {round_id} doesn't have a winner yet!")
		else:
			winner = self.bot._episode_data[str(winner_id)]

			# TODO: turn this into a cool embed or whatever
			msg = (
				f"### __Info for Round {round_id}__\n"
				f"Winner: Episode {winner['episode']} - [{winner['title']}]({winner['link']})\n"
				f"-# [_Click here to see the bracket online!_](https://bracket.podaboutli.st/#round-{round_id})"
			)

			await interaction.response.send_message(msg, suppress_embeds=True)
