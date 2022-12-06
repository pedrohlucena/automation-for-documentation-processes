import os
from atlassian import Confluence
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class ConfluenceIntegration:
    def __init__(self):
        self.iclubs_atlassian_base_url = os.getenv('ICLUBS_ATLASSIAN_BASE_URL')

        self.confluence_instance = Confluence(
            url = self.iclubs_atlassian_base_url,
            username = os.getenv('ICLUBS_ATLASSIAN_USERNAME'),
            password = os.getenv('ATLASSIAN_API_KEY'),
            cloud=True
        )

        self.confluence_space_key = os.getenv('CONFLUENCE_SPACE_KEY')

    def pass_to_confluence(self, parent_id, title, body):
        self.confluence_instance.update_or_create(parent_id, title, body, representation='storage', full_width=False)

    def get_page_id_by_name(self, page_title):
        return self.confluence_instance.get_page_id(self.confluence_space_key, page_title)

    def get_page_url_by_name(self, page_title):
        page_id = self.get_page_id_by_name(page_title)
        return f'{self.iclubs_atlassian_base_url}/wiki/spaces/{self.confluence_space_key}/pages/{page_id}'