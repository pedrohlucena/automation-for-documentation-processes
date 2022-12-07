import os
import re
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
            'post-behavior.md'
        )
        self.parent_page_title = 'Comportamentos'
        self.card_key = 'IC-7383'

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

    def __mount_the_final_confluence_page_body(self, md_translated_to_html):
        self.confluence_page_body = md_translated_to_html

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

    def __translate_md_to_html(self):
        md_content = self.__join_md_lines_into_a_md_content(self.confluence_page_body)

        md_content_converted_to_html = markdown.markdown(
            md_content,
            extensions=[TableExtension(use_align_attribute=True)]
        )
        return md_content_converted_to_html

    def __get_link_name_on_anchor_html_tag(self, html_link):
        link_name_regex = r'(GET|POST|PUT).+(?=<\/a>)'
        link_name = re.search(link_name_regex, html_link).group()
        return link_name

    def __fix_anchor_tag_hrefs(self):
        html_href_content_regex = r'((?<=href=").+?(?="))'
        html_anchor_tag_regex = r'(<a href="\..+?(?=\/a>)\/a>)'
        md_translated_to_html = self.__translate_md_to_html()
        html_achor_tags = re.findall(html_anchor_tag_regex, md_translated_to_html)

        for html_anchor_tag in html_achor_tags:
            link_name = self.__get_link_name_on_anchor_html_tag(html_anchor_tag)
            confluence_page_link = self.confluence_integration.get_page_url_by_name(link_name)
            old_href_with_md_reference = re.search(html_href_content_regex, html_anchor_tag).group()
            new_href_with_html_reference = html_anchor_tag.replace(old_href_with_md_reference, confluence_page_link)
            md_translated_to_html = md_translated_to_html.replace(html_anchor_tag, new_href_with_html_reference)

        return md_translated_to_html
        
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
        
        md_translated_to_html = self.__fix_anchor_tag_hrefs()

        self.__mount_the_final_confluence_page_body(md_translated_to_html)

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
        parent_page_id = self.confluence_integration.get_page_id_by_name(self.parent_page_title)
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

    def __watch_parent_card(self, child_card_key):
        parent_card_key = self.jira_integration.get_parent_card_key(child_card_key)
        self.jira_integration.watch_card(parent_card_key)

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
        self.__watch_parent_card(self.card_key)

tmc = TransferMdContentToConfluence()
tmc.main()