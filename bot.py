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

#API URLS
GOOGLE_SPREADSHEET_API = 'https://sheets.googleapis.com/v4/spreadsheets/'

GTA_API_URL = 'https://gta.now.sh/api/'
GTA_VEHICLE_INFO_URL = GTA_API_URL+'vehicles/'
GTA_MANUFACTURER_LOGO_URL = GTA_API_URL+'vehicles/manufacturer/'

####################################################
#################### END BLOCK #####################
####################################################

#Uses the GTA API to get information for the vehicles
#Not all the information is here, but we do get exclusive information here
def get_info_from_api(search):
    try:
        search = search.lower()
        request = requests.get(GTA_VEHICLE_INFO_URL+search)
        return request.json()
    except:
        return False

#Uses the GTA API to get the manufacturer's logo
def get_manufacturer_logo_from_api(manufacturer):
    try:
        manufacturer = manufacturer.lower()
        request = requests.get(GTA_MANUFACTURER_LOGO_URL+manufacturer)

        return request.text
    except:
        return False
#Reads a spreedsheet for the rest of the information. As this is a point of truth we will
#use this for the pricing. If the API above doesn't have a result, but the spreedsheet does,
#we'll use this for the information and omit the exclusive fields
def get_info_from_spreedsheet(search):
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
            'brand': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['BRAND']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['BRAND']) else '',
            'image': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['IMAGE']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['IMAGE']) else '',
            'carWeight': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['CAR_WEIGHT']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['CAR_WEIGHT']) else '',
            'driveTrain': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['DRIVE_TRAIN']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['DRIVE_TRAIN']) else '',
            'gears': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['GEARS']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['GEARS']) else '',
            'carryWeight': row['values'][0][GOOGLE_SPREADSHEET_COLUMN['CARRY_WEIGHT']] if index_in_list(row['values'][0], GOOGLE_SPREADSHEET_COLUMN['CARRY_WEIGHT']) else '',
        }

        return spreadsheetRow
    except:
        return False

#Formats the output into a discord embed
def format_output(brandName, carName, price, vclass='', seats='', tspeed='', speed='', acceleration='', braking='', handling='', carWeight='', driveTrain='', gears='', carryWeight='', image_url='', thumbnail_url=''):    
    output = discord.Embed(title=carName)
    output.set_author(name=brandName)
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

    if(bool(carWeight)):
        output.add_field(name='Car Weight:', value=carWeight)
    
    if(bool(driveTrain)):
        output.add_field(name='Drive Train:', value=driveTrain)
    
    if(bool(gears)):
        output.add_field(name='Gears:', value=gears)
    
    if(bool(carryWeight)):
        output.add_field(name='Carry Weight:', value=carryWeight)
    
    if(bool(image_url)):
        output.set_image(url=image_url)

    if(bool(thumbnail_url)):
        output.set_thumbnail(url=thumbnail_url)

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

            api_info = get_info_from_api(search)
            spreadsheet_info = get_info_from_spreedsheet(search)
            
            #If the API returned false, but we got information from the spreadsheet; lets search the API with the spreadsheet name
            if api_info == False and spreadsheet_info != False:
                api_info = get_info_from_api(spreadsheet_info['name'].lower())

            if spreadsheet_info != False:
                manufacturerLogo = get_manufacturer_logo_from_api(spreadsheet_info['brand'])

            #If both the API and spreadsheet return valid values, proceed to use both
            if api_info != False and spreadsheet_info != False:  
                output = format_output(
                    brandName=spreadsheet_info['brand'], 
                    carName=spreadsheet_info['name'], 
                    price=spreadsheet_info['price'],
                    vclass=spreadsheet_info['class'],
                    seats=api_info['seats'] if 'seats' in api_info else spreadsheet_info['seats'],
                    tspeed=api_info['topSpeed']['mph'] if 'topSpeed' in api_info and 'mph' in api_info['topSpeed'] else '',
                    speed=api_info['speed'] if 'speed' in api_info else '',
                    acceleration=api_info['acceleration'] if 'acceleration' in api_info else '',
                    braking=api_info['braking'] if 'braking' in api_info else '',
                    handling=api_info['handling'] if 'handling' in api_info else '',
                    carWeight=spreadsheet_info['carWeight'] if 'carWeight' in spreadsheet_info else '',
                    driveTrain=spreadsheet_info['driveTrain'] if 'driveTrain' in spreadsheet_info else '',
                    gears=spreadsheet_info['gears'] if 'gears' in spreadsheet_info else '',
                    carryWeight=spreadsheet_info['carryWeight'] if 'carryWeight' in spreadsheet_info else '',
                    image_url=api_info['images']['frontQuarter'] if 'images' in api_info and 'frontQuarter' in api_info['images'] else spreadsheet_info['image'],
                    thumbnail_url=manufacturerLogo if manufacturerLogo != False else ''
                )

                await message.channel.send(embed=output)
            #If only the spreadsheet is valid, use that
            elif spreadsheet_info != False:
                output = format_output(
                    brandName=spreadsheet_info['brand'], 
                    carName=spreadsheet_info['name'], 
                    price=spreadsheet_info['price'],
                    vclass=spreadsheet_info['class'],
                    seats=spreadsheet_info['seats'],
                    carWeight=spreadsheet_info['carWeight'] if 'carWeight' in spreadsheet_info else '',
                    driveTrain=spreadsheet_info['driveTrain'] if 'driveTrain' in spreadsheet_info else '',
                    gears=spreadsheet_info['gears'] if 'gears' in spreadsheet_info else '',
                    carryWeight=spreadsheet_info['carryWeight'] if 'carryWeight' in spreadsheet_info else '',
                    image_url=spreadsheet_info['image'] if 'image' in spreadsheet_info else '',
                    thumbnail_url=manufacturerLogo if manufacturerLogo != False else ''
                )

                await message.channel.send(embed=output)
            #Otherwise, output an message to the user to let them know the vehicle doesn't exist
            else:
                await message.channel.send('No Vehicle Found')
        except:
            #Error found, do not output anything
            print('An error has occurred')

client.run(DISCORD_BOT_TOKEN)