# llm-rag-discord-bot

Just a little toy project, llm backed discord bot with extension support. Inspired by my own koboldcpp fork.

Discuss pull requests (doesn't persist the PR data atm)  :

neph — Today at 10:01 PM  
what happened in the parse_utils file in pr#77? do you have any recommendations or improvements?  

  
Elid Gald [Bot]  
APP  
 — Today at 10:02 PM  
It appears that the parse_utils file in PR #77 has undergone significant changes. Here's a summary of the changes:1. Added sanitize_json function: A new function sanitize_json was added to parse and sanitize JSON data. This function takes a JSON string as input, parses it, and returns a sanitized JSON object.  
Added load_item_spawners function: A new function load_item_spawners was added to load item spawners from a JSON file. This function takes a JSON string as input, parses it, and returns a list of ItemSpawner objects.  
Updated load_mob_spawners function: The load_mob_spawners function was updated to load mob spawners from a JSON file. This function takes a JSON string as input, parses it, and returns a list of MobSpawner objects.As for recommendations or improvements, here are a few suggestions:1. Consider adding type hints: The sanitize_json and load_item_spawners functions could benefit from type hints to indicate the expected input and output types.  
Use a more robust JSON parsing library: The json module in Python is not the most robust JSON parsing library. Consider using a library like ujson or ijson for better performance and error handling.  
Add error handling: The sanitize_json and load_item_spawners functions could benefit from error handling to handle cases where the input JSON is invalid or malformed.  
Consider using a more efficient data structure: The load_item_spawners function returns a list of ItemSpawner objects. Consider using a more efficient data structure like a dictionary or a set to store the item spawners, especially if the list is large.  
Add documentation: The sanitize_json and load_item_spawners functions could benefit from documentation to explain their purpose, input parameters, and return values.  
Overall, the changes in PR #77 appear to be focused on improving the parsing and loading of JSON data in the parse_utils file. However, there are opportunities to improve the code further by adding type hints, error handling, and documentation.  
  
  
Search a chroma db:  
  
neph — 04/24/2024 8:02 AM  
@Elid Gald [Bot] how do i get started? [with LlamaTale]  
  
  
Elid Gald [Bot]  
APP  
 — 04/24/2024 8:04 AM  
Ah, a curious soul! adjusts monocle Getting started with LlamaTale is quite simple, my dear. First, you'll need to download the repository from GitHub. winks You can do that by running git clone git@github.com:neph1/LlamaTale.git in your terminal. Once you have the repository, you can install the required dependencies by running pip install -r requirements.txt. tips hat  
Now, to start the tale, you can run python -m stories.prancingllama.story in your terminal. This will launch the demo, and you'll be able to create and play your very own story! excitedly If you want to play in a browser, you can add the --web flag when running the demo, and connect to http://localhost:8180/tale/story. smirks  
But wait, there's more! winks If you have a character card, you can skip the character creation process by adding --.original to the command. nods  
So, my dear, what are you waiting for? grins Dive into the world of LlamaTale and create your own adventure! winks  
