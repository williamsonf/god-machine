'''
Created on Jun 16, 2021

@author: Fred
'''
import os
from dotenv import load_dotenv
from discord.ext import commands
from bot_commands import initialize_commands
load_dotenv()

if __name__ == '__main__':
    bot = commands.Bot(command_prefix='!')
    initialize_commands(bot)
    
    @bot.event
    async def on_ready(): #on_ready runs when the bot has connected.
        print('Bot initialized as {}, ID: {}.'.format(bot.user, bot.user.id))        

    bot.run(os.environ.get('DISCORD_API_KEY'))