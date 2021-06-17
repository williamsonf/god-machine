'''
Created on Jun 16, 2021

@author: Fred
'''
from time import sleep
from char_sheet import sheet

def initialize_commands(client):
    @client.command(brief='Displays the character sheet. Contains optional arguments.')
    async def score(ctx, arg=None):
        '''Displays the character sheet. By default, as a series of messages.
        However, a single page of the character sheet may be selected instead.
        To do so, enter one of the following after score:
            header - displays only the name, integrity, attributes, virtue, vice
            skills - displays only skills
            merits - displays only merits
            beats - displays only conditions, beats, experience, aspirations
            advantages - displays only derived advantages, willpower and health (once health is implemented)
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
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
        
    @client.command(brief='Rolls dice according to your wants.')
    async def roll(ctx, *args):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.roll_dice(args)
        await ctx.send(response)
        
    @client.command(brief='Alters your character name')
    async def name(ctx, name):
        '''Alters the name of your character. If you do not yet have a character
        sheet, one will be generated for you.
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_name(name)
        await ctx.send(response)
        
    @client.command(brief='Sets an attribute score')
    async def attribute(ctx, attribute, score):
        '''Sets an attribute score for your character.
        Takes 2 arguments, separated by spaces. The first should be
        the chosen attribute, followed by the value you wish to set it to.
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_attrib(attribute, int(score))
        await ctx.send(response)
    
    @client.command(brief='Sets a skill level')
    async def skill(ctx, skill, score):
        '''Sets the number of dots you have in a given skill. If the dots are
        set to 0, then you will remove that skill from your list (unless you
        also have specialties in that skill).
        Takes 2 arguments, separates by spaces. The first should be the chosen
        skill, followed by the value you wish to set it to.
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_skill(skill, int(score))
        await ctx.send(response)
        
    @client.command(brief='Adds a skill specialty')
    async def addspecialty(ctx, skill, specialty):
        '''Adds a given specialty to a given skill. Requires two arguments,
        separated by spaces. The first is the skill, the second is the specialty.
        Multi-word specialties must be enclosed in quotes.
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_specialty(skill, specialty)
        await ctx.send(response)
        
    @client.command(brief='Removes a skill specialty')
    async def delspecialty(ctx, skill, specialty):
        '''Removes a specialty from a skill. Requires two arguments,
        separated by spaces. The first is the skill, the second is the specialty.
        Multi-word specialties must be enclosed in quotes.
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_specialty(skill, specialty)
        await ctx.send(response)
        
    @client.command(brief='Sets a merit level')
    async def merit(ctx, selection, value):
        '''Sets the level of a given merit. If the level becomes 0 or less, then
        that merit will be removed. Requires two arguments. The first should be
        the merit name, the second is the value of the merit. Multi-word merit
        names should be enclosed in quotes.
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_merit(selection, int(value))
        await ctx.send(response)
        
    @client.command(brief='Adds a condition to the character')
    async def addcon(ctx, condition):
        '''Accepts one argument: The name of the condition. Multiword condition
        names should be enwrapped in quotes ("Soul Loss" not just Soul Loss)
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_con(condition)
        await ctx.send(response)       

    @client.command(brief='Removes a condition from the character')
    async def delcon(ctx, condition):
        '''Accepts one argument: The name of the condition. Multiword condition
        names should be wrapped in quotes ("Soul Loss" not just Soul Loss)
        '''
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_con(condition)
        await ctx.send(response)      

    @client.command(brief='Adds beats to the character. Automatically converts to xp.')
    async def beats(ctx, val):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_beats(int(val))
        await ctx.send(response)
             
    @client.command(brief='Removes experience from the character.')
    async def spendxp(ctx, val):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_exp(int(val))
        await ctx.send(response)
    
    @client.command(brief='Adds an aspiration to the character. Must be wrapped in quotes.')
    async def aspireto(ctx, aspiration):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.add_aspir(aspiration)
        await ctx.send(response)  
        
    @client.command(brief='Removes an aspiration from the character. Must be wrapped in quotes. This command does not award a beat on its own.')
    async def fulfill(ctx, aspiration):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.del_aspir(aspiration)
        await ctx.send(response)
        
    @client.command(brief='Sets the Integrity score for the character.')
    async def integrity(ctx, value):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.mod_integ(int(value))
        await ctx.send(response)    
        
    @client.command(brief='Sets the virtue and vice of the character.')
    async def virtvice(ctx, virtue, vice):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_virtue(virtue) + "\n"
        response += char.set_vice(vice)
        await ctx.send(response)
            
    @client.command(brief='Sets the current willpower for the character.')
    async def wp(ctx, value):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.set_wp(int(value))
        await ctx.send(response)
        
    @client.command(brief='Deletes the character sheet. CANNOT BE UNDONE.')
    async def clear(ctx):
        char = sheet(ctx.message.guild.id, ctx.author.id)
        response = char.clear_sheet()
        await ctx.send(response)