# bot.py

import discord
import yaml

from bot_methods import handle_extensions, load_extensions
from openai_backend import OpenAIBackend


class DiscordBot(discord.Client):

    def __init__(self, intents, config):
        super().__init__(intents=intents)
        
        self.extensions = list()
        self.history_length = config['CHANNEL_HISTORY']
        self.openai_backend = None
        if config.get('OPENAI_HOST', None):
            self.openai_backend = OpenAIBackend(host=config['OPENAI_HOST'], port=config['OPENAI_PORT'], endpoint=config['OPENAI_ENDPOINT'], system_prompt=config['SYSTEM_PROMPT'])
        else:
            print('No openai host. Running without')

        self.extensions = load_extensions(config)

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
        messages = [message async for message in message.channel.history(limit=self.history_length)]
        history = "\n".join([f"{msg.author.name}: {msg.content}" for msg in messages])
        if extension_history:
            history = extension_history + "\n" + history
        if self.user in message.mentions or message.channel.type == discord.ChannelType.private:

            prompt = message.content
            response = handle_extensions(self.extensions, self.openai_backend, message.author.name, prompt, history)

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

