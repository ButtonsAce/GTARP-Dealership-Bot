import discord
import requests
import os

client = discord.Client()
#If you wish to hardcode the variables (for testing, it's a security risk if you do it for production), you can do that here
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
GOOGLE_API_KEY = os.getenv('GOOGLE_API')
GOOGLE_SPREADSHEET_ID = os.getenv('GOOGLE_SPREADSHEET_ID')

####################################################
### You can update this block to suit your needs ###
####################################################
#This is the key to get the bot to respond. This will look at the first characters in the message
#If you wish to have a space, please add it here
BOT_COMMAND = '!'

#This sets the color of the discord embed.
#0x[HEX COLOR]
EMBED_COLOR = 0x8f030f

#Update these settings based off your spreadsheet
GOOGLE_SPREADSHEET_SHEET = 'Vehicles'
GOOGLE_SPREADSHEET_SEARCH_COLUMN = 'B'
GOOGLE_SPREADSHEET_COLUMN = {
    'NAME': 0, #A
    'CLASS': 5, #F
    'SEATS': 6, #G
    'PRICE': 3, #D
    'BRAND': 9, #J
    'IMAGE': 7 #H
}
####################################################
#################### END BLOCK #####################
####################################################

#Uses the GTA API to get information for the vehicles
#Not all the information is here, but we do get exclusive information here
def get_info_from_api(search):
    try:
        request = requests.get('https://gta.now.sh/api/vehicles/'+search)
        return request.json()
    except:
        return False
    
#Reads a spreedsheet for the rest of the information. As this is a point of truth we will
#use this for the pricing. If the API above doesn't have a result, but the spreedsheet does,
#we'll use this for the information and omit the exclusive fields
def get_info_from_spreedsheet(search):
    try:
        #Let's get the column to find the row
        nameRange = GOOGLE_SPREADSHEET_SHEET+'!'+GOOGLE_SPREADSHEET_SEARCH_COLUMN+':'+GOOGLE_SPREADSHEET_SEARCH_COLUMN
        request = requests.get('https://sheets.googleapis.com/v4/spreadsheets/'+GOOGLE_SPREADSHEET_ID+'/values/'+nameRange+'?key='+GOOGLE_API_KEY)
        cars = request.json() 
        cars = cars['values']

        #This is just a quick job anyway, too lazy to find a better method
        key = 1
        found = False
        for value in cars:
            if search in value:
                found = True
                break
            key = key + 1
        
        #If not found, lets search again via substrings
        if not found:
            key = 1
            for value in cars:
                if search in value[0]:
                    found = True
                    break
                key = key + 1

        #Just a case in case it doesn't find it
        if not found:
            return False

        #Now lets get the row
        rowRange = nameRange = GOOGLE_SPREADSHEET_SHEET+'!'+str(key)+':'+str(key)
        
        request = requests.get('https://sheets.googleapis.com/v4/spreadsheets/'+GOOGLE_SPREADSHEET_ID+'/values/'+rowRange+'?key='+GOOGLE_API_KEY)
        row = request.json()
        spreadsheetRow = {
            'name': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['NAME']],
            'class': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['CLASS']],
            'seats': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['SEATS']],
            'price': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['PRICE']],
            'brand': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['BRAND']],
            'image': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['IMAGE']]
        }

        return spreadsheetRow
    except:
        return False

#Formats the output into a discord embed
def format_output(title, description, price, vclass='', seats='', tspeed='', speed='', acceleration='', braking='', handling='', image_url=''):    
    output = discord.Embed(title=title, description=description)
    output.color = EMBED_COLOR
    output.add_field(name='Price:', value=price, inline=False)

    #The following are all optional, if they aren't populated, they won't show up
    if(bool(vclass)):
        output.add_field(name='Class:', value=vclass, inline=False)
    
    if(bool(seats)):
        output.add_field(name='Seats:', value=seats)
    
    if(bool(tspeed)):
        output.add_field(name='Top Speed:', value=str(tspeed)+'mph')
    
    if(bool(speed)):
        output.add_field(name='Speed:', value=speed)
    
    if(bool(acceleration)):
        output.add_field(name='Acceleration:', value=acceleration)
    
    if(bool(braking)):
        output.add_field(name='Braking:', value=braking)
    
    if(bool(handling)):
        output.add_field(name='Handling:', value=handling)
    
    if(bool(image_url)):
        output.set_image(url=image_url)

    return output

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith(BOT_COMMAND):
        try:
            search = message.content
            search = search[int(len(BOT_COMMAND)):].lower().strip()

            api_info = get_info_from_api(search)
            spreadsheet_info = get_info_from_spreedsheet(search)
            
            #If the API returned false, but we got information from the spreadsheet; lets search the API with the spreadsheet name
            if api_info == False and spreadsheet_info != False:
                api_info = get_info_from_api(spreadsheet_info['name'].lower())

            #If both the API and spreadsheet return valid values, proceed to use both
            if api_info != False and spreadsheet_info != False:  
                output = format_output(
                    title=spreadsheet_info['brand'], 
                    description=spreadsheet_info['name'], 
                    price=spreadsheet_info['price'],
                    vclass=spreadsheet_info['class'],
                    seats=spreadsheet_info['seats'] if 'seats' in api_info else spreadsheet_info['seats'],
                    tspeed=api_info['topSpeed']['mph'] if 'topSpeed' in api_info and 'mph' in api_info['topSpeed'] else '',
                    speed=api_info['speed'] if 'speed' in api_info else '',
                    acceleration=api_info['acceleration'] if 'acceleration' in api_info else '',
                    braking=api_info['braking'] if 'braking' in api_info else '',
                    handling=api_info['handling'] if 'handling' in api_info else '',
                    image_url=api_info['images']['frontQuarter'] if 'images' in api_info and 'frontQuarter' in api_info['images'] else spreadsheet_info['image']
                )

                await message.channel.send(embed=output)
            #If only the spreadsheet is valid, use that
            elif spreadsheet_info != False:
                output = format_output(
                    title=spreadsheet_info['brand'], 
                    description=spreadsheet_info['name'], 
                    price=spreadsheet_info['price'],
                    vclass=spreadsheet_info['class'],
                    seats=spreadsheet_info['seats'],
                    image_url=spreadsheet_info['image'] if 'image' in spreadsheet_info else ''
                )

                await message.channel.send(embed=output)
            #Otherwise, output an message to the user to let them know the vehicle doesn't exist
            else:
                await message.channel.send('No Vehicle Found')
        except:
            #Error found, do not output anything
            print('An error has occurred')

client.run(DISCORD_BOT_TOKEN)
