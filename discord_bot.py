# bot.py

import discord
import yaml

from chroma_db.chroma_db import ChromaDb
from openai_backend import OpenAIBackend
from pull_request.pull_request import PullRequest


class DiscordBot(discord.Client):

    def __init__(self, intents, config):
        super().__init__(intents=intents)
        
        extensions = list()

        self.openai_backend = None
        if config.get('OPENAI_HOST', None):
            self.openai_backend = OpenAIBackend(host=config['OPENAI_HOST'], port=config['OPENAI_PORT'], endpoint=config['OPENAI_ENDPOINT'], system_prompt=config['SYSTEM_PROMPT'])
        else:
            print('No openai host. Running without')

        if config.get('GITHUB', None):
            extensions.append(PullRequest())

        if config.get('CHROMA', None):
            extensions.append(ChromaDb())
        else:
            print('No chromadb. Running without')


    async def on_ready(self):
        print(f'{self.user} has connected to Discord!')

    async def on_member_join(self, member: discord.Member):
        if not config['GREET_NEW_MEMBERS']:
            return
        if self.openai_backend:
            greeting = self.openai_backend.query(f'The user {member.name} has joined the server. Greet them in a friendly manner.')
        else:
            greeting = self.config['STANDARD_GREETING']
        await member.create_dm()
        await member.dm_channel.send(greeting)
        
    async def on_message(self, message: discord.Message):
        """ Reacts to messages in server
        
        Loops through extensions (will only successfully call one extension per message)
            Check if message triggers extension
            Call extension for a result
            If LLM is available: Modify prompt to suit llm inference, or
            Package response to suit user

            If no suitable response and LLM available, send prompt to LLM

            Return response to channel
        """
        extension_history = None
        if message.author == self.user:
            return
        messages = [message async for message in message.channel.history(limit=self.config['CHANNEL_HISTORY'])]
        history = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
        if extension_history:
            history = extension_history + "\n" + history
        if self.user in message.mentions or message.channel.type == discord.ChannelType.private:

            prompt = message.content
            response = None
            for extension in self.extensions:
                if not extension.check_for_trigger(prompt=prompt):
                    continue
                results = extension.call(prompt=prompt)
                extension_history = results
                if not results:
                    continue

                if self.openai_backend:
                    prompt = extension.modify_prompt_for_llm(prompt=prompt, results=results, user=message.author.name)
                    response = self.openai_backend.query(prompt=prompt)
                    continue
                if response:
                    break
                response = extension.modify_response_for_user(results, user=message.author.name)


            if not response and self.openai_backend:
                # Just LLM inference
                response = self.openai_backend.query(f'The user {message.author.name} has directed a message to you. History: {history}.\n\nRespond appropriately to the message.\n\n{prompt}')
            

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

# Init

intents = discord.Intents.default()

with open('config.yaml', 'r') as file:
    config = yaml.safe_load(file)

TOKEN = config['DISCORD_TOKEN']
GUILD = config['DISCORD_SERVER']

client = DiscordBot(intents=intents, config=config)
client.run(TOKEN)

