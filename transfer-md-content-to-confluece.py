import os
import markdown
from library.confluence import ConfluenceIntegration
from library.jira import JiraIntegration
from library.discord import Discord
from dotenv import load_dotenv, find_dotenv
from markdown.extensions.tables import TableExtension 

load_dotenv(find_dotenv())

class TransferMdContentToConfluence:
    def __init__(self):
        self.md_file_path = os.path.join(
            os.getenv('DOCS_FOLDER_IN_DOC_CONTENT_REPOSITORY_PATH'),
            'core',
            'comportamentos',
            'pedro-teste.md'
        )
        
        print(self.md_file_path)

        self.parent_page_title = '(Cliente) Core'

        self.card_key = 'IC-7332'

        self.card_url = f'{os.getenv("ICLUBS_ATLASSIAN_BASE_URL")}/browse/{self.card_key}'

        self.doc_reviewer_channel_ids = [os.getenv('ART_CHANNEL_ID'), os.getenv('LETICIA_CHANNEL_ID')]

        self.confluence_integration = ConfluenceIntegration()
        self.jira_integration = JiraIntegration()
        self.discord_integration = Discord()

    def __extract_confluence_page_title_from_md_line(self, line):
        self.confluence_page_title = line[1:].strip()
        
    def __take_off_sidebar_position_of_confluence_page_body(self, index_of_first_hifen_sequence):
        self.confluence_page_body = self.confluence_page_body[index_of_first_hifen_sequence+4:]

    def __join_md_lines_into_a_md_content(self, md_lines):
        return '\n'.join(md_lines)

    def __convert_md_content_to_html(self, md_content):
        md_content_converted_to_html = markdown.markdown(
            md_content,
            extensions=[TableExtension(use_align_attribute=True)]
        )
        return md_content_converted_to_html

    def __mount_the_final_confluence_page_body(self):
        md_content = self.__join_md_lines_into_a_md_content(self.confluence_page_body)
        md_content_converted_to_html = self.__convert_md_content_to_html(md_content)
        self.confluence_page_body = md_content_converted_to_html

    def __set_initial_confluence_page_body(self, md_lines):
        self.confluence_page_body = md_lines

    def __take_off_page_title_of_confluence_page_body(self):
        self.confluence_page_body = self.confluence_page_body[1:]

    def __the_line_is_the_md_title(self, line):
        if line.__contains__('#') and line.__contains__('GET') or line.__contains__('POST') or line.__contains__('PUT'):
            return True
        else:
            return False

    def __it_is_sidebar_position(self, index, line, md_lines):
        return line.__contains__('---') and md_lines[index+1].__contains__('sidebar_position:')

    def __extract_and_clean_info_from_md_lines(self, md_lines):
        self.__set_initial_confluence_page_body(md_lines)

        sidebar_position_if_statement_already_run = False
        title_if_statement_already_run = False
        for index, line in enumerate(md_lines):
            if self.__it_is_sidebar_position(index, line, md_lines) and not sidebar_position_if_statement_already_run:
                self.__take_off_sidebar_position_of_confluence_page_body(index)
                sidebar_position_if_statement_already_run = True
            if self.__the_line_is_the_md_title(line) and not title_if_statement_already_run:
                self.__extract_confluence_page_title_from_md_line(line)
                self.__take_off_page_title_of_confluence_page_body()
                title_if_statement_already_run = True
        
        self.__mount_the_final_confluence_page_body()

    def __get_md_content(self):
        if os.path.exists(self.md_file_path):
            with open(self.md_file_path, 'r', encoding='utf8') as file:
                md_content = file.read()
            return md_content
        else:
            raise Exception('O md em questão não existe!')

    def __get_the_md_with_splitted_md_lines(self):
        md_content = self.__get_md_content()
        return md_content.splitlines()        
        
    def __transfer_md_content_to_confluence(self):
        parent_page_id = self.confluence_integration.get_page_id(self.parent_page_title)
        self.confluence_integration.pass_to_confluence(parent_page_id, self.confluence_page_title, self.confluence_page_body)
        
    def __get_card_status(self):
        return self.jira_integration.get_card_status(self.card_key)

    def __move_card_to_review(self):
        self.jira_integration.move_card_to_review(self.card_key)

    def __get_discord_review_message(self):
        return f''':cowboy: Aoba, nova doc de cliente pra revisão :page_with_curl::writing_hand: 
{self.card_url}
Não se esqueça do emoji! :face_holding_back_tears:'''

    def __get_discord_fix_message(self):
        return f'''Opa! Consertei a {self.card_url}
Pode dar uma olhadinha de novo? :heart:'''

    def __notify_the_documentation_reviewers(self, message):
        self.discord_integration.send_message(self.doc_reviewer_channel_ids, message)

    def main(self):
        splitted_lines_of_the_md = self.__get_the_md_with_splitted_md_lines()

        self.__extract_and_clean_info_from_md_lines(splitted_lines_of_the_md)

        self.__transfer_md_content_to_confluence()

        card_status = self.__get_card_status()
        if card_status != "Review":
            self.__move_card_to_review()
            review_message = self.__get_discord_review_message()
            self.__notify_the_documentation_reviewers(review_message)
        else:
            fix_message = self.__get_discord_fix_message()
            self.__notify_the_documentation_reviewers(fix_message)

tmc = TransferMdContentToConfluence()
tmc.main()