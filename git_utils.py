import os
from dotenv import load_dotenv, find_dotenv
from library.os import Os
from doc_state import DocState
from library.git import Git

load_dotenv(find_dotenv()) 

class GitUtils():
    def __init__(self):
        self.doc_state = DocState()
        self.docs_repo_path = os.getenv('DOC_CONTENT_REPOSITORY_PATH')
        
        self.os = Os()
        self.git = Git()
    
    def __create_local_branch(self):
        self.os.go_to_docs_repo()
        self.git.create_local_branch(self.doc_state.origin_branch_name)
        self.os.stay_in_the_current_dir()

    def __add_commit_and_push_changes(self):
        self.os.go_to_docs_repo()
        self.git.add_and_commit('commit message')
        self.git.push_branch_to_codecommit(self.doc_state.origin_branch_name)
        self.os.stay_in_the_current_dir()

    def main(self):
        self.__add_commit_and_push_changes()