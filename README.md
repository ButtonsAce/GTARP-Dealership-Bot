# GTA RP Dealership Prices Discord Bot

## Features

Allows you to enter in a key and a search term and the bot will get the results of the vehicle based on a combination of the the unoffical GTA RP API and a specified Google Sheet. 

## Requirements

* [Discord Bot Token](https://discordpy.readthedocs.io/en/stable/discord.html)
* [Google Sheets API Key](https://developers.google.com/workspace/guides/create-credentials)
* Pip Packages
    * discord: `pip install -U discord.py`
    * requests: `pip install requests`

## Environment Variables

* `DISCORD_TOKEN`: The Discord Bot token
* `GOOGLE_API`: Google API Key (Make sure it is an API key and not an OAuth Key)
* `GOOGLE_SPREADSHEET_ID`: The id of the Google Sheets

## Starting the Bot

1. Add the bot to your server, you can find out information here: [Discord Docs](https://discordpy.readthedocs.io/en/stable/discord.html)
1. Add the environment variables with your own keys/ids
    1. You can also modify some of the contents of the code, it's wrapped around comments.
1. Go to the folder this project is in and run `py bot.py`