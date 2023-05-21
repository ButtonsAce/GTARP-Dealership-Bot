import discord
import requests
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)
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

DEALERSHIP_NAME = 'Sanders Motorcycles'

#Fallback Manufacturer Info
MANUFACTURER_FALLBACK_NAME = DEALERSHIP_NAME
MANUFACTURER_FALLBACK_LOGO_URL = 'https://i.imgur.com/AYEoAPX.png'

#Update these settings based off your spreadsheet
GOOGLE_SPREADSHEET_SHEET = 'Sheet1'
GOOGLE_SPREADSHEET_SEARCH_COLUMN = 'E'
GOOGLE_SPREADSHEET_COLUMN = {
    'NAME': 3, #C
    'CLASS': 2, #B
    'SEATS': 13, #N
    'PRICE': 6, #G
    'IMAGE': 14, #O
    'TRUNK_CAP': 9, #J
    'TRUNK_SLOT': 10, #K
    'DASH_CAP': 11, #L
    'DASH_SLOT': 12, #M
    'FUEL_CAP': 7, #H
    'FUEL_ECO': 8, #I
    'BRAND_LOGO': 15 #p
}

#API URLS
GOOGLE_SPREADSHEET_API = 'https://sheets.googleapis.com/v4/spreadsheets/'

####################################################
#################### END BLOCK #####################
####################################################

#Reads a spreadsheet for the rest of the information.
def get_info_from_spreadsheet(search):
    try:
        search = search.lower()

        #Let's get the column to find the row
        nameRange = GOOGLE_SPREADSHEET_SHEET+'!'+GOOGLE_SPREADSHEET_SEARCH_COLUMN+':'+GOOGLE_SPREADSHEET_SEARCH_COLUMN
        request = requests.get(GOOGLE_SPREADSHEET_API+GOOGLE_SPREADSHEET_ID+'/values/'+nameRange+'?key='+GOOGLE_API_KEY)

        cars = request.json() 
        cars = cars['values']

        #This is just a quick job anyway, too lazy to find a better method
        key = 1
        found = False
        partialMatch = False
        partialKey = 1 #Not used unless a partial match
        for value in cars:
            if search in value:
                found = True
                break
            elif not partialMatch:
                if search in value[0]:
                    partialMatch = True
                    partialKey = key

            key = key + 1
        
        #If not found, lets use the partial match
        if not found and partialMatch:
            key = partialKey
            found = True
        #Just a case in case it doesn't find it
        elif not found:
            return False

        #Now lets get the row
        rowRange = nameRange = GOOGLE_SPREADSHEET_SHEET+'!'+str(key)+':'+str(key)
        
        request = requests.get(GOOGLE_SPREADSHEET_API+GOOGLE_SPREADSHEET_ID+'/values/'+rowRange+'?key='+GOOGLE_API_KEY)
        row = request.json()

        spreadsheetRow = {
            'name': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['NAME']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['NAME']) else '',
            'class': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['CLASS']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['CLASS']) else '',
            'seats': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['SEATS']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['SEATS']) else '',
            'price': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['PRICE']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['PRICE']) else '',
            'image': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['IMAGE']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['IMAGE']) else '',
            'truckCap': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['TRUNK_CAP']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['TRUNK_CAP']) else '',
            'trunkSlot': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['TRUNK_SLOT']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['TRUNK_SLOT']) else '',
            'dashCap': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['DASH_CAP']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['DASH_CAP']) else '',
            'dashSlot': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['DASH_SLOT']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['DASH_SLOT']) else '',
            'fuelCap': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['FUEL_CAP']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['FUEL_CAP']) else '',
            'fuelEco': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['FUEL_ECO']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['FUEL_ECO']) else '',
            'brand_logo':  row['values'][0][GOOGLE_SPREADSHEET_COLUMN['BRAND_LOGO']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['BRAND_LOGO']) else ''
        }

        return spreadsheetRow
    except:
        return False

#Formats the output into a discord embed
def format_output(
        header,
        carName,
        price,
        vclass='',
        seats='',
        tspeed='',
        speed='',
        acceleration='',
        braking='',
        handling='',
        truckCapacity='',
        trunkSlot='',
        dashboardCapacity='',
        dashboardSlot='',
        fuelCapacity='',
        fuelEco='',
        image_url='',
        thumbnail_url=''
    ):    
    
    if (bool(price)):
        output = discord.Embed(title=carName, description=price)
    else:
        output = discord.Embed(title=carName)

    if(bool(header)):
        output.set_author(name=header)
    else:
        output.set_author(name=MANUFACTURER_FALLBACK_NAME)

    output.color = EMBED_COLOR

    #The following are all optional, if they aren't populated, they won't show up
    if(bool(vclass)):
        output.add_field(name='Class:', value=vclass)
    
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

    if(bool(truckCapacity)):
        output.add_field(name='Trunk Capacity:', value=truckCapacity)

    if(bool(trunkSlot)):
        output.add_field(name='Trunk Storage:', value=trunkSlot)

    if(bool(dashboardCapacity)):
        output.add_field(name='Dashboard Capacity:', value=dashboardCapacity)

    if(bool(dashboardSlot)):
        output.add_field(name='Dashboard Storage:', value=dashboardSlot)

    if(bool(fuelCapacity)):
        output.add_field(name='Fuel Capacity:', value=fuelCapacity)

    if(bool(fuelEco)):
        output.add_field(name='Fuel Eco:', value=fuelEco)

    if(bool(image_url)):
        output.set_image(url=image_url)

    if(bool(thumbnail_url)):
        output.set_thumbnail(url=thumbnail_url)
    else:
        output.set_thumbnail(url=MANUFACTURER_FALLBACK_LOGO_URL)

    return output

#Checks to see if an index is in the list
def index_in_list(list, index):
    return index < len(list) 

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

            spreadsheet_info = get_info_from_spreadsheet(search)

            #If spreadsheet return valid values
            if spreadsheet_info != False:  
                output = format_output(
                    header=DEALERSHIP_NAME, 
                    carName=spreadsheet_info['name'], 
                    price=spreadsheet_info['price'],
                    vclass=spreadsheet_info['class'],
                    seats=spreadsheet_info['seats'],
                    truckCapacity=spreadsheet_info['truckCap'] if 'truckCap' in spreadsheet_info else '',
                    trunkSlot=spreadsheet_info['trunkSlot'] if 'trunkSlot' in spreadsheet_info else '',
                    dashboardCapacity=spreadsheet_info['dashCap'] if 'dashCap' in spreadsheet_info else '',
                    dashboardSlot=spreadsheet_info['dashSlot'] if 'dashSlot' in spreadsheet_info else '',
                    fuelCapacity=spreadsheet_info['fuelCap'] if 'fuelCap' in spreadsheet_info else '',
                    fuelEco=spreadsheet_info['fuelEco'] if 'fuelEco' in spreadsheet_info else '',
                    image_url=spreadsheet_info['image'] if 'image' in spreadsheet_info else '',
                    thumbnail_url=spreadsheet_info['brand_logo'] if 'brand_logo' in spreadsheet_info else '',
                )

                await message.channel.send(embed=output)
            #Otherwise, output an message to the user to let them know the vehicle doesn't exist
            else:
                await message.channel.send('No Vehicle Found')
        except:
            #Error found, do not output anything
            print('An error has occurred')

client.run(DISCORD_BOT_TOKEN)