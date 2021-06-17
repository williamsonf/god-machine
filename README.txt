Discord Bot Invite Link: currently unavailable

God Machine Bot is a rather simple discord bot designed both to store character
sheets, and to provide ease of dice rolling. The bot is capable of understanding
requests like "roll Athletics Strength 9again" and will construct a dice pool
and roll along the given parameters.

Currently, the God Machine only supports Mortal character sheets.
The intention is to eventually expand its functions to cover the other gamelines.

Players are able to have one sheet saved per server that the God Machine inhabits.

God Machine requires the following to run:

A .env file in the same directory as bot.py
This file should contain the following variables:
	DB_HOST - the host name for a mongo db
	DB_PORT - the port for a mongo db
	DB_NAME - the name of the mongo db
	DISCORD_API_KEY - the discord api key used for your bot
	
God Machine will require the following discord permissions:
	Read messages
	Send messages
	
Naturally, you will also need to have a mongo database to connect to.