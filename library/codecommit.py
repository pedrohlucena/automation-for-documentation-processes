import json
import os

class CodeCommit:
    def __init__(self, profile, account_id, region):
        self.profile = profile
        self.account_id = account_id
        self.region = region
        self.command = f'aws --profile {self.profile} --region {self.region} codecommit'

    def get_merge_conflicts(self, repository, origin_branch, target_branch, merge_type):
        command = f'{self.command} get-merge-conflicts --repository-name {repository} --source-commit-specifier {origin_branch} --destination-commit-specifier {target_branch} --merge-option {merge_type}'
        return json.loads(os.popen(command).read())

    def create_pull_request(self, title, repository, sourceReference, destinationReference):
        command = f'{self.command} create-pull-request --title "{title}" --targets repositoryName={repository},sourceReference={sourceReference},destinationReference={destinationReference}'
        return json.loads(os.popen(command).read())