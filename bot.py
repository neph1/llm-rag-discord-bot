# bot.py

import discord
import yaml

from chroma_db.chroma_db import ChromaDb
from extension import ExtensionInterface
from openai_backend import OpenAIBackend
from pull_request.pull_request import PullRequest

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)


TOKEN = config['DISCORD_TOKEN']
GUILD = config['DISCORD_SERVER']

intents = discord.Intents.default()

client = discord.Client(intents=intents)

extensions = list()

openai_backend = None
if config.get('OPENAI_HOST', None):
    openai_backend = OpenAIBackend(host=config['OPENAI_HOST'], port=config['OPENAI_PORT'], endpoint=config['OPENAI_ENDPOINT'], system_prompt=config['SYSTEM_PROMPT'])
else:
    print('No openai host. Running without')

github = None
if config.get('GITHUB', None):
    github = PullRequest()
    extensions.append(github)
chromaDb = None
if config.get('CHROMA_PATH', None):
    chromaDb = ChromaDb(config['CHROMA_PATH'])
    extensions.append(chromaDb)
else:
    print('No chromadb. Running without')

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
    """ Reacts to messages in server
    
    Loops through extensions (will only successfully call one extension per message)
        Check if message triggers extension
        Call extension for a result
        If LLM is available: Modify prompt to suit llm inference, or
        Package response to suit user

        If no suitable response and LLM available, send prompt to LLM

        Return response to channel
    """

    if message.author == client.user:
        return
    messages = [message async for message in message.channel.history(limit=config['CHANNEL_HISTORY'])]
    history = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
    if client.user in message.mentions or message.channel.type == discord.ChannelType.private:

        prompt = message.content
        response = None
        for extension in extensions:
            if not extension.check_for_trigger(prompt=prompt):
                continue
            results = extension.call(prompt=prompt)
            if not results:
                continue

            if openai_backend:
                prompt = extension.modify_prompt_for_llm(prompt=prompt, results=results, user=message.author.name)
                response = openai_backend.query(prompt=prompt)
                continue
            if response:
                break
            response = extension.modify_response_for_user(response, user=message.author.name)


        if not response and openai_backend:
            # Just LLM inference
            response = openai_backend.query(f'The user {message.author.name} has directed a message to you. Chat history: {history}.\n\nRespond appropriately to the message.\n\n{prompt}')
        

        if response:
            response_lines = response.split('\n\n')
            output = ''
            for line in response_lines:
                if len(output) + len(line) < 2000:
                    output += line
                else:
                    await message.channel.send(output)
                    output = line
            if output:
                await message.channel.send(output)
        else:
            print('Something went wrong. No response to send')

client.run(TOKEN)

