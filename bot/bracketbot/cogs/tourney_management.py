import json
import logging
import os
from datetime import datetime

import discord
import git
from discord import app_commands
from discord.ext import commands

from bracketbot.bracketbot import BracketBot
from bracketbot.helpers import find_key_nonrecursive

from .checks.owner_only import owner_only

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOG_LEVEL", "INFO"))


class TourneyManager(commands.Cog):
	git_group = app_commands.Group(
		name="git",
		description="Manage the back-end data",
		guild_only=True,
	)

	bracket_group = app_commands.Group(
		name="bracket",
		description="Manage the PAL tournament",
		guild_only=True,
	)

	def __init__(self, bot: BracketBot) -> None:
		self.bot = bot

		self._repo_dir = os.path.join(os.getcwd(), "bracket_repo")
		self._repo_url = os.getenv("REPO_URL")
		self._repo = None

		self._ssh_keyfile = os.path.normpath(os.getenv("SSH_KEYFILE"))
		self._ssh_keypass = os.getenv("SSH_KEYPASS")

		self._git_cmd = f"ssh -i {self._ssh_keyfile}"

		self.__setup_repo()
		self._git_user = git.Actor(os.getenv("GIT_USER"), os.getenv("GIT_EMAIL"))
		# HACK (audrey): this is a stupid way of doing this but whatever
		self._git_authors = {
			143123353249513472: git.Actor("Audrey", "6566104+RalphORama@users.noreply.github.com"),
			208347530902110219: git.Actor("emptyvezzel", "murph.jack97@gmail.com"),
		}

		self._episodes_file = os.path.join(self._repo_dir, "data", "episodes.json")
		self._structure_file = os.path.join(self._repo_dir, "data", "structure.json")

		logger.debug("cog initialized")

		self.__read_data_from_repo()

	@property
	def repo_dir(self) -> str:
		return self._repo_dir

	@property
	def repo_url(self) -> str:
		return self._repo_url

	def __setup_repo(self) -> None:
		logger.debug("Setting up git repo...")

		if not os.path.isdir(self.repo_dir):
			logger.debug("Cloning repo: %s -> %s", self.repo_url, self.repo_dir)

			with git.Git().custom_environment(GIT_SSH_COMMAND=self._git_cmd):
				self._repo = git.Repo.clone_from(self.repo_url, self.repo_dir)
		else:
			logger.debug("Repo already exists: %s", self.repo_dir)
			self._repo = git.Repo(self.repo_dir)
			# TODO (audrey): This throws an error and prevents startup if there are conflicts
			self._repo.remotes.origin.pull()
			logger.debug("Existing repo state: %s", "DIRTY" if self._repo.is_dirty() else "clean")

	def __fetch_remote(self) -> bool:
		self._repo.remotes.origin.fetch(kill_after_timeout=10)
		return self._repo.head.object.hexsha == self._repo.refs["main"].object.hexsha

	def __pull_remote(self) -> None:
		self._repo.remotes.origin.pull(kill_after_timeout=10)

	def __push_commits(self) -> bool:
		with git.Git().custom_environment(GIT_SSH_COMMAND=self._git_cmd):
			push = self._repo.remotes.origin.push(kill_after_timeout=10)
			push.raise_if_error()

	def __read_data_from_repo(self) -> None:
		logger.debug("Reading episode data from cloned repo...")
		self.bot.read_episode_data_file(data_file=self._episodes_file)
		self.bot.read_tourney_data_file(data_file=self._structure_file)

	def __write_data_to_repo(self, *, filename: str) -> bool:
		if filename == "episodes.json":
			logger.info("Writing bot.episode_data to %s", self._episodes_file)
			with open(self._episodes_file, "w", encoding="utf8") as ep_file:
				json.dump(
					self.bot.episode_data,
					ep_file,
					allow_nan=False,
					indent="\t",
					ensure_ascii=False,
				)
				# Add a newline like VS Code also does
				ep_file.write("\n")
				return True
		elif filename == "structure.json":
			logger.info("Writing bot.tourney_data to %s", self._structure_file)
			with open(self._structure_file, "w", encoding="utf8") as td_file:
				json.dump(
					self.bot.tourney_data,
					td_file,
					allow_nan=False,
					indent="\t",
					ensure_ascii=False,
				)
				# Add a newline like VS Code
				td_file.write("\n")
				return True
		else:
			logger.error("__write-data_to_repo called with incorrect filename %s", filename)
			return False

	def __create_commit(self, *, author: int) -> None:
		if not self._repo.is_dirty():
			logger.debug("__create_commit() called but repo isn't dirty.")
			return

		logger.debug(
			"Attempting to commit %s/data/ (current HEAD SHA is %s)...",
			self._repo_dir,
			self._repo.head.object.hexsha,
		)

		commit_author = self._git_authors[author]

		self._repo.index.add(os.path.join(self._repo_dir, "data"), write=True)
		self._repo.index.commit(
			"[bracketbot] update tournament data files",
			# TODO (audrey): maybe make this reference which account is committing?
			author=commit_author,
			committer=self._git_user,
			# commit_date=datetime.now(time.tzname[time.daylight]),
			commit_date=datetime.now().astimezone(),
		)

		logger.debug("Created commit! New HEAD SHA is %s", self._repo.head.object.hexsha)

	@git_group.command(name="fetch", description="runs git fetch")
	@owner_only()
	async def cmd_git_fetch(self, interaction: discord.Interaction) -> None:
		await interaction.response.send_message("running `git fetch`...", ephemeral=True)
		om = await interaction.original_response()

		is_synced = self.__fetch_remote()

		new_msg = (
			":white_check_mark: `git fetch` succeeded!\n\n"
			f"- `is_synced`: {is_synced}\n"
			f"- local HEAD: `{self._repo.head.object.hexsha[:7]}`\n"
			f"- remote HEAD: `{self._repo.refs['main'].object.hexsha[:7]}`\n"
		)

		await om.edit(content=new_msg)

	@git_group.command(name="pull", description="pulls upstream changes")
	@owner_only()
	async def cmd_git_pull(self, interaction: discord.Interaction) -> None:
		await interaction.response.send_message("Pulling upstream changes...", ephemeral=True)
		om = await interaction.original_response()

		self.__pull_remote()

		await om.edit(content=":white_check_mark: successfully pulled latest changes!")

	@git_group.command(name="commit", description="commits changes in the data directory")
	@owner_only()
	async def cmd_git_commit(self, interaction: discord.Interaction) -> None:
		await interaction.response.send_message("Committing changes...", ephemeral=True)
		om = await interaction.original_response()

		self.__write_data_to_repo(filename="episodes.json")
		self.__write_data_to_repo(filename="structure.json")

		if not self._repo.is_dirty():
			await om.edit(content=":warning: No files changed on disk!")
			return

		self.__create_commit(author=interaction.user.id)

		new_msg = (
			":white_check_mark: Created a new commit!\n\n"
			f"- HEAD SHA: `{self._repo.head.object.hexsha[:7]}`\n"
			f"- Author: {self._repo.head.object.author}\n"
			f"- Committer: {self._repo.head.object.committer}\n"
		)

		await om.edit(content=new_msg)

	@bracket_group.command(name="set_winner", description="Declare a winner for a bracket")
	@app_commands.rename(round_id="round")
	@app_commands.describe(round_id="Declare a winner for this round")
	@app_commands.describe(winner="The episode that won the round")
	@owner_only()
	async def set_winner_cmd(
		self,
		interaction: discord.Interaction,
		round_id: app_commands.Range[int, 1, 141],
		# TODO (audrey): Create an autocomplete function based on entries in the round
		winner: app_commands.Range[int, 1, 302],
	) -> None:
		await interaction.response.send_message("not implemented yet.", ephemeral=True)
