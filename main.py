# Hey, if ur reading this, ts is a message left by the original code developer (specific_aura on discord), navigate over to 'TOKEN' and add ur Bot token.
# Make sure all intents are enabled and that the bot is in the server.
# The only thing that needa to be configured is the bot token, everything else is already ready!
# If you dont know what ur doing, DONT edit the code at all (inventory and stuffs is saved in data.json (the other file))
# You can add your own players by navigating over to rarities which is on line 22 and adding players below the signated rairty (dont do it if u dont know how to..)
# Credits would be nice..


import discord
from discord import app_commands
from discord.ext import commands
import random
import time
import json
import os

TOKEN = "REPLACE_THIS_WITH_YOUR_TOKEN"
DATA_FILE = "data.json"

intents = discord.Intents.default()
client = commands.Bot(command_prefix="!", intents=intents)

# You can add as much players u want lol, adding all these players were one pain in the ass to do :/
rarities = {
    "Common": (60, [
        "Bukayo Saka", "Bruno Fernandes", "Antoine Griezmann", "Marcus Rashford", 
        "Jack Grealish", "Phil Foden", "Jamal Musiala", "Martin Ødegaard", 
        "Declan Rice", "Gabriel Jesus", "Raphinha", "Kai Havertz", 
        "Mason Mount", "Serge Gnabry", "Kingsley Coman", "Federico Chiesa",
        "Luis Díaz", "Heung-min Son", "Ousmane Dembélé", "Riyad Mahrez"
    ]),
    "Rare": (30, [
        "Erling Haaland", "Vinicius Jr", "Harry Kane", "Kevin De Bruyne", 
        "Robert Lewandowski", "Jude Bellingham", "Luka Modrić", "Toni Kroos", 
        "Virgil van Dijk", "Thibaut Courtois", "Manuel Neuer", "Karim Benzema", 
        "Sadio Mané", "N'Golo Kanté", "Casemiro", "Rúben Dias", 
        "Trent Alexander-Arnold", "João Cancelo", "Joshua Kimmich", "Marquinhos"
    ]),
    "Legendary": (9, [
        "Kylian Mbappé", "Neymar Jr", "Pedri", "Mohamed Salah", 
        "Zlatan Ibrahimović", "Andrea Pirlo", "Xabi Alonso", "Arjen Robben", 
        "Franck Ribéry", "Sergio Agüero", "David Silva", "Fernando Torres", 
        "Steven Gerrard", "Wayne Rooney", "Paul Scholes", "Ryan Giggs"
    ]),
    "Mythical": (1, [
        "Lionel Messi", "Cristiano Ronaldo", "Pelé", "Diego Maradona", 
        "Johan Cruyff", "Zinedine Zidane", "Ronaldinho", "Ronaldo Nazário", 
        "Thierry Henry", "Andrés Iniesta", "Xavi", "Paolo Maldini"
    ])
}


values = {
    "Common": 100,
    "Rare": 500,
    "Legendary": 2000,
    "Mythical": 10000
}


inventories = {}      
cash = {}             
shop_inventories = {} 

roll_cooldowns = {}   

def create_embed(title, description, color=discord.Color.blurple()):
    """Helper to create a styled embed."""
    embed = discord.Embed(title=title, description=description, color=color)
    embed.set_footer(text="Football RNG Bot")
    return embed

def get_player_rarity(player):
    """Returns the rarity of the given player."""
    for rarity, data in rarities.items():
        if player in data[1]:
            return rarity
    return "Unknown"

def generate_shop_inventory():
    """Generate a shop inventory with 5 random items based on weighted rarity.
       Each item is a tuple: (player, rarity, cost) where cost is double the sell value.
    """
    inventory = []
    for _ in range(5):
        roll_num = random.randint(1, 100)
        if roll_num <= 60:
            rarity = "Common"
        elif roll_num <= 90:
            rarity = "Rare"
        elif roll_num <= 99:
            rarity = "Legendary"
        else:
            rarity = "Mythical"
        player = random.choice(rarities[rarity][1])
        cost = values[rarity] * 2  
        inventory.append((player, rarity, cost))
    return inventory

def save_data():
    """Save inventories, cash, and shop_inventories to a JSON file."""
    data = {
        "inventories": {uid: list(players) for uid, players in inventories.items()},
        "cash": cash,
        "shop": shop_inventories
    }
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

def load_data():
    """Load persistent data from a JSON file if it exists."""
    global inventories, cash, shop_inventories
    if os.path.isfile(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)
            inventories = {uid: set(players) for uid, players in data.get("inventories", {}).items()}
            cash = data.get("cash", {})
            shop_inventories = data.get("shop", {})
    else:
        inventories = {}
        cash = {}
        shop_inventories = {}

load_data()

@client.event
async def on_ready():
    print(f"Logged in as {client.user}")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} commands.")
    except Exception as e:
        print(f"Sync error: {e}")

