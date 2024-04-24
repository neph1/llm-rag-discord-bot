# bot.py

import discord
import yaml

from chroma_db.chroma_db import ChromaDb
from openai_backend import OpenAIBackend

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


TOKEN = config['DISCORD_TOKEN']
GUILD = config['DISCORD_SERVER']

intents = discord.Intents.default()

client = discord.Client(intents=intents)

openai_backend = None
if config.get('OPENAI_HOST', None):
    openai_backend = OpenAIBackend(host=config['OPENAI_HOST'], port=config['OPENAI_PORT'], endpoint=config['OPENAI_ENDPOINT'], system_prompt=config['SYSTEM_PROMPT'])
else:
    print('No openai host. Running without')

chromaDb = None
if config.get('CHROMA_PATH', None):
    chromaDb = ChromaDb(config['CHROMA_PATH'])
else:
    print('No chromadb. Running wihtout')

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')


@client.event
async def on_member_join(member: discord.Member):
    if not config['GREET_NEW_MEMBERS']:
        return
    if openai_backend:
        greeting = openai_backend.query(f'The user {member.name} has joined the server. Greet them in a friendly manner.')
    else:
        greeting = config['STANDARD_GREETING']
    await member.create_dm()
    await member.dm_channel.send(greeting)
    

@client.event
async def on_message(message: discord.Message):
    if message.author == client.user:
        return
    messages = [message async for message in message.channel.history(limit=config['CHANNEL_HISTORY'])]
    history = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
    if client.user in message.mentions or message.channel.type == discord.ChannelType.private:

        prompt = message.content
        if chromaDb:
            rag_results = chromaDb.inference(message.content)

        if openai_backend:
            if rag_results:
                prompt = f'Use the information in the following snippets to help you. Use only facts found in snippets when responding. If it contains an appropriate link, copy it: {rag_results}. Original prompt: {prompt}'
            response = openai_backend.query(f'The user {message.author.name} has directed a message to you. Chat history: {history}. Respond appropriately to the message. {prompt}')
        elif rag_results:
            response = f'I found these pieces of information in the database. I hope they will help! Otherwise, don\'t hesistate to reach out. {rag_results}'

        if response:
            await message.channel.send(response)
        else:
            print('Something went wrong. No response to send')

client.run(TOKEN)

