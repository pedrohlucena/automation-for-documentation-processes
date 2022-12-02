import os
from library.confluence import ConfluenceIntegration
from library.jira import JiraIntegration
from library.discord import Discord
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class TransferMdContentToConfluence:
    def __init__(self):
        self.md_file_path = os.path.join(
            os.getenv('DOCS_FOLDER_IN_DOC_CONTENT_REPOSITORY_PATH'),
            'comportamentos',
            'post-behavior.md'
        )

        self.parent_page_title = 'Parent'

        self.card_key = 'KEY-1111'

        self.splitted_lines_of_the_md = self.__split_md_lines(
            self.__get_md_content()
        )

        self.card_url = f'{os.getenv("ICLUBS_ATLASSIAN_BASE_URL")}/browse/{self.card_key}'

        self.doc_reviewer_channel_ids = [os.getenv('ART_CHANNEL_ID'), os.getenv('LETICIA_CHANNEL_ID')]

        self.confluence_integration = ConfluenceIntegration()
        self.jira_integration = JiraIntegration()
        self.discord_integration = Discord()

    def __extract_confluence_page_title_from_md_line(self, line):
        self.confluence_page_title = line[1:].strip()
        
    def __take_off_sidebar_position_of_confluence_page_body(self, md_lines, index_of_first_hifen_sequence):
        self.confluence_page_body = md_lines[index_of_first_hifen_sequence+4:]

    def __mount_the_final_confluence_page_body(self):
        self.confluence_page_body = '\n'.join(self.confluence_page_body)

    def __extract_and_clean_info_from_md_lines(self, md_lines):
        for index, line in enumerate(md_lines):
            if line.__contains__('---') and md_lines[index+1].__contains__('sidebar_position:'):
                self.__take_off_sidebar_position_of_confluence_page_body(md_lines, index)
            if line.__contains__('#'):
                self.__extract_confluence_page_title_from_md_line(line)
                continue
        
        self.__mount_the_final_confluence_page_body()

    def __get_md_content(self):
        md_content = ''
        with open(self.md_file_path, 'r', encoding='utf8') as file:
            md_content = file.read()
        return md_content

    def __split_md_lines(self, md_content):
        return md_content.splitlines()        
        
    def __transfer_md_content_to_confluence(self):
        parent_page_id = self.confluence_integration.get_page_id(self.parent_page_title)
        self.confluence_integration.pass_to_confluence(parent_page_id, self.page_title, self.confluence_page_body)
        
    def __get_card_status(self):
        return self.jira_integration.get_card_status(self.card_key)

    def __move_card_to_review(self):
        self.jira_integration.move_card_to_review(self.card_key)

    def __get_discord_review_message(self):
        return f''':cowboy: Aoba, nova doc de cliente pra revisão :page_with_curl::writing_hand: 
{self.card_url}
Não se esqueça do emoji! :face_holding_back_tears:'''

    def __notify_the_documentation_reviewers(self):
        review_message = self.__get_discord_review_message()
        self.discord_integration.send_message(self.doc_reviewer_channel_ids, review_message)

    def main(self):
        self.__extract_and_clean_info_from_md_lines()

        self.__transfer_md_content_to_confluence()

        card_status = self.__get_card_status()
        if card_status != "Review":
            self.__move_card_to_review()
            self.__notify_the_documentation_reviewers()

tmc = TransferMdContentToConfluence()
tmc.main()