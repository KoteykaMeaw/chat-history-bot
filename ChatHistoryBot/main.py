import discord
from settings import TOKEN
from settings import DATABASE
from discord.ext import commands
from discord import app_commands
import sqlite3 as sql

bot = commands.Bot(command_prefix='/', intents=discord.Intents.all())

conn = sql.connect(DATABASE)
c = conn.cursor()


@bot.event
async def on_ready():
    print("Bot is Up and Ready!")
    try:
        synched = await bot.tree.sync()
        print(f'Synched {len(synched)} command(s)')
    except Exception as e:
        print(e)

    c.execute('''CREATE TABLE IF NOT EXISTS history (username TEXT, message TEXT)''')

    conn.commit()

@bot.event
async def on_message(message):
    c.execute("INSERT INTO history VALUES (?, ?)", (message.author.name, message.content))



@bot.tree.command(name='messages', description='everything you said')
async def messages(interaction: discord.Integration):
    messagez = []

    c.execute("SELECT message FROM history WHERE username = ?", (interaction.user.name,))
    msgs = c.fetchall()

    for message in msgs:
        messagez.append(message[0])

    if messagez:
        all_messages = "\n".join(messagez)
        await interaction.user.send(f'Hello {interaction.user.mention}! Here are all your messages:\n{all_messages}')
    else:
        await interaction.user.send(f'Hello {interaction.user.mention}! You have not sent any messages.')

    await interaction.response.send_message(f'Sent messages in DM!', ephemeral=True)


@bot.tree.command(name='messageselse', description='everything someone said')
async def messageselse(interaction: discord.Integration, target_user: discord.User):
    messagez = []

    c.execute("SELECT message FROM history WHERE username = ?", (target_user.name,))
    msgs = c.fetchall()

    for message in msgs:
        messagez.append(message[0])

    if messagez:
        all_messages = "\n".join(messagez)
        await interaction.user.send(f'Hello {interaction.user.mention}! Here are all your messages:\n{all_messages}')
    else:
        await interaction.user.send(f'Hello {interaction.user.mention}! You have not sent any messages.')

    await interaction.response.send_message(f'Sent messages in DM of {target_user.name}!', ephemeral=True)

@bot.tree.command(name='clear', description='clear your messages')
async def clear(interaction: discord.Integration):
    c.execute("DELETE FROM history WHERE username = ? ", (interaction.user.name,))
    conn.commit()
    await interaction.response.send_message(f'All messages of {interaction.user.mention} have been cleared.', ephemeral=True)

@bot.tree.command(name='clearelse', description='clear messages of a user')
@commands.has_permissions(administrator=True)
async def clearelse(interaction: discord.Integration, target_user: discord.User):
    c.execute("DELETE FROM history WHERE username = ?", (target_user.name,))
    conn.commit()
    await interaction.response.send_message(f'All messages of {target_user.mention} have been cleared.', ephemeral=True)





bot.run(token=TOKEN)
