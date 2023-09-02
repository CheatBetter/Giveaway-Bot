"""
Copyright 2023 CheatBetter

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the “Software”), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

Join Us
"""
import discord
from discord.ext import commands
import sqlite3
import random

# Initialize the bot
bot = commands.Bot(command_prefix='!')

# Connect to the SQLite database (create it if it doesn't exist)
conn = sqlite3.connect('giveaways.db')
cursor = conn.cursor()

# Create a table for giveaway entries if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS giveaway_entries (
        user_id INTEGER,
        giveaway_id INTEGER
    )
''')
conn.commit()

# Create a table for past giveaway winners if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS giveaway_winners (
        user_id INTEGER,
        giveaway_id INTEGER
    )
''')
conn.commit()

# Global variable to track the current giveaway
current_giveaway = None

# Event: Bot is ready
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

# Command: Start a giveaway
@bot.command()
async def start_giveaway(ctx, prize, duration_minutes: int):
    global current_giveaway

    if current_giveaway:
        await ctx.send('A giveaway is already in progress.')
    else:
        current_giveaway = {
            'host': ctx.author,
            'prize': prize,
            'end_time': ctx.message.created_at + discord.Duration(minutes=duration_minutes),
            'entries': set()
        }

        await ctx.send(f'A new giveaway for {prize} has started! Type "!enter" to join. This giveaway ends in {duration_minutes} minutes.')

# Command: Enter the giveaway
@bot.command()
async def enter(ctx):
    global current_giveaway

    if current_giveaway and ctx.author not in current_giveaway['entries']:
        current_giveaway['entries'].add(ctx.author)
        await ctx.send(f'{ctx.author.mention} has entered the giveaway for {current_giveaway["prize"]}!')

# Command: Draw the winner of the giveaway
@bot.command()
async def draw_winner(ctx):
    global current_giveaway

    if ctx.author != current_giveaway['host']:
        await ctx.send('Only the giveaway host can draw a winner.')
    elif not current_giveaway['entries']:
        await ctx.send('No one has entered the giveaway yet.')
    else:
        winner = random.choice(list(current_giveaway['entries']))
        await ctx.send(f'Congratulations to {winner.mention} for winning the giveaway for {current_giveaway["prize"]}!')

        # Add the winner to the past winners table
        cursor.execute('INSERT INTO giveaway_winners (user_id, giveaway_id) VALUES (?, ?)', (winner.id, ctx.message.id))
        conn.commit()

        current_giveaway = None

# Command: View past giveaway winners
@bot.command()
async def past_winners(ctx):
    cursor.execute('SELECT user_id FROM giveaway_winners')
    winners = cursor.fetchall()

    if winners:
        winner_list = "\n".join([f'<@{winner[0]}>' for winner in winners])
        await ctx.send(f'Past giveaway winners:\n{winner_list}')
    else:
        await ctx.send('No past giveaway winners.')

# Replace 'YOUR_BOT_TOKEN' with your bot's token
bot.run('YOUR_BOT_TOKEN')
