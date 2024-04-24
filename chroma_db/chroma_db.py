from extension import ExtensionInterface
import chromadb
import os
from os import listdir
from os.path import isfile, join


class ChromaDb(ExtensionInterface):
    chromaCollection = None

    def __init__(self, relative_path: str):
        self.chromaCollection = chromadb.Client().get_or_create_collection(relative_path)
        if not self.chromaCollection:
            print('creating collection')
            self.chromaCollection = chromadb.Client().create_collection(relative_path)
        relative_path = os.getcwd() + '/' + relative_path + '/'
        files = os.listdir(relative_path)
        for f2 in files:
            if f2.endswith('.md'):
                doc = open(relative_path + f2).read()
                split_docs = doc.split('== ')
                docs = []
                entries = []
                id_list = []
                meta_data_list = []
                i = 0
                for d in split_docs:
                    docs = d.split('=== ')
                    page = d.split("\n")[0].replace('\'', '')
                    entries.extend(docs)
                    
                    for d2 in docs:
                        topic = d2.split("\n")[0].replace('\'', '')
                        id_list.append(f'{f2} {i}')
                        meta_data_list.append({'source':f'{f2}', 'page':f'{page}', 'section':f'{topic}'})
                        i = i + 1
                    
                print(f'found data file {f2} {len(entries)}')
                
                self.chromaCollection.add(documents=entries, metadatas=meta_data_list, ids=id_list)        

    def inference(self, newprompt, genparams = {}, max_context = 10000, *args):
        query_string = newprompt
        print(query_string)
        stop_sequence = genparams.get('stop_sequence', [])
        response_length = genparams.get('max_length', 300)
        max_distance = genparams.get('max_distance', 1.5) # TODO
        result_context_factor = genparams.get('result_context_factor', 0.25) #TODO
        n_results = genparams.get('n_results', 2) #TODO
        if not stop_sequence:
            stop_sequence = ['\n']
        
        if stop_sequence:
            query_string = query_string.rsplit(stop_sequence[0], 1)[-1] or query_string
        # TODO: should shorten query anyway if no stop_sequence? or summarize?
        results = self.chromaCollection.query(query_texts=query_string, n_results=n_results)
        if not results:
            return newprompt
        trimmed_results = ''
        num_results = len(results['documents'][0])
        for i in range(0, num_results):
            distance = results['distances'][0][i]
            if distance < max_distance:
                bit = results['documents'][0][i]     
                # replacing line breaks, since they tend to stop the generation when double
                trim = bit.replace('\n', '')
                trimmed_results += f"[SNIPPET]{trim}[/SNIPPET]"
                print(f' {distance} {bit[:15]}')
            else:
                print(f'not using {distance} {bit[:15]}')
        if not trimmed_results:
            return newprompt
        # max tokens for chromadb results is a fraction of max context
        result_max_tokens = int(max_context * result_context_factor)
        if len(newprompt) > max_context - result_max_tokens:
            result_max_tokens -= response_length
        #print(f'result_max_tokens: {result_max_tokens}')
        trimmed_results = (trimmed_results[:result_max_tokens]) if len(trimmed_results) > result_max_tokens else trimmed_results
        max_new_prompt = max_context-result_max_tokens
        newprompt = (newprompt[-(max_new_prompt):]) if len(newprompt) > max_new_prompt else newprompt
        return trimmed_results
