import settings as settings
import google_api
import usage
import logging

logger = logging.getLogger(__name__)

gDrive = google_api.GoogleDriveAPI()

def convert_to_server_friendly_name(title):
	title = [c if (c.isalnum() or c == ' ') else '' for c in list(title)] # strip nonalphanumeric
	title = ['-' if c == ' ' else c for c in title] # convert spaces to dashes
	title = ''.join(title)
	if len(title) < 1:
		raise NameError('Must provide a name that has some alphanumeric characters')
	return title

def get_puzzle_announcements_channel(client):
	return client.get_channel(int(settings.DISCORD_PUZZLEANNOUNCE_CHANNEL))

# here commences all the commands
async def new_puzzle(client, message):
	msg_bits = message.content.split(' ')
	# check for insufficient data
	if len(msg_bits) < 2:
		return await message.channel.send('Not enough info sent. Please specify a name and url starting with http(s) or enclosed in brackets.')

	# extract url
	msg_url = msg_bits[-1]
	if not (msg_url.startswith('http') or msg_url.startswith('<')):
		msg_url = ''
		puzzle_name = ' '.join(msg_bits[1:])
		if puzzle_name.startswith('"'):
			puzzle_name = puzzle_name[1:-1] # trim "" if provided
		await message.channel.send("No url found, fine. Add it later on the spreadsheet if applicable.\nMaking spreadsheet for puzzle **" + puzzle_name + "**")
	else:
		if msg_url.startswith('<'):
			msg_url = msg_url[1:-1]  # strip brackets from url
		puzzle_name = ' '.join(msg_bits[1:-1])
		if puzzle_name.startswith('"'):
			puzzle_name = puzzle_name[1:-1] # trim "" if provided
		await message.channel.send("Making spreadsheet for puzzle **{0}** at url: <{1}>".format(puzzle_name, msg_url))

	# Make a new discord Channel in the right category
	server_friendly_name = convert_to_server_friendly_name(puzzle_name)

	puzzCategory = client.get_channel(int(settings.DISCORD_PUZZLE_CATEGORY))
	new_channel = await message.guild.create_text_channel(server_friendly_name, category=puzzCategory)

	sheet_url = gDrive.make_sheet(puzzle_name, msg_url)

	# Update new discord channel with data
	await new_channel.edit(topic=sheet_url, reason='Made new channel')
	await new_channel.send("Your sheet is now available at: <" + sheet_url + ">\nThe puzzle can be found at <" + msg_url + ">" + "\n" +
		"Please update this channel with puzzle type and topic at your earliest convenience.")

	await message.channel.send("New puzzle created. See channel <#{0}> for details".format(new_channel.id))
	return await get_puzzle_announcements_channel(client).send("New puzzle **{0}** created in <#{1}>".format(puzzle_name, new_channel.id))

async def solve_puzzle(client, message):
	await message.channel.send('Solved puzzle request detected!')

	answer = ' '.join(message.content.split(' ')[1:]).upper()
	puzzle_name = message.channel

	# Get the spreadsheet url from the channel topic
	sheet_url = message.channel.topic # we hope nobody changed it
	if sheet_url is None or sheet_url == '':
		await message.channel.send('Unable to detect spreadsheet url, please move spreadsheet manually')
	else: # Move the spreadsheet to the SOLVED folder
		puzzle_name = gDrive.solve_sheet(sheet_url, answer);
	# Move the discord channel to the ARCHIVED category

	archiveCategory = client.get_channel(int(settings.DISCORD_ARCHIVE_CATEGORY))
	await message.channel.edit(category=archiveCategory)
	await message.channel.send('Puzzle **{0}** solved with answer {1}!'.format(puzzle_name, answer));

	# Announce in the general channel that a puzzle has been solved!
	announce_channel = get_puzzle_announcements_channel(client)
	return await announce_channel.send('Puzzle **{0}** solved with answer {1}!'.format(puzzle_name, answer));

async def datamodel(client, message):
	return await message.channel.send(usage.DATA_MODEL)

async def debug_info(client, message):
	logger.debug(
		"debug_info channel=%s category=%s guild=%s content=%s",
		message.channel,
		message.channel.category,
		message.guild,
		message.content,
	)
	return await message.channel.send('channel: {0}, category: {1}'.format(message.channel, message.channel.category))

PUBLIC_COMMANDS = [
	usage.Command("$new_puzzle", "Makes a new puzzle spreadsheet and channel. Format '$new_puzzle Name Of Puzzle <http(s)://puzzle_link>', link optional", new_puzzle),
	usage.Command("$solve_puzzle", "Solves the puzzle and archives the current channel and spreadsheet in the description. Format '$solve_puzzle answer' in the relevant channel", solve_puzzle),
	usage.Command("$datamodel", "Describes the data model and how to do the bot functions if the bot is down", datamodel),
]

async def help_cmd(client, message):
	return await message.channel.send('\n'.join([c.display() for c in PUBLIC_COMMANDS]))

HIDDEN_COMMANDS = [
	usage.Command("$new", "Same as $new_puzzle", new_puzzle),
	usage.Command("$add_puzzle", "Same as $new_puzzle", new_puzzle),
	usage.Command("$answer", "Same as $solve_puzzle", solve_puzzle),
	usage.Command("$solve", "Same as $solve_puzzle", solve_puzzle),
	usage.Command("$datamodel", "Describes the data model and how to do the bot functions if the bot is down", datamodel),
	usage.Command("$debug_info", "Lists debug info", debug_info),
	usage.Command("$help", "Lists public commands", help_cmd),
]

COMMANDS = PUBLIC_COMMANDS + HIDDEN_COMMANDS

