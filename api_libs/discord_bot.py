import discord
import bot_commands
import settings as settings
import logging

client = discord.Client()
import usage

logger = logging.getLogger(__name__)

# when bot is ready to be used
@client.event
async def on_ready():
	logger.info("We have logged in as %s", client.user)

# gets a message
@client.event
async def on_message(message):
	# don't do anything if it's from us
	if message.author == client.user:
		return

	# not a bot command
	if not message.content.startswith('$'):
		return

	# finds the first command that matches
	for command in bot_commands.COMMANDS:
		if command.matches(message.content):
			logger.info("Running command %s", command.invocation)
			return await command.invoke(client, message)
	logger.warning("Command not found: %s", message.content)

	# if starts with command but not sure what
	return await message.channel.send("Command detected, but it doesn't match what I know. Try $help to list them.")

def run_discordbot(API_TOKEN):
	client.run(API_TOKEN)
