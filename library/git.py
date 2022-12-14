import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv()) 

class Git():
    def add_and_commit(self, commit_message):
        os.system('git add .')
        os.system(f'git commit -m "{commit_message}"')

    def push_branch_to_codecommit(self, branch_name):
        os.system(f'git push --set-upstream origin {branch_name}')