import os
from atlassian import Confluence
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class ConfluenceIntegration:
    def __init__(self):
        self.confluence_instance = Confluence(
            url = os.getenv('ICLUBS_ATLASSIAN_BASE_URL'),
            username = os.getenv('ICLUBS_ATLASSIAN_USERNAME'),
            password = os.getenv('ATLASSIAN_API_KEY'),
            cloud=True
        )

        self.confluence_space_key = os.getenv('CONFLUENCE_SPACE_KEY')

    def pass_to_confluence(self, parent_id, title, body):
        self.confluence_instance.update_or_create(parent_id, title, body, representation='storage', full_width=False)

    def get_page_id(self, page_title):
        return self.confluence_instance.get_page_id(self.confluence_space_key, page_title)