@client.tree.command(name="roll")
async def roll(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    current_time = time.time()
    if user_id in roll_cooldowns and current_time - roll_cooldowns[user_id] < 3:
        wait_time = 3 - (current_time - roll_cooldowns[user_id])
        embed = create_embed("Cooldown", f"Please wait {wait_time:.1f} more seconds before rolling again.", discord.Color.dark_red())
        await interaction.response.send_message(embed=embed, ephemeral=True)
        return
    roll_cooldowns[user_id] = current_time

    roll_num = random.randint(1, 100)
    if roll_num <= 60:
        rarity = "Common"
        color = discord.Color.green()
    elif roll_num <= 90:
        rarity = "Rare"
        color = discord.Color.gold()
    elif roll_num <= 99:
        rarity = "Legendary"
        color = discord.Color.orange()
    else:
        rarity = "Mythical"
        color = discord.Color.red()
    player = random.choice(rarities[rarity][1])

    if user_id not in inventories:
        inventories[user_id] = set()
        cash[user_id] = 0
    inventories[user_id].add(player)
    save_data()

    embed = create_embed("Roll Result", f"You rolled **{player}**! ({rarity})", color)
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="inventory")
async def inventory(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in inventories or not inventories[user_id]:
        embed = create_embed("Inventory", "Your inventory is empty!", discord.Color.dark_grey())
        await interaction.response.send_message(embed=embed)
    else:
        players_list = ""
        for player in inventories[user_id]:
            rarity = get_player_rarity(player)
            players_list += f"**{player}** - *{rarity}*\n"
        embed = create_embed("Your Inventory", players_list, discord.Color.blue())
        await interaction.response.send_message(embed=embed)

@client.tree.command(name="sell")
async def sell(interaction: discord.Interaction, player: str):
    user_id = str(interaction.user.id)
    if user_id not in inventories or player not in inventories[user_id]:
        embed = create_embed("Sell Player", "You don't have that player!", discord.Color.dark_red())
        await interaction.response.send_message(embed=embed)
        return
    rarity = get_player_rarity(player)
    if rarity == "Unknown":
        embed = create_embed("Sell Player", "Invalid player!", discord.Color.dark_red())
        await interaction.response.send_message(embed=embed)
        return
    inventories[user_id].remove(player)
    cash[user_id] += values[rarity]
    save_data()
    embed = create_embed("Player Sold", f"Sold **{player}** for ${values[rarity]}!", discord.Color.purple())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="balance")
async def balance(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    bal = cash.get(user_id, 0)
    embed = create_embed("Balance", f"You have ${bal}.", discord.Color.teal())
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="shop")
async def shop(interaction: discord.Interaction):
    user_id = str(interaction.user.id)
    if user_id not in shop_inventories or not shop_inventories[user_id]:
        shop_inventories[user_id] = generate_shop_inventory()
        save_data()
    
    shop_list = ""
    for player, rarity, cost in shop_inventories[user_id]:
        shop_list += f"**{player}** - *{rarity}* - Price: ${cost}\n"
    
    embed = create_embed("Shop Inventory", shop_list, discord.Color.dark_orange())
    embed.set_footer(text="Use /buy <player> to purchase a player. (Case sensitive)")
    await interaction.response.send_message(embed=embed)

@client.tree.command(name="buy")
async def buy(interaction: discord.Interaction, player: str):
    user_id = str(interaction.user.id)
    if user_id not in shop_inventories or not shop_inventories[user_id]:
        embed = create_embed("Buy Player", "No active shop inventory. Use /shop first.", discord.Color.dark_red())
        await interaction.response.send_message(embed=embed)
        return

    for item in shop_inventories[user_id]:
        p_name, rarity, cost = item
        if p_name == player:
            user_cash = cash.get(user_id, 0)
            if user_cash < cost:
                embed = create_embed("Buy Player", f"Insufficient funds! You need ${cost} but have ${user_cash}.", discord.Color.dark_red())
                await interaction.response.send_message(embed=embed)
                return
            cash[user_id] = user_cash - cost
            if user_id not in inventories:
                inventories[user_id] = set()
            inventories[user_id].add(p_name)
            shop_inventories[user_id].remove(item)
            save_data()
            embed = create_embed("Purchase Successful", f"You bought **{p_name}** for ${cost}!", discord.Color.green())
            await interaction.response.send_message(embed=embed)
            return

    embed = create_embed("Buy Player", "That player is not available in your shop inventory.", discord.Color.dark_red())
    await interaction.response.send_message(embed=embed)

client.run(TOKEN)

# Hey, if ur reading this, ts is a message left by the original code developer (specific_aura on discord), navigate over to 'TOKEN' and add ur Bot token.
# Make sure all intents are enabled and that the bot is in the server.
# The only thing that needa to be configured is the bot token, everything else is already ready!
# If you dont know what ur doing, DONT edit the code at all (inventory and stuffs is saved in data.json (the other file))
# You can add your own players by navigating over to rarities which is on line 22 and adding players below the signated rairty (dont do it if u dont know how to..)
# Credits would be nice..
