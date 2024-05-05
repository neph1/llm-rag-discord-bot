import yaml
from extension import ExtensionInterface
import chromadb
import os


class ChromaDb(ExtensionInterface):
    chromaCollection = None

    def __init__(self):
        with open('chromadb_config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)
        path = 'chroma_db/data'
        collection = self.config['collection']
        self.chromaCollection = chromadb.Client().get_or_create_collection(collection)
        if not self.chromaCollection:
            print('creating collection')
            self.chromaCollection = chromadb.Client().create_collection(collection)
        collection = os.getcwd() + '/' + path + '/' + collection + '/'
        files = os.listdir(collection)
        extension = self.config['extension']
        doc_split1 = self.config['doc_split1']
        doc_split2 = self.config['doc_split2']
        for f2 in files:
            if f2.endswith(extension):
                doc = open(collection + f2).read()
                split_docs = doc.split(doc_split1)
                docs = []
                entries = []
                id_list = []
                meta_data_list = []
                i = 0
                for d in split_docs:
                    docs = d.split(doc_split2)
                    page = d.split("\n")[0].replace('\'', '')
                    entries.extend(docs)
                    
                    for d2 in docs:
                        topic = d2.split("\n")[0].replace('\'', '')
                        id_list.append(f'{f2} {i}')
                        meta_data_list.append({'source':f'{f2}', 'page':f'{page}', 'section':f'{topic}'})
                        i = i + 1
                    
                print(f'found data file {f2} {len(entries)}')
                
                self.chromaCollection.add(documents=entries, metadatas=meta_data_list, ids=id_list)        


    def check_for_trigger(self, prompt: str) -> bool:
        return True

    def call(self, prompt):
        stop_sequence = self.config.get('stop_sequence', None)
        response_length = self.config.get('response_length', 1000)
        max_distance = self.config.get('max_distance', 1.5)
        result_context_factor = self.config.get('result_context_factor', 0.25)
        n_results = self.config.get('num_results', 3)
        if not stop_sequence:
            stop_sequence = ['\n']
        
        if stop_sequence:
            prompt = prompt.rsplit(stop_sequence[0], 1)[-1] or prompt
        # TODO: should shorten query anyway if no stop_sequence? or summarize?
        results = self.chromaCollection.query(query_texts=prompt, n_results=n_results)
        if not results:
            return prompt
        trimmed_results = ''
        num_results = len(results['documents'][0])
        for i in range(0, num_results):
            distance = results['distances'][0][i]
            snippet = ''
            if distance < max_distance:
                snippet = results['documents'][0][i]     
                # replacing line breaks, since they tend to stop the generation when double
                trimmed_results += f"[SNIPPET]{snippet}[/SNIPPET]\n\n"
                print(f' {distance} {snippet[:15]}')
            else:
                print(f'not using {distance} {snippet[:15]}')
        if not trimmed_results:
            return prompt
        # max tokens for chromadb results is a fraction of max context
        result_max_tokens = int(self.config['max_context'] * result_context_factor)
        if len(prompt) > self.config['max_context'] - result_max_tokens:
            result_max_tokens -= response_length
        #print(f'result_max_tokens: {result_max_tokens}')
        trimmed_results = (trimmed_results[:result_max_tokens]) if len(trimmed_results) > result_max_tokens else trimmed_results
        return trimmed_results

    def modify_prompt_for_llm(self, prompt: str, results: str, user: str) -> str:
        return f'{results}.\n\nThe user {user} has directed a message to you. Respond appropriately to the message using the information inside the [SNIPPET] tags. Use only facts found in snippets when responding. If it contains an appropriate link, copy it\n\n: User message:{prompt}'
                
    def modify_response_for_user(self, results: str, user: str) -> str:
        return f'I found these pieces of information in the database. I hope they will help! Otherwise, don\'t hesitate to reach out. {results}'