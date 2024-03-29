import discord
import bot_commands
import settings as settings

client = discord.Client()
import usage

# when bot is ready to be used
@client.event
async def on_ready():
	print('We have logged in as {0.user}'.format(client))

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
			print(f'Running command {command.invocation}')
			return await command.invoke(client, message)
	print(f'Command not found: {message.content}')

	# if starts with command but not sure what
	return await message.channel.send("Command detected, but it doesn't match what I know. Try $help to list them.")

def run_discordbot(API_TOKEN):
	client.run(API_TOKEN)
