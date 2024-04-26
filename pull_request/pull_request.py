

import json
import re

import requests
import yaml

from extension import ExtensionInterface


class PullRequest(ExtensionInterface):

    def __init__(self):
        with open('github_config.yaml', 'r') as file:
            self.config = yaml.safe_load(file)

    def check_for_trigger(self, prompt: str) -> bool:
        return 'pull request' in prompt or 'pr#' in prompt

    def call(self, prompt: str):
        # Extract the pull request number from the prompt
        pull_request_number = self._extract_pull_request_number(prompt)
        
        if not pull_request_number:
            return None
        headers={
                "Authorization": f"token {self.config['token']}"
            }
        
        # Get the pull request details
        response = requests.get(
            url=f"https://api.github.com/repos/{self.config['repository']}/pulls/{pull_request_number}",
            headers=headers
        )

        pull_request_data = response.json()

        results = {}
        results['title'] = pull_request_data['title']
        results['body'] = pull_request_data['body']
        results['state'] = pull_request_data['state']
        results['draft'] = pull_request_data['draft']
        results['user'] = pull_request_data['user']['login']
        results['created_at'] = pull_request_data['created_at']
        results['updated_at'] = pull_request_data['updated_at']
        results['url'] = pull_request_data['html_url']

        comments = requests.get(
            url=pull_request_data['comments_url'],
            headers=headers
        )

        results['comments'] = comments.json()

        reviews = requests.get(
            url=pull_request_data['review_comments_url'],
            headers=headers
        ) 

        results['reviews'] = reviews.json()
        
        diff = requests.get(
            url= response.json()['diff_url'],
            headers=headers
        )

        results['diff'] = diff.text

        #print(json.dumps(results, indent=4))

        return json.dumps(results, indent=4)

    def modify_prompt_for_llm(self, prompt: str, results: str, user: str):
        return f'The user {user} has asked you to check this pull request. Pull request: {results}.\n\nRespond appropriately to the message.\n\n{prompt}'
    
    def modify_response_for_user(self, results, user):
        return f'Hey {user}, I found this information for the pull request: {results}'
    
    def _extract_pull_request_number(self, prompt: str):
        pull_request_number = re.search(r'pull request #[0-9]+', prompt)
        if not pull_request_number:
            pull_request_number = re.search(r'pr#[0-9]+', prompt)
        if not pull_request_number:
            return None
        return pull_request_number.group(0).split("#")[1]
    