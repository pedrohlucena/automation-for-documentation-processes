import os
import sys
from library.codecommit import CodeCommit
from library.discord import Discord
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())
    
class OpenPr:
    def __init__(self):
        config = self.__get_configuration_object()
        self.repository = config['REPOSITORY']
        self.origin_branch = config['ORIGIN_BRANCH']
        self.target_branch = config['TARGET_BRANCH']
        self.region = config['REGION']
        self.profile = config['PROFILE']
        self.account_id = config['PROFILE']
        self.merge_type = config['MERGE_TYPE']
        self.pr_channel_id = config['PR_CHANNEL_ID']
        self.card_number = config['CARD_NUMBER']
        self.approval_groups_ids = config['APROVAL_GROUPS_IDS']
        
        self.aws_code_commit = CodeCommit(
            self.profile, 
            self.account_id, 
            self.region
        )
        
        self.discord_integration = Discord()
    
    def __get_configuration_object(self):
        configuration_object = {}
        configuration_object['REPOSITORY'] =  'repository'
        configuration_object['TARGET_BRANCH'] = 'target branch'
        configuration_object['ORIGIN_BRANCH'] = sys.argv[3] if self.__there_is_origin_branch() else self.__get_current_branch_name()

        configuration_object['PROFILE'] = os.getenv('PROFILE')
        configuration_object['REGION'] = os.getenv('REGION')
        configuration_object['ACCOUNT_ID'] = os.getenv('ACCOUNT_ID')
        configuration_object['PR_CHANNEL_ID'] = os.getenv('PR_CHANNEL_ID')
        configuration_object['APROVAL_GROUPS_IDS'] = [os.getenv('FRONTEND_GROUP_ID'), os.getenv('ARCHITECTURE_GROUP_ID')]
        configuration_object['CARD_NUMBER'] = self.__get_card_number(self.__get_current_branch_name())
        configuration_object['MERGE_TYPE'] = 'THREE_WAY_MERGE'

        return configuration_object
    
    def __there_is_origin_branch(self):
        return len(sys.argv) == 4

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

    def __send_discord_message(self, pr_id):
        message = self.__get_pr_message(pr_id)
        self.discord_integration.send_message(self.pr_channel_id, message)

    def __get_pr_message(self, pr_id):
        pr_url = f'https://{self.region}.console.aws.amazon.com/codesuite/codecommit/repositories/{self.repository}/pull-requests/{pr_id}/details?region={self.region}'
        frontend_group_id, architecture_group_id = self.approval_groups_ids
        pr_message = f'''[{self.target_branch.upper()}] {self.card_number.upper()}: DOC CLIENTE
{pr_url}
<@&{frontend_group_id}> <@&{architecture_group_id}>
        '''
        return pr_message

    def __push_branch_to_codecommit(self, branch):
        os.system(f'git push origin {branch}')

    def __get_current_branch_name(self):
        return os.popen('git rev-parse --abbrev-ref HEAD').read().strip() 

    def __create_intermediate_branch(self):
        os.system(f'git fetch origin {self.target_branch}')
        os.system(f'git checkout {self.target_branch}')
        os.system(f'git pull origin {self.target_branch}')

        intermediateBranchName = ''
        
        if (self.target_branch != 'master'):
            intermediateBranchName = {self.origin_branch}-{self.target_branch}
            os.system(f'git branch -D {intermediateBranchName}')
            os.system(f'git checkout -b {intermediateBranchName}')
            os.system(f'git merge {self.origin_branch}')
            print('Branch intermediária criada! Agora é só resolver os conflitos :3')
        else:
            intermediateBranchName = self.origin_branch.replace('feature', 'delivery')
            os.system(f'git branch -D {intermediateBranchName}')
            os.system(f'git checkout -b {intermediateBranchName}')
            os.system(f'git merge {self.origin_branch} --squash')
            os.system(f'git commit -m "delivery of {self.card_number}"')
            self.__push_branch_to_codecommit(intermediateBranchName)
            return intermediateBranchName

    def __get_card_number(self, branchName):
        return branchName[branchName.find('/')+1:branchName.rfind('-')]

    def main(self):
        self.__push_branch_to_codecommit(self.__get_current_branch_name())
        isMergeable = self.__check_if_mergeable()
        if isMergeable:
            pr_id = self.__open_pr()
            self.__send_discord_message(pr_id)
        else:
            print(f'O repositório: {self.repository}, possui conflito!')
            self.__create_intermediate_branch()
        
op = OpenPr()
op.main()