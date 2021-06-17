'''
Created on Jun 16, 2021
The base class used for storing and retrieving information for a
Chronicles of Darkness character sheet

@author: Fred
'''
import pymongo, os, random
from dotenv import load_dotenv
load_dotenv()

men_skills = ['academics', 'computer', 'crafts', 'investigation', 'medicine', 'occult', 'politics', 'science']
phy_skills = ['athletics', 'brawl', 'drive', 'firearms', 'larceny', 'stealth', 'survival', 'weaponry']
soc_skills = ['animals', 'empathy', 'expression', 'intimidation', 'persuasion', 'socialize', 'streetwise', 'subterfuge']
skill_list = men_skills+phy_skills+soc_skills

class sheet():
    '''
    The base class used for storing and retrieving information for a
    Chronicles of Darkness character sheet
    
    Attributes
    -----------
    server_id : int
        the discord server id for the originating server. serves as the
        collection name for the mongo db on which characters are stored.
    user_id : int
        the discord user id for the owner of this character sheet. serves
        to identify and search for the character in a given collection, selected
        by the server_id
    splat : str
        the gameline the character is from
    name : str
        the character name
    attributes : dic
        a dictionary containing the attributes of the character, where
        attribute names are the key and their value is an integer
    skills : dic
        a dictionary containing the skills of the character, where skill names
        are the key. the values in this dictionary form a list, with the value
        of the skill at index 0 as an int. indexes 1: potentially contain
        specialties, stored as a string
    merits : dic
        a dictionary containing the characters merits. keys are merit names, str,
        and values are int, representing the level of the merit
    conditions : list
        a list of strings, indicating conditions afflicting the character
    beats : int
        the number of beats acquired by the character
    experience : int
        the amount of experience acquired by the character
    aspirations : list
        a list of strings representing the character's aspirations
    integrity : int
        the character's integrity score
    willpower : int
        the character's current willpower points
    virtue : str
        the character's Virtue
    vice : str
        the character's Vice
        
    Methods
    -------
    find_sheet
        Connects to the bot's MongoDB and returns the stored character sheet
    save_sheet
        Connects to the bot's MongoDB and updates the stored character sheet
    unload
        Generates a dictionary based on the sheet's attributes, for storage
        in the bot's MongoDB
    set_name
        Sets self.name to a given input, and then saves the sheet with save_sheet
    set_attrib
        Sets one of the characters statistical attributes to a given value,
        and then saves the sheet with save_sheet
    set_skill
        Sets one of the character's skills to a given value. If that value
        would be 0 or less and there are no specialties, it removes the skill
    add_specialty
        Adds a new specialty to the character's chosen skill
    del_specialty
        Removes a known specialty from the character's chosen skill
    set_merit
        Alters a value for a given merit, adding it if it is not yet known
        and removing it if the value is 0 or less
    add_con
        Adds a condition to the character
    del_con
        Removes a condition from the character
    add_beats
        Adds a number of beats to the character. If the beats are enough to
        generate new experience, then that is updated as well
    del_exp
        Reduces character's experience points by a given value
    add_aspir
        Adds an aspiration to the character
    del_aspir
        Removes an aspiration from the character
    max_wp
        Calculates the character's maximum willpower
    mod_integ
        Sets the character's Integrity stat
    set_wp
        Sets the character's willpower points
    displ_head, displ_skills, displ_merits
    displ_beats, displ_advant
        Returns a formatted block of text for posting to the discord
    set_virtue
        sets the character's virtue
    set_vice
        sets the character's vice
    clear_sheet
        deletes a sheet
    parse_rollargs
        parses a list of arguments used to define a roll
    '''


    def __init__(self, server_id, user_id):
        '''
        Initializing a sheet instance takes a discord server id and user id
        and collects that information from a mongo db, which is then used
        to populate the other attributes of the class.
        
        Args
        ----
        server_id : int
            a discord server id, will serve as the collection name when searching
            for the character sheet
        user_id : int
            a discord user id, which acts as a unique identifier for every
            character saved to a given collection in the database
        '''
        self.server_id = str(server_id)
        self.user_id = user_id
        info = self.find_sheet()
        self.splat = info.get("splat", "mortal")
        self.name = info.get("name", "Unnamed Character")
        default_attributes = {'intelligence' : 1, 'wits' : 1, 'resolve' : 1,
                              'strength' : 1, 'dexterity' : 1, 'stamina' : 1,
                              'presence' : 1, 'manipulation' : 1, 'composure' : 1}
        self.attributes = info.get("attributes", default_attributes)
        self.skills = info.get("skills", {})
        self.merits = info.get('merits', {})
        self.conditions = info.get('conditions', [])
        self.beats = info.get('beats', 0)
        self.experience = info.get('experience', 0)
        self.aspirations = info.get('aspirations', [])
        self.integrity = info.get('integrity', 7)
        self.willpower = info.get('willpower', self.max_wp())
        self.virtue = info.get('virtue', 'Nice')
        self.vice = info.get('vice', 'Naughty')

        
    def find_sheet(self):
        mongo_client = pymongo.MongoClient(os.environ.get('DB_HOST'), int(os.environ.get('DB_PORT')))
        db = mongo_client[os.environ.get('DB_NAME')]
        collection = db[self.server_id]
        sheet = collection.find_one({'user id' : self.user_id})
        if sheet != None:
            return sheet
        else:
            return {}
    
    def save_sheet(self):
        mongo_client = pymongo.MongoClient(os.environ.get('DB_HOST'), int(os.environ.get('DB_PORT')))
        db = mongo_client[os.environ.get('DB_NAME')]
        collection = db[self.server_id]
        collection.replace_one({'user id' : self.user_id}, self.unload(), upsert=True)
        
    def unload(self):
        result = {}
        result['user id'] = self.user_id
        result['splat'] = self.splat
        result['name'] = self.name
        result['attributes'] = self.attributes
        result['skills'] = self.skills
        result['merits'] = self.merits
        result['conditions'] = self.conditions
        result['beats'] = self.beats
        result['experience'] = self.experience
        result['aspirations'] = self.aspirations
        result['integrity'] = self.integrity
        result['willpower'] = self.willpower
        result['virtue'] = self.virtue
        result['vice'] = self.vice
        
        return result
    
    def set_name(self, user_input):
        self.name = str(user_input)
        self.save_sheet()
        return "{}'s new name has been saved!".format(self.name)
    
    def set_attrib(self, attribute, user_input):
        attribute = attribute.lower()
        if attribute in self.attributes:
            if user_input > 0:
                self.attributes[attribute] = user_input
                self.save_sheet()
                return "{}'s {} is now {}.".format(self.name, attribute.title(), str(self.attributes[attribute]))
            else:
                return "Invalid value for an attribute score."
        else:
            return "Invalid attribute selected: {}".format(attribute.title())
        
    def set_skill(self, skill, user_input):
        skill = skill.lower()
        if skill not in skill_list:
            return "Skill does not exist. Valid skills are: {}".format(', '.join(skill_list))
        if skill in self.skills: #First we check to see if the character already knows the skill. We don't want to erase specialties by accident.
            if user_input > 0 or len(self.skills[skill]) > 1: #If it's greater than 0 or it has a specialty, we set the new skill level
                if user_input < 0:
                    user_input = 0
                self.skills[skill][0] = user_input
                self.save_sheet()
                return "{}'s {} is now {}.".format(self.name, skill.title(), str(self.skills[skill][0]))
            else: #If user input is 0 or less, and no specialties, we remove the skill
                self.skills[skill].pop()
                self.save_sheet()
                return "{} no longer has the skill {}.".format(self.name, skill.title())
        else: #If the skill isn't yet listed
            if user_input > 0:
                self.skills[skill] = []
                self.skills[skill].append(user_input)
                self.save_sheet()
                return "{}'s {} is now {}.".format(self.name, skill.title(), str(self.skills[skill][0]))
            else:
                return "Skill levels must be greater than 0."
            
    def add_specialty(self, skill, specialty):
        skill = skill.lower()
        specialty = specialty.lower()
        if skill not in skill_list:
            return "Skill does not exist. Valid skills are: {}".format(', '.join(skill_list))
        if skill in self.skills:
            existing = self.skills[skill]
            if specialty in existing:
                return "{} already has that specialty.".format(self.name)
            self.skills[skill].append(specialty)
        else:
            self.skills[skill] = []
            self.skills[skill].append(0)
            self.skills[skill].append(specialty)
        self.save_sheet()
        return "{} now has the specialty {} in {}.".format(self.name, specialty.title(), skill.title())
    
    def del_specialty(self, skill, specialty):
        skill = skill.lower()
        specialty = specialty.lower()
        if skill in self.skills:
            if specialty in self.skills[skill]:
                self.skills[skill].pop(self.skills[skill].index(specialty))
                self.save_sheet()
                return "{} has been removed.".format(specialty.title())
            else:
                return "That specialty is not known."
        else:
            return "That skill is not known."
        
    def set_merit(self, merit, user_input):
        merit = merit.lower()
        if merit in self.merits:
            if user_input > 0:
                self.merits[merit] = user_input
                self.save_sheet()
                return "{} is now {}.".format(merit.title(), str(self.merits[merit]))
            else:
                self.merits[merit].pop()
                self.save_sheet()
                return "{} has been removed.".format(merit.title())
        else:
            if user_input > 0:
                self.merits[merit] = user_input
                self.save_sheet()
                return "{} is now {}.".format(merit.title(), str(self.merits[merit]))
            else:
                return "You must have a merit before you can delete it."
            
    def add_con(self, condition):
        condition = condition.lower()
        self.conditions.append(condition)
        self.save_sheet()
        return "{} is now afflicted with {}!".format(self.name, condition.title())
    
    def del_con(self, condition):
        condition = condition.lower()
        if condition in self.conditions:
            self.conditions.pop(self.conditions.index(condition))
            self.save_sheet()
            return "{} has been removed.".format(condition.title())
        else:
            return "{} does not have that condition.".format(self.name)
        
    def add_beats(self, value):
        if value > 0:
            curr_beats = self.beats
            new_beats = curr_beats + value
            xp_gain = 0
            while new_beats >= 5:
                xp_gain += 1
                new_beats -= 5
            self.beats = int(new_beats)
            self.experience += int(xp_gain)
            self.save_sheet()
            return "{} has earned {} beats and {} exp, leaving them with {} beats.".format(self.name, str(value), str(int(xp_gain)), str(self.beats))
        else:
            return "Cannot gain negative beats."
        
    def del_exp(self, value):
        if value <= self.experience:
            self.experience -= int(value)
            self.save_sheet()
            return "{} has spent {} experience. They now have {}.".format(self.name, str(int(value)), str(self.experience))
        else:
            return "Cannot spend more experience than you have!"
        
    def add_aspir(self, aspir):
        self.aspirations.append(aspir)
        self.save_sheet()
        return "{} now has the aspiration {}".format(self.name, aspir)
    
    def del_aspir(self, aspir):
        if aspir in self.aspirations:
            self.aspirations.pop(self.aspirations.index(aspir))
            self.save_sheet()
            return "Aspiration removed."
        else:
            return "{} does not have that aspiration. Please be certain that all capitalization, spelling and punctuation is 1:1.".format(self.name)
        
    def max_wp(self):
        return self.attributes['resolve'] + self.attributes['composure']
    
    def mod_integ(self, value):
        if value >= 0:
            self.integrity = value
            self.save_sheet()
            return "{}'s integrity is now {}".format(self.name, str(self.integrity))
        else:
            return "Cannot have negative integrity."
        
    def set_wp(self, value):
        if value >= 0 and value <= self.max_wp():
            self.willpower = value
            self.save_sheet()
            return "{} now has {} willpower.".format(self.name, str(self.willpower))
        else:
            return "Invalid value for willpower. {}'s max willpower is {}".format(self.name, str(self.max_wp()))
        
    def displ_head(self):
        '''Returns a block of text used as a header for displaying the character sheet.
        Contains name, splat, integrity, and attributes.
        '''
        result = "__***"+self.name+"***__"
        result += ", "+self.splat.title()+"\n"
        result += "**Virtue:** {}\t**Vice:** {}\n".format(self.virtue, self.vice)
        result += "**Integrity:** "+str(self.integrity)
        result += "\n\n"
        result += "__**Attributes**__\n```"
        result += "Int {}\tStr {}\tPre {}\n".format(str(self.attributes['intelligence']), str(self.attributes['strength']), str(self.attributes['presence']))
        result += "Wit {}\tDex {}\tMan {}\n".format(str(self.attributes['wits']), str(self.attributes['dexterity']), str(self.attributes['manipulation']))
        result += "Res {}\tSta {}\tCom {}\n".format(str(self.attributes['resolve']), str(self.attributes['stamina']), str(self.attributes['composure']))
        result += "```"
        return result
    
    def displ_skills(self):
        '''Returns a block of text containing the character's skills and specialties
        in a more readable format.
        '''
        mental = {}
        physical = {}
        social = {}
        for x in self.skills:
            if x in men_skills:
                mental[x] = self.skills[x]
            elif x in phy_skills:
                physical[x] = self.skills[x]
            elif x in soc_skills:
                social[x] = self.skills[x]
        result = "__**Skills**__\n"
        result += "**Mental Skills**\n"
        for x in mental:
            if len(mental[x]) == 1: #If there are no specialties
                result += "{}\t{}\n".format(x.title(), str(mental[x][0]))
            else:
                result += "{} ({})\t{}\n".format(x.title(), ", ".join(mental[x][1:]).title(), str(mental[x][0]))
        result += "**Physical  Skills**\n"
        for x in physical:
            if len(physical[x]) == 1: #If there are no specialties
                result += "{}\t{}\n".format(x.title(), str(physical[x][0]))
            else:
                result += "{} ({})\t{}\n".format(x.title(), ", ".join(physical[x][1:]).title(), str(physical[x][0]))
        result += "**Social Skills**\n"
        for x in social:
            if len(social[x]) == 1: #If there are no specialties
                result += "{}\t{}\n".format(x.title(), str(social[x][0]))
            else:
                result += "{} ({})\t{}\n".format(x.title(), ", ".join(social[x][1:]).title(), str(social[x][0]))
        return result
    
    def displ_merits(self):
        '''Returns a block of text containing the character's merits in a more 
        readable format.
        '''
        result = "__**Merits**__\n"
        for x in self.merits:
            result += "{}\t{}\n".format(x.title(), str(self.merits[x]))
        return result
    
    def displ_beats(self):
        '''Returns a block of text containing experience related aspects of the
        character's sheet. Beats, Experience, Conditions, and Aspirations.
        '''
        result = "__**Conditions**__\n"
        for x in self.conditions:
            result += x.title()+"\n"
        result += "\n**Beats:** {}\t**Experience:** {}\n__**Aspirations**__\n".format(str(self.beats), str(self.experience))
        for x in self.aspirations:
            result += x.title()+"\n"
        return result
    
    def displ_advant(self):
        '''Returns a block of text containing the derived attributes of the
        character sheet. Willpower, Health, Initiative, Defense, Size, Speed.
        '''
        results = "__**Advantages**__\n"
        results += "Willpower: {}/{}\n".format(str(self.willpower), str(self.max_wp()))
        results += "Initiative: {}\n".format(str(self.get_initiative()))
        results += "Defense: {}\n".format(str(self.get_defense()))
        results += "Size: {}\n".format(str(self.get_size()))
        results += "Speed: {}\n".format(str(self.get_speed()))
        return results
        
    def get_initiative(self):
        result = self.attributes['dexterity'] + self.attributes['composure']
        if 'fast reflexes' in self.merits:
            result += self.merits['fast reflexes']
        return result
    
    def get_defense(self):
        result = min([self.attributes['dexterity'], self.attributes['wits']])
        if 'athletics' in self.skills:
            result += self.skills['athletics'][0]
        return result
    
    def get_size(self):
        result = 5
        if 'giant' in self.merits:
            result += 1
        if 'small-framed' in self.merits:
            result -= 1
        return result
    
    def get_speed(self):
        return self.attributes['strength']+self.attributes['dexterity']+self.get_size()
    
    def set_virtue(self, value):
        self.virtue = value
        self.save_sheet()
        return "Virtue has been set to {}".format(self.virtue)
    
    def set_vice(self, value):
        self.vice = value
        self.save_sheet()
        return "Vice has been set to {}".format(self.vice)
    
    def clear_sheet(self):
        mongo_client = pymongo.MongoClient(os.environ.get('DB_HOST'), int(os.environ.get('DB_PORT')))
        db = mongo_client[os.environ.get('DB_NAME')]
        collection = db[self.server_id]
        collection.delete_one({'user id' : self.user_id})
        return "Character {} has been deleted.".format(self.name)
    
    def parse_rollargs(self, arglist=[]):
        result = {'type' : 'normal', 'skills' : [], 'attributes' : [], 'rote' : False, 'specialty' : [], 'math' : []}
        if len(arglist) != 0:
            for x in arglist:
                if type(x) == str:
                    x = x.lower()
                if x in skill_list:
                    result['skills'].append(x)
                elif x in self.attributes:
                    result['attributes'].append(x)
                elif x in ['9again', '8again', 'chance']:
                    result['type'] = x
                elif x == 'rote':
                    result['rote'] = True
                elif x[0] == "(" and x[-1] == ")":
                    result['specialty'].append(x.strip('()'))
                elif x[0] == "+" or x[0] == "-":
                    result['math'].append(x)
                elif type(x) == int or x.isnumeric():
                    result['math'].append("+"+str(x))
        return result
    
    def build_dicepool(self, argdic):
        pool = 0
        if argdic['type'] == 'chance':
            pool = 1
            return pool
        for skill in argdic['skills']:
            if skill in self.skills: #if they have the skill
                if self.skills[skill][0] > 0: #If it is trained
                    pool += self.skills[skill][0]
                else: #if it is untrained
                    if skill in men_skills:
                        pool -= 3
                    elif skill in phy_skills or skill in soc_skills:
                        pool -= 1
                if len(self.skills[skill]) > 1:
                    for spec in self.skills[skill][1:]:
                        if spec in argdic['specialty']:
                            pool += 1
            else:
                if skill in men_skills:
                    pool -= 3
                elif skill in phy_skills or skill in soc_skills:
                    pool -= 1
        for attrib in argdic['attributes']:
            pool += self.attributes[attrib]
        for num in argdic['math']:
            if num[0] == '+':
                pool += int(num.strip('+'))
            else:
                pool -= int(num.strip('-'))
        if pool <= 0:
            pool = 1
            argdic['type'] = 'chance'
        argdic['pool'] = pool
        return argdic
    
    def roll_dice(self, arglist):
        rules = self.parse_rollargs(arglist)
        rules = self.build_dicepool(rules)
        roll_results = []
        successes = 0
        explosions = 0
        explode_on = 10
        
        if rules['type'] == 'chance':
            explode_on = 11
        elif rules['type'] == '9again':
            explode_on = 9
        elif rules['type'] == '8again':
            explode_on = 8
            
        for _ in range(rules['pool']):
            roll_list = []
            roll = random.randint(1,10)
            roll_list.append(roll)
            if rules['rote'] == True and roll == 1:
                roll = random.randint(1,10)
                roll_list.append(roll)
            if roll >= 8 and rules['type'] != 'chance':
                successes += 1
                while roll >= explode_on:
                    explosions += 1
                    roll = random.randint(1,10)
                    roll_list.append(roll)
                    if roll >= 8:
                        successes += 1
            elif rules['type'] == 'chance' and roll == 10:
                successes += 1
            if len(roll_list) == 1:
                roll_results.append(str(roll_list[0]))
            else:
                outcome = str(roll_list[0])
                roll_list = roll_list[1:]
                if len(roll_list) > 1:
                    string_ints = [str(i) for i in roll_list]
                    roll_list = ", ".join(string_ints)
                else:
                    roll_list = str(roll_list[0])
                outcome += "("+roll_list+")"
                roll_results.append(outcome)
                
        roll_results = ", ".join(roll_results)
        if rules['pool'] > 1:
            dice_word = 'dice'
        else:
            dice_word = 'die'
        if rules['type'] == 'chance':
            rules['pool'] = 'a chance'
        return "You rolled {} {}!\n**{} successes** and {} explosions\n{}".format(str(rules['pool']), dice_word, str(successes), str(explosions), roll_results)                
    
