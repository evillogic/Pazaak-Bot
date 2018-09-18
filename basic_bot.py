import discord
from discord.ext import commands
import random
import re
import json
import copy

description = '''An example bot to showcase the discord.ext.commands extension
module.

There are a number of utility commands being showcased here.'''
board = "```\n  Pazaak Table\npOne  {0}   {1}  pTwo\n{4} {5} {6} {2}   {3} {13} {14} {15}\n{7} {8} {9}       {16} {17} {18}\n{10} {11} {12}       {19} {20} {21}\n```"
bot = commands.Bot(command_prefix='?', description=description)

#Players
playerOne = None
playerTwo = None
#The sum on each round
sumOne = 0
sumTwo = 0
#Number of rounds won
scoreOne = 0
scoreTwo = 0
#Used for displaying board
lBoard = [0,0,0,0,0,0,0,0,0]
rBoard = [0,0,0,0,0,0,0,0,0]
turn = None
lTurnNum = 0
rTurnNum = 0
winner = None
gameChannel = None
playerData = json.load(open('playerdata.json'))
cardData = json.load(open('carddata.json'))

@bot.event
async def on_ready():
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
	
@bot.command()
async def add(left : int, right : int):
    """Adds two numbers together."""
    await bot.say(left + right)

@bot.command()
async def roll(dice : str):
    """Rolls a dice in NdN format."""
    try:
        rolls, limit = map(int, dice.split('d'))
    except Exception:
        await bot.say('Format has to be in NdN!')
        return

    result = ', '.join(str(random.randint(1, limit)) for r in range(rolls))
    await bot.say(result)

@bot.command(description='For when you wanna settle the score some other way')
async def choose(*choices : str):
    """Chooses between multiple choices."""
    await bot.say(random.choice(choices))

@bot.command()
async def repeat(times : int, content='repeating...'):
    """Repeats a message multiple times."""
    for i in range(times):
        await bot.say(content)

@bot.command()
async def joined(member : discord.Member):
    """Says when a member joined."""
    await bot.say('{0.name} joined in {0.joined_at}'.format(member))

@bot.group(pass_context=True)
async def cool(ctx):
    """Says if a user is cool.

    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await bot.say('No, {0.subcommand_passed} is not cool'.format(ctx))

@cool.command(name='bot')
async def _bot():
    """Is the bot cool?"""
    await bot.say('Yes, the bot is cool.')

@bot.command(pass_context=True)
async def create(ctx):
	"""Create a Pazaak game."""
	global playerOne, gameChannel
	if playerOne is not None:
		await bot.say("Someone is already at the table!")
		return
	playerOne = ctx.message.author
	gameChannel = ctx.message.channel
	await bot.say("{0} is waiting for another player!".format(playerOne))

@bot.command(pass_context=True)
async def join(ctx):
	"""Join the Pazaak game."""
	global playerOne
	global playerTwo
	if playerOne is None:
		await bot.say("There is no open game!")
		return
	#Add playerOne is not playerTwo
	if playerTwo is not None:
		await bot.say("There is already a game underway!")
		return
	playerTwo = ctx.message.author
	await bot.say("{0} approaches!".format(playerTwo))
	await bot.say("Game Start!")
	await initGame()
	
async def initGame():
	#read playerdata.json
	global playerOne, playerTwo, turn
	if playerOne not in playerData["players"]:
		await setupPlayer(playerOne)
	if playerTwo not in playerData["players"]:
		await setupPlayer(playerTwo)
	await bot.send_message(playerOne, "No sidedeck!")
	await bot.send_message(playerTwo, "No sidedeck!")
	turn = playerOne
	await incGame()

async def incGame():
	global gameChannel, turn, sumOne, sumTwo, lTurnNum, rTurnNum
	#instructionSet[instruction]()
	#Erase Board
	#Print Board
	
	num = random.randint(1,10)
	if turn is playerOne:
		lBoard[lTurnNum] = num
		sumOne += num
	else:
		rBoard[rTurnNum] = num
		sumTwo += num
		
	await bot.send_message(gameChannel, board.format(scoreOne, scoreTwo, sumOne, sumTwo, *lBoard, *rBoard))
	#await bot.send_message(gameChannel, board.format(scoreOne, scoreTwo, sumOne, sumTwo, lBoard[0],  lBoard[1], lBoard[2], lBoard[3], lBoard[4], lBoard[5], lBoard[6], lBoard[7], lBoard[8]))
	#await bot.say("{0} is the winner!".format(winner))
	#PlayerOne = None
	#PlayerTwo = None
	return

@bot.event
async def on_message(message):
	#using bot.event overrides default process_commands, so we call it here
	await bot.process_commands(message)
	global playerOne, playerTwo, gameChannel, turn, lTurnNum, rTurnNum
	#running?
	#if playerTwo is None or message.author not in [playerOne, playerTwo]:
	#if playerTwo is None or message.author != playerOne or message.author != playerTwo:
	#	return
	if message.author is not turn:
		return
	pattern = "[+-][1-6]"
	if re.match(pattern, message.content) is None:
		return
	#CHANGE to find()
	clist = re.findall("[+-][1-6]", message.content)
	
	#check if user has card
	global sumOne, sumTwo, scoreOne, scoreTwo
	if turn is playerOne:
		sumOne = eval(str(sumOne)+clist[0])
		turn = playerTwo
		lTurnNum += 1
		lBoard[lTurnNum] = clist[0]
		lTurnNum += 1
	else:
		sumTwo = eval(str(sumTwo)+clist[0])
		turn = playerOne
		rTurnNum += 1
		rBoard[rTurnNum] = clist[0]
		rTurnNum += 1
	
	await bot.send_message(gameChannel, "Valid input")
	await incGame()
	
@bot.command()
async def hardreset():
	global playerOne, playerTwo
	playerOne = None
	playerTwo = None
	global sumOne, sumTwo, scoreOne, scoreTwo
	sumOne = 0
	sumTwo = 0
	scoreOne = 0
	scoreTwo = 0
	
async def setupPlayer(player):
	global playerData
	for f in playerData["players"]:
		#fred = json.load(str(f))
		print(type(f))
		if(f["ID"] == "Example"):
			print("yes")
	fred = copy.copy(playerData["players"][0])
	fred["ID"] = player.id
	fred["Name"] = player.name
	playerData["players"].append(fred)
	#fred = playerData["players"]["Example"]
	#print(fred)
	#playerData["players"].append(player.id)
	#playerData["players"][player.id].append
	
@bot.command(pass_context=True)
async def save(ctx):
	global playerData
	print(playerData)
	with open('playerdata.json', 'w') as outfile:
		json.dump(playerData, outfile, sort_keys = True, indent = 4, ensure_ascii = False)

bot.run(playerData['token'])