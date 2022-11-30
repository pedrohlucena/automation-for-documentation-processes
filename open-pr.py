import os
import webbrowser
from library.codecommit import CodeCommit
from library.discord import Discord
from dotenv import load_dotenv, find_dotenv
import PySimpleGUI as sg

load_dotenv(find_dotenv())
    
class OpenPr:
    def __init__(self):
        self.repository = 'repository'
        self.origin_branch = 'origin branch'
        self.target_branch = 'target branch'
        self.region = os.getenv('REGION')
        self.profile = os.getenv('PROFILE')
        self.account_id = os.getenv('ACCOUNT_ID')
        self.merge_type = 'THREE_WAY_MERGE'
        self.pr_channel_id = os.getenv('PR_CHANNEL_ID')
        self.card_number = self.__get_card_number(self.__get_current_branch_name())
        self.approval_groups_ids = [os.getenv('FRONTEND_GROUP_ID'), os.getenv('ARCHITECTURE_GROUP_ID')]
        
        self.aws_code_commit = CodeCommit(
            self.profile, 
            self.account_id, 
            self.region
        )
        
        self.discord_integration = Discord()

    def __get_current_branch_name(self):
        return os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

    def __open_pr(self):
        prTitle = 'DOC DE CLIENTE'
        if self.target_branch == 'master':
            deliveryBranchName = self.__create_intermediate_branch()
            self.origin_branch = deliveryBranchName
        pr = self.aws_code_commit.create_pull_request(prTitle, self.repository, self.origin_branch, self.target_branch)
        pr_id = pr['pullRequest']['pullRequestId']
        return pr_id

    def __check_if_mergeable(self):
        mergeable = self.aws_code_commit.get_merge_conflicts(
            self.repository, 
            self.origin_branch, 
            self.target_branch,
            self.merge_type
        )

        return mergeable['mergeable']

    def __send_discord_message(self, pr_url):
        message = self.__get_pr_message(pr_url)
        self.discord_integration.send_message(self.pr_channel_id, message)

    def __get_pr_message(self, pr_url):
        frontend_group_id, architecture_group_id = self.approval_groups_ids
        pr_message = f'''[{self.target_branch.upper()}] {self.card_number.upper()}: DOC CLIENTE
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
        branch_name = {self.origin_branch}-{self.target_branch}
        os.system(f'git branch -D {branch_name}')
        os.system(f'git checkout -b {branch_name}')
        os.system(f'git merge {self.origin_branch}')

    def __create_intermediate_branch(self):
        if self.target_branch != 'master':
            self.__create_normal_intermediate_branch()
        else:
            self.__create_delivery_branch()

    def __create_delivery_branch(self):
        self.__fetch_checkout_and_pull()
        branch_name = self.origin_branch.replace('feature', 'delivery')
        os.system(f'git branch -D {branch_name}')
        os.system(f'git checkout -b {branch_name}')
        os.system(f'git merge {self.origin_branch} --squash')
            
    def __get_card_number(self, branchName):
        return branchName[branchName.find('/')+1:branchName.rfind('-')]

    def __mount_conflict_popup(self):
        layout = [
            [sg.Text(
                'Já resolveu os conflitos? Posso terminar de fazer a subida?', 
                size=(50, 2), 
                justification="center")
            ], 
            [sg.Button("Sim"), sg.Button("Não")]
        ] 
        return layout

    def __render_conflict_popup(self):
        layout = self.__mount_conflict_popup()
        window = sg.Window("Conflitos na subida...", layout)
        while True:
            event, values = window.read()
            if event == "Sim":
                self.__send_discord_message()
                break

    def __mount_send_discord_message_popup(self, pr_url):
        column_to_be_centered = [
            [sg.Text('Link da PR:', size=(45, 1), justification="center")],
            [sg.Text(
                pr_url, 
                tooltip=pr_url, 
                enable_events=True, 
                size=(140, 1), 
                justification="center",
                key=f'URL {pr_url}')],
            [sg.Text('A pr já foi revisada? Posso mandar a mensagem no discord pro pessoal?', size=(60, 1), justification="center")],
            [sg.Button("Sim"), sg.Button("Não")]
        ]

        layout = [
            [sg.VPush()],
            [sg.Push(), sg.Column(column_to_be_centered,element_justification='c'), sg.Push()],
            [sg.VPush()]
        ]

        return layout

    def __get_pr_url(self, pr_id):
        return f'https://{self.region}.console.aws.amazon.com/codesuite/codecommit/repositories/{self.repository}/pull-requests/{pr_id}/details?region={self.region}'

    def __render_send_discord_message_popup(self, pr_id):
        pr_url = self.__get_pr_url(pr_id)
        layout = self.__mount_send_discord_message_popup(pr_url)
        window = sg.Window("Pó manda?", layout)

        while True:
            event, values = window.read()
            if event == "Sim":
                self.__send_discord_message(pr_url)
                break
            elif event.startswith("URL "):
                url = event.split(' ')[1]
                webbrowser.open(url)

    def main(self):
        mergeable = False
        while not mergeable:
            mergeable = self.__check_if_mergeable()
            if mergeable:
                pr_id = self.__open_pr()
                self.__render_send_discord_message_popup(pr_id)
            else:
                print(f'O repositório: {self.repository}, possui conflito!')
                self.__create_intermediate_branch()
                self.__render_conflict_popup()
        
op = OpenPr()
op.main()