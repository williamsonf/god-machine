'''
Created on Jun 16, 2021

@author: Fred

Methods
-------
get_sheet
    Loads a sheet from the database, identifies the associated gameline, and
    returns the character sheet object of the correct class.
    
Classes
-------
CommonActions
    Discord.py Cog containing common user actions like Roll, Score, etc.
Experience
    Discord.py Cog for commands pertaining to beats and experience
Combat 
    Discord.py Cog for commands pertaining to combat
Creation
    Discord.py Cog for Character Creation commands
Other
    Discord.py Cog for miscellaneous other character sheet commands
'''
import pymongo, os
from time import sleep
from char_sheet import mortal
from discord.ext import commands
from dotenv import load_dotenv
load_dotenv()

def get_sheet(server_id, user_id):
        mongo_client = pymongo.MongoClient(os.environ.get('DB_HOST'), int(os.environ.get('DB_PORT')))
        db = mongo_client[os.environ.get('DB_NAME')]
        collection = db[str(server_id)]
        info = collection.find_one({'user id' : user_id})
        if info == None:
            return mortal(server_id, {'user id' : user_id})
        if info['splat'] == 'mortal':
            return mortal(server_id, info)
        
class CommonActions(commands.Cog, name='01. Common Actions'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(brief='Rolls dice according to your wants.')
    async def roll(self, ctx, *args):
        '''Standard dice rolling command. Accepts skill names, attributes names,
        specialties as arguments. Specialties must be encased in parentheses in
        order to be considered.
        
        Numerical modifiers may additionally be included. Numbers on their own
        will be added. +<val> will add a value to the dice pool. -<val> will
        remove a value from the dice pool.
        
        An empty !roll command will result in a chance die.
        This function automatically accounts for and applies unskilled penalties
        to the roll.
        
        Additional Arguments:
            9again
                dice explode on 9 and above
            8again
                dice explode on 8 and above
            NoAgain
                prevents dice from exploding
            Rote
                applies rote quality to the roll
            wp
                applies +3 to the dice pool. does NOT alter your willpower
            
        Valid examples include:
        !roll Athletics (running) strength 8again rote
            This will roll your Athletics (Running) + Strength with 8again and rote.
        !roll 3
            This will roll 3 dice.
        !roll chance
            This will roll a chance die.
        !roll Jimbo pushes his stamina to the limit as he attempts to (sprint) away from the monster. It has been years since he engaged in any real athletics, but at this point, all he can do is run! wp
            This will roll Athletics (Sprint) + Stamina, with the +3 willpower bonus
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.roll_dice(args)
        await ctx.send(response)

    @commands.command(brief='Displays the character sheet. Contains optional arguments.')
    async def score(self, ctx, arg=None):
        '''Displays the character sheet. By default, as a series of messages.
        However, a single page of the character sheet may be selected instead.
        To do so, enter one of the following after score:
            header - displays only the name, integrity, attributes, virtue, vice
            skills - displays only skills
            merits - displays only merits
            beats - displays only conditions, beats, experience, aspirations
            advantages - displays only derived advantages, willpower and health
            wounds - just the character's wound track
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        if arg != None:
            arg = arg.lower()
        if arg == 'header':
            await ctx.send(char.displ_head())
        elif arg == 'skills':
            await ctx.send(char.displ_skills())
        elif arg == 'merits':
            await ctx.send(char.displ_merits())
        elif arg == 'beats':
            await ctx.send(char.displ_beats())
        elif arg == 'advantages':
            await ctx.send(char.displ_advant())
        elif arg == 'wounds':
            await ctx.send("{}'s Wounds:\n".format(char.name) + char.wound_track())
        elif arg == None:
            await ctx.send(char.displ_head())
            sleep(1)
            await ctx.send(char.displ_skills())
            sleep(1)
            await ctx.send(char.displ_merits())
            sleep(1)
            await ctx.send(char.displ_beats())
            sleep(1)
            await ctx.send(char.displ_advant())
            
    @commands.command(brief='Sets the current willpower for the character.')
    async def wp(self, ctx, value):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_wp(int(value))
        await ctx.send(response)
        
class Experience(commands.Cog, name='02. Beats and Experience'):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(brief='Adds a condition to the character')
    async def addcon(self, ctx, condition):
        '''Accepts one argument: The name of the condition. Multiword condition
        names should be enwrapped in quotes ("Soul Loss" not just Soul Loss)
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_con(condition)
        await ctx.send(response)       

    @commands.command(brief='Removes a condition from the character')
    async def delcon(self, ctx, condition):
        '''Accepts one argument: The name of the condition. Multiword condition
        names should be wrapped in quotes ("Soul Loss" not just Soul Loss)
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_con(condition)
        await ctx.send(response)      

    @commands.command(brief='Adds beats to the character. Automatically converts to xp.')
    async def beats(self, ctx, val):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_beats(int(val))
        await ctx.send(response)
             
    @commands.command(brief='Removes experience from the character.')
    async def spendxp(self, ctx, val):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_exp(int(val))
        await ctx.send(response)

    @commands.command(brief='Adds an aspiration to the character. Must be wrapped in quotes.')
    async def aspireto(self, ctx, aspiration):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_aspir(aspiration)
        await ctx.send(response)  
        
    @commands.command(brief='Removes an aspiration from the character. Does not award beats.')
    async def fulfill(self, ctx, aspiration):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_aspir(aspiration)
        await ctx.send(response)
        
class Combat(commands.Cog, name='03. Combat'):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(brief='Applies damage to the character')
    async def damage(self, ctx, value, damagetype='b'):
        '''Applies damage to the character. First argument is the amount of damage
        taken, and is required. Second argument is one of b, l, or a for
        bashing, lethal or aggravated respectively.
        If no second input is provided, it will default to bashing.
        '''
        value = int(value)
        damagetype = damagetype.lower()
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = ""
        if damagetype == 'b':
            response = char.add_bashing(value)
        elif damagetype == 'l':
            response = char.add_lethal(value)
        elif damagetype == 'a':
            response = char.add_agg(value)
        response += "\n" + char.wound_track()
        await ctx.send(response)
        
    @commands.command(brief='Heals damage from the character')
    async def heal(self, ctx, value=0, damagetype='b'):
        '''First argument is the amount of damage to be healed, second argument
        is the damage type. Like the damage command, this accepts one of b, l,
        or a - representing bashing, lethal or aggravated.
        If no second input is provided, it will default to bashing damage.
        '''
        value = int(value)
        damagetype = damagetype.lower()
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = ""
        if damagetype == 'b':
            response = char.bheal(value)
        elif damagetype == 'l':
            response = char.lheal(value)
        elif damagetype == 'a':
            response = char.aheal(value)
        response += "\n" + char.wound_track()
        await ctx.send(response)
        
class Creation(commands.Cog, name="04. Character Creation"):
    def __init__(self, bot):
        self.bot = bot
        
    @commands.command(brief='Alters your character name')
    async def name(self, ctx, name):
        '''Alters the name of your character. If you do not yet have a character
        sheet, one will be generated for you.
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_name(name)
        await ctx.send(response)
        
    @commands.command(brief='Sets an attribute score')
    async def attribute(self, ctx, attribute, score):
        '''Sets an attribute score for your character.
        Takes 2 arguments, separated by spaces. The first should be
        the chosen attribute, followed by the value you wish to set it to.
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_attrib(attribute, int(score))
        await ctx.send(response)
    
    @commands.command(brief='Sets a skill level')
    async def skill(self, ctx, skill, score):
        '''Sets the number of dots you have in a given skill. If the dots are
        set to 0, then you will remove that skill from your list (unless you
        also have specialties in that skill).
        Takes 2 arguments, separates by spaces. The first should be the chosen
        skill, followed by the value you wish to set it to.
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_skill(skill, int(score))
        await ctx.send(response)
        
    @commands.command(brief='Adds a skill specialty')
    async def addspecialty(self, ctx, skill, specialty):
        '''Adds a given specialty to a given skill. Requires two arguments,
        separated by spaces. The first is the skill, the second is the specialty.
        Multi-word specialties must be enclosed in quotes.
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_specialty(skill, specialty)
        await ctx.send(response)

    @commands.command(brief='Removes a skill specialty')
    async def delspecialty(self, ctx, skill, specialty):
        '''Removes a specialty from a skill. Requires two arguments,
        separated by spaces. The first is the skill, the second is the specialty.
        Multi-word specialties must be enclosed in quotes.
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_specialty(skill, specialty)
        await ctx.send(response)
        
    @commands.command(brief='Sets a merit level')
    async def merit(self, ctx, selection, value):
        '''Sets the level of a given merit. If the level becomes 0 or less, then
        that merit will be removed. Requires two arguments. The first should be
        the merit name, the second is the value of the merit. Multi-word merit
        names should be enclosed in quotes.
        '''
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_merit(selection, int(value))
        await ctx.send(response)   
        
    @commands.command(brief='Sets the Integrity score for the character.')
    async def integrity(self, ctx, value):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.mod_integ(int(value))
        await ctx.send(response)    
        
    @commands.command(brief='Sets the virtue and vice of the character.')
    async def virtvice(self, ctx, virtue, vice):
        char = get_sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_virtue(virtue) + "\n"
        response += char.set_vice(vice)
        await ctx.send(response) 

class Other(commands.Cog, name='05. Other'):        
    @commands.command(brief='Deletes the character sheet. CANNOT BE UNDONE.')
    async def clear(self, ctx, confirmation=None):
        if confirmation != 'clearcharacter':
            await ctx.send('This command will delete your character. Please be aware that this action cannot be undone.\nIf you are absolutely certain that you would like to delete your character, please input `!clear clearcharacter` in all lower case.')
        else:
            char = get_sheet(ctx.message.guild.id, ctx.author.id)
            response = char.clear_sheet()
            await ctx.send(response)    
        
def initialize_commands(bot):
    print('Initializing Common Actions')
    bot.add_cog(CommonActions(bot))
    print('Initializing Beats and Experience')
    bot.add_cog(Experience(bot))
    print('Initializing Combat')
    bot.add_cog(Combat(bot))
    print('Initializing Character Creation')
    bot.add_cog(Creation(bot))
    print('Initializing Other')
    bot.add_cog(Other(bot))