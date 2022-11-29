import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv()) 

class GitUtils():
    def __init__(self):
        self.card_number = '1111'
        self.branch_name = f'feature/ic-{self.card_number}'
        self.docs_repo_path = os.getenv('DOC_CONTENT_REPOSITORY_PATH')

    def __go_to_docs_repo(self):
        os.chdir(self.doc_repo_path)

    def __create_local_branch(self):
        self.__go_to_docs_repo()
        os.system('git checkout master')
        os.system('git pull origin master')
        os.system(f'git checkout -b {self.branch_name}')
        # os.system(f'git merge qa --squash') # when to create branch deploy

    def __add_commit_and_push_changes(self):
        self.__go_to_docs_repo()
        os.system('git add .')
        os.system(f'git commit -m "delivery of {self.card_number}"')
        os.system(f'git push --set-upstream origin {self.branch_name}')
        
    def main(self):
        self.__create_local_branch()

gu = GitUtils()
GitUtils.main()