if __name__ == '__main__':
    test = sheet(100, 1000)
    test.clear_sheet()
    test = sheet(100, 1000)
    test.set_name('Bob the Tester')
    test.set_virtue('Kind')
    test.set_virtue('Grim')
    test.set_attrib('sTaMinA', 3)
    test.mod_integ(6)
    print(test.displ_head())
    test.set_skill('aTHleTicS', 3)
    test.set_skill('Boomer', 5)
    test.add_specialty('ATHLETICS', 'running')
    test.add_specialty('ATHLETICS', 'swimming')
    test.set_skill('Science', 4)
    test.set_skill('Persuasion', 2)
    print(test.displ_skills())
    test.set_merit('Giant', 1)
    print(test.displ_merits())
    test.add_con('Dumb Dumb')
    test.add_aspir('Get this damn thing to work.')
    test.add_aspir('Something else.')
    test.add_beats(7)
    print(test.displ_beats())
    test.set_wp(0)
    print(test.displ_advant())
    print(test.roll_dice(['AthLETics', 'RuNning', 'stamina', '9again']))
    print(test.roll_dice(['no']))
    print(test.roll_dice(['inTELLIGENCE', 'science']))
    print(test.roll_dice(['Stamina', 'ATHLETICS', 'rote', '8again']))
    print(test.roll_dice(['Athletics', 'Running', 'Stamina', '8again', '-5']))
    print(test.roll_dice(['Athletics', 'Running', 'Stamina', '+5']))
    test.clear_sheet()