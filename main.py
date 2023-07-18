import discord
from discord.ext import commands
import json
import random
import datetime
import asyncio

# credits to AogiriBling on github, don't try to skid :joy:

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# it loads the database of users.
def load_data():
    try:
        with open('database.json', 'r') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}
    return data

# an autosaver for the database thingy.
def save_data(data):
    with open('database.json', 'w') as file:
        json.dump(data, file)

# this checks if the person exists in database or not.
def user_exists(data, user_id):
    return str(user_id) in data

# automatically creates a new user in the database
def create_user(data, user_id):
    data[str(user_id)] = {
        'balance': 0,
        'last_claimed_daily': None,
        'last_claimed_weekly': None,
    }

# this checks if the user has claimed their daily income
def has_claimed_daily(data, user_id):
    if user_exists(data, user_id):
        last_claimed_daily = data[user_id].get('last_claimed_daily')
        if last_claimed_daily:
            now = datetime.datetime.now()
            delta = now - datetime.datetime.fromisoformat(last_claimed_daily)
            if delta.days < 1:
                return True
    return False

# Set the last claimed daily timestamp for the user
def set_last_claimed_daily(data, user_id):
    if user_exists(data, user_id):
        data[user_id]['last_claimed_daily'] = datetime.datetime.now().isoformat()

# Checks if the user has claimed their weekly income
def has_claimed_weekly(data, user_id):
    if user_exists(data, user_id):
        last_claimed_weekly = data[user_id].get('last_claimed_weekly')
        if last_claimed_weekly:
            now = datetime.datetime.now()
            delta = now - datetime.datetime.fromisoformat(last_claimed_weekly)
            if delta.days < 7:
                return True
    return False

# Set the last claimed weekly timestamp for the user
def set_last_claimed_weekly(data, user_id):
    if user_exists(data, user_id):
        data[user_id]['last_claimed_weekly'] = datetime.datetime.now().isoformat()

@bot.event
async def on_ready():
    print(f'I am god: {bot.user.name}')

@bot.command()
async def balance(ctx):
    """Checks your current balance."""
    data = load_data()
    user_id = str(ctx.author.id)
    if not user_exists(data, user_id):
        create_user(data, user_id)
        save_data(data)
    balance = data[user_id]['balance']

    embed = discord.Embed(title="Balance", description=f"**<@{ctx.author.id}>, your current balance is: `{balance}` coins.**", color=0xFBFBFB)
    await ctx.send(embed=embed)

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def work(ctx):
    """Earn some money by working."""
    data = load_data()
    user_id = str(ctx.author.id)
    if not user_exists(data, user_id):
        create_user(data, user_id)
        save_data(data)
    earnings = random.randint(1, 1000)
    data[user_id]['balance'] += earnings
    save_data(data)

    embed = discord.Embed(title="Work", description=f"**<@{ctx.author.id}>, you earned `{earnings}` coins by working!**", color=0xFBFBFB)
    await ctx.send(embed=embed)

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command()
async def rob(ctx, member: discord.Member):
    """Rob another member's balance."""
    data = load_data()
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    if not user_exists(data, user_id):
        create_user(data, user_id)
        save_data(data)
    if not user_exists(data, target_id):
        create_user(data, target_id)
        save_data(data)
    if user_id == target_id:
        embed = discord.Embed(title="Rob", description=f"**<@{ctx.author.id}>, you can't rob yourself!**", color=0xFBFBFB)
        await ctx.send(embed=embed)
        return
    if data[user_id]['balance'] < 100:
        embed = discord.Embed(title="Rob", description=f"**<@{ctx.author.id}>, you need at least 100 coins to attempt a robbery.**", color=0xFBFBFB)
        await ctx.send(embed=embed)
        return
    if random.random() < 0.5:
        amount = random.randint(1, int(data[target_id]['balance'] * 0.5))
        data[user_id]['balance'] += amount
        data[target_id]['balance'] -= amount
        save_data(data)
        embed = discord.Embed(title="Rob", description=f"**<@{ctx.author.id}>, you successfully robbed {member.mention} and got away with `{amount}` coins!**", color=0xFBFBFB)
        await ctx.send(embed=embed)
    else:
        fine = random.randint(1, int(data[user_id]['balance'] * 0.25))
        data[user_id]['balance'] -= fine
        save_data(data)
        embed = discord.Embed(title="Rob", description=f"**<@{ctx.author.id}>, you were caught while trying to rob {member.mention} and had to pay a fine of `{fine}` coins.**", color=0xFBFBFB)
        await ctx.send(embed=embed)

@work.error
async def work_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Work", description="**This command is on cooldown. Please try again later.**", color=0xFBFBFB)
        await ctx.send(embed=embed)

@rob.error
async def rob_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        embed = discord.Embed(title="Rob", description="**This command is on cooldown. Please try again later.**", color=0xFBFBFB)
        await ctx.send(embed=embed)

