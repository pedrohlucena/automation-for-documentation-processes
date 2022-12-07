import json
import os
from atlassian import Jira
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class JiraIntegration:
    def __init__(self):
        self.jira_instance = Jira(
            url = os.getenv('ICLUBS_ATLASSIAN_BASE_URL'),
            username = os.getenv('ICLUBS_ATLASSIAN_USERNAME'),
            password = os.getenv('ATLASSIAN_API_KEY'),
            cloud=True
        )

        self.pedro_atlassian_account_id = os.getenv('PEDRO_ATLASSIAN_ACCOUNT_ID') 

    def get_card_status(self, card_key):
        return self.jira_instance.get_issue_status(card_key)

    def move_card_to_review(self, card_key):
        self.jira_instance.set_issue_status(card_key, 'Review', fields=None)

    def get_card_name(self, card_key):
        return self.jira_instance.issue(card_key)

    def watch_card(self, card_key):
        self.jira_instance.issue_add_watcher(card_key, self.pedro_atlassian_account_id)