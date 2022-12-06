import os
import webbrowser
from library.codecommit import CodeCommit
from library.discord import Discord
from library.popup import Popup
from library.jira import JiraIntegration
from dotenv import load_dotenv, find_dotenv
import PySimpleGUI as sg

load_dotenv(find_dotenv())
    
class OpenPr:
    def __init__(self):
        self.aws_code_commit = CodeCommit(
            self.profile, 
            self.account_id, 
            self.region
        )
        self.jira_integration = JiraIntegration()
        self.discord_integration = Discord()
        self.popup = Popup()

        self.card = 'IC-2474'
        self.origin_branch = f'feature/{self.card.lower()}'
        self.target_branch = 'develop'
        self.repository = os.getenv('DOC_CONTENT_REPOSITORY_NAME')

        self.pr_title = f'{self.card_number}: {self.jira_integration.get_card_name(self.card)}'
        self.merge_type = 'THREE_WAY_MERGE'
        self.region = os.getenv('REGION')
        self.profile = os.getenv('PROFILE')
        self.account_id = os.getenv('ACCOUNT_ID')
        self.pr_channel_id = os.getenv('PR_CHANNEL_ID')
        self.approval_groups_ids = [os.getenv('FRONTEND_GROUP_ID'), os.getenv('ARCHITECTURE_GROUP_ID')]
        
    def main(self):
        if self.target_branch == 'master':
            self.__create_delivery_branch()

        self.mergeable = self.__check_if_mergeable()

        if self.mergeable:
            self.__open_pr()
        else:
            print(f'O repositório: {self.repository}, possui conflito!')
            self.__create_intermediate_branch()

    def __check_if_mergeable(self):
        mergeable = self.aws_code_commit.get_merge_conflicts(
            self.repository, 
            self.origin_branch, 
            self.target_branch,
            self.merge_type
        )

        return mergeable['mergeable']

    def __open_pr(self):
        pr = self.aws_code_commit.create_pull_request(self.pr_title, self.repository, self.origin_branch, self.target_branch)
        pr_id = pr['pullRequest']['pullRequestId']

        self.__render_send_discord_message_popup(pr_id)

    def __send_discord_message(self, pr_url):
        message = self.__get_pr_message(pr_url)
        self.discord_integration.send_message(self.pr_channel_id, message)

    def __get_pr_message(self, pr_url):
        frontend_group_id, architecture_group_id = self.approval_groups_ids
        pr_message = f'''[{self.target_branch.upper()}] {self.pr_title}
{pr_url}
<@&{frontend_group_id}> <@&{architecture_group_id}>
        '''
        return pr_message

    def __fetch_checkout_and_pull(self):
        os.system(f'git fetch origin {self.target_branch}')
        os.system(f'git checkout {self.target_branch}')
        os.system(f'git pull origin {self.target_branch}')

    def __create_normal_intermediate_branch(self):
        self.__fetch_checkout_and_pull()
        intermediate_branch_name = {self.origin_branch}-{self.target_branch}
        os.system(f'git branch -D {intermediate_branch_name}')
        os.system(f'git checkout -b {intermediate_branch_name}')
        os.system(f'git merge {self.origin_branch}')

    def __create_intermediate_branch(self):
        if self.target_branch != 'master':
            self.__create_normal_intermediate_branch()
        
        if not self.mergeable: 
            self.__render_conflict_popup()
        
    def __create_delivery_branch(self):
        delivery_branch_name = self.origin_branch.replace('feature', 'delivery')

        self.__fetch_checkout_and_pull()
        os.system(f'git branch -D {delivery_branch_name}')
        os.system(f'git checkout -b {delivery_branch_name}')
        os.system(f'git merge {self.origin_branch} --squash')

        self.origin_branch = delivery_branch_name

    def __render_conflict_popup(self):
        window = self.popup.__mount_conflict_popup()

        while True:
            event, values = window.read()
            if event == "Sim":
                self.__open_pr()
                break

    def __get_pr_url(self, pr_id):
        return f'https://{self.region}.console.aws.amazon.com/codesuite/codecommit/repositories/{self.repository}/pull-requests/{pr_id}/details?region={self.region}'

    def __render_send_discord_message_popup(self, pr_id):
        pr_url = self.__get_pr_url(pr_id)

        window = self.popup.__mount_send_discord_message_popup(pr_url)

        while True:
            event, values = window.read()
            if event == "Sim":
                self.__send_discord_message(pr_url)
                break
            elif event.startswith("URL "):
                url = event.split(' ')[1]
                webbrowser.open(url)
       
op = OpenPr()
op.main()