@bot.command()
async def leaderboard(ctx):
    """Check the leaderboard of the richest users. for example the god of awesomeness, Bling!"""
    data = load_data()

    sorted_users = sorted(data.items(), key=lambda x: x[1]['balance'], reverse=True)

    embed = discord.Embed(title="Leaderboard", description="Top 10 Richest Users:", color=0xFBFBFB)
    for idx, (user_id, user_data) in enumerate(sorted_users[:10], start=1):
        member = ctx.guild.get_member(int(user_id))
        if member:
            username = member.display_name
        else:
            username = f"{user_id}"
        balance = user_data['balance']
        embed.add_field(name=f"{idx}. {username}", value=f"<@{username}>'s Balance: `{balance}` coins", inline=False)

    await ctx.send(embed=embed)

@bot.command()
async def give(ctx, amount: int, member: discord.Member):
    """Give money to another user. like prefix give amount username or user id"""
    data = load_data()
    user_id = str(ctx.author.id)
    target_id = str(member.id)
    if not user_exists(data, user_id):
        create_user(data, user_id)
        save_data(data)
    if not user_exists(data, target_id):
        create_user(data, target_id)
        save_data(data)
    if data[user_id]['balance'] < amount:
        embed = discord.Embed(title="Give", description=f"**<@{ctx.author.id}>, you don't have enough coins to give that amount.**", color=0xFBFBFB)
        await ctx.send(embed=embed)
        return
    data[user_id]['balance'] -= amount
    data[target_id]['balance'] += amount
    save_data(data)

    embed = discord.Embed(title="Give", description=f"**<@{ctx.author.id}> gave `{amount}` coins to {member.mention}!**", color=0xFBFBFB)
    await ctx.send(embed=embed)

@commands.cooldown(1, 86400, commands.BucketType.user)  # 24 hours cooldown = 86400 seconds cooldown
@bot.command()
async def daily(ctx):
    """Claim your daily income."""
    data = load_data()
    user_id = str(ctx.author.id)
    if not user_exists(data, user_id):
        create_user(data, user_id)
        save_data(data)
    if has_claimed_daily(data, user_id):
        last_claimed_daily = datetime.datetime.fromisoformat(data[user_id]['last_claimed_daily'])
        next_claim = last_claimed_daily + datetime.timedelta(days=1)
        remaining_time = next_claim - datetime.datetime.now()
        remaining_time = remaining_time.total_seconds()
        remaining_time = int(remaining_time)
        embed = discord.Embed(title="Daily", description=f"**You have already claimed your daily income. Please come back in `{remaining_time} seconds`.**", color=0xFBFBFB)
        await ctx.send(embed=embed)
        return
    income = 10000
    data[user_id]['balance'] += income
    set_last_claimed_daily(data, user_id)
    save_data(data)
    embed = discord.Embed(title="Daily", description=f"**You claimed `{income}` coins as your daily income!**", color=0xFBFBFB)
    await ctx.send(embed=embed)

@commands.cooldown(1, 604800, commands.BucketType.user)  # 1 week cooldown = 604800 seconds cooldown
@bot.command()
async def weekly(ctx):
    """Claim your weekly income."""
    data = load_data()
    user_id = str(ctx.author.id)
    if not user_exists(data, user_id):
        create_user(data, user_id)
        save_data(data)
    if has_claimed_weekly(data, user_id):
        last_claimed_weekly = datetime.datetime.fromisoformat(data[user_id]['last_claimed_weekly'])
        next_claim = last_claimed_weekly + datetime.timedelta(days=7)
        remaining_time = next_claim - datetime.datetime.now()
        remaining_time = remaining_time.total_seconds()
        remaining_time = int(remaining_time)
        embed = discord.Embed(title="Weekly", description=f"**You have already claimed your weekly income. Please come back in `{remaining_time} seconds`.**", color=0xFBFBFB)
        await ctx.send(embed=embed)
        return
    income = 100000
    data[user_id]['balance'] += income
    set_last_claimed_weekly(data, user_id)
    save_data(data)
    embed = discord.Embed(title="Weekly", description=f"**You claimed `{income}` coins as your weekly income!**", color=0xFBFBFB)
    await ctx.send(embed=embed)

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandOnCooldown):
        remaining_time = int(error.retry_after)
        embed = discord.Embed(title="Cooldown", description=f"**You are on cooldown. Please try again in `{remaining_time} seconds`.**", color=0xFBFBFB)
        await ctx.send(embed=embed)
    elif isinstance(error, commands.CommandNotFound):
        embed = discord.Embed(title="Invalid Command", description="**Invalid command used.**", color=0xFBFBFB)
        await ctx.send(embed=embed)

# put your discord bot token in here.
bot.run('Your discord bot token')
