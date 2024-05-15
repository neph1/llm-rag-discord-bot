


import importlib


def load_extensions(config):
    extensions = list()
    if config.get('GITHUB', None):
        extension_module = importlib.import_module('extensions.github')
        
        extensions.extend(extension_module.get_extensions())

    if config.get('CHROMA', None):
        extension_module = importlib.import_module('extensions.chroma_db_mdr')
        extensions.extend(extension_module.get_extensions())
    else:
        print('No chromadb. Running without')
    return extensions

def handle_extensions(extensions, openai_backend, user: str, prompt, history):
    for extension in extensions:
        if not extension.check_for_trigger(prompt=prompt):
            continue
        results = extension.call(prompt=prompt)
        extension_history = results
        if not results:
            continue

        if openai_backend:
            prompt = extension.modify_prompt_for_llm(prompt=prompt, results=results, user=user)
            response = openai_backend.query(prompt=prompt)
            continue
        if response:
            break
        response = extension.modify_response_for_user(results, user=user)

    if not response and openai_backend:
        # Just LLM inference
        response = openai_backend.query(f'The user {user} has directed a message to you. History: {history}.\n\nRespond appropriately to the message.\n\n{prompt}')