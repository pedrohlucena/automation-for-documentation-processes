import os
import subprocess
from subprocess import CalledProcessError
from dotenv import load_dotenv, find_dotenv  
from library.popup import Popup

load_dotenv(find_dotenv()) 

class Git():
    def __init__(self):
        self.popup = Popup()

    def add_and_commit(self, commit_message):
        os.system('git add .')
        os.system(f'git commit -m "{commit_message}"')

    def push_branch_to_codecommit(self, branch_name):
        os.system(f'git push --set-upstream origin {branch_name}')

    def create_local_branch(self, local_branch_name):
        os.system('git checkout master')
        os.system('git pull origin master')
        os.system(f'git checkout -b {local_branch_name}')

    def __verify_if_local_branch_exists(self, branch): 
        try:
            subprocess.Popen(['git', 'show-ref', '--verify', f'refs/heads/{branch}'], stderr=subprocess.STDOUT)
            return True
        except CalledProcessError as e:
            if 'fatal not a valid ref' in str(e.output):
                return False

    def __delete_local_branch(self, branch):
        os.system(f'git branch -D {branch}')

    def __create_local_branch(self, branch):
        os.system(f'git checkout -b {branch}')
    
    def __get_current_branch_name(self):
        return os.popen('git rev-parse --abbrev-ref HEAD').read().strip()

    def __recreate_from_current_branch(self, branch_to_be_recreated):
        self.__delete_local_branch(branch_to_be_recreated)
        self.__create_local_branch(branch_to_be_recreated)

    def fetch_checkout_and_pull(self, target_branch):
        os.system(f'git fetch origin {target_branch}')
        os.system(f'git checkout {target_branch}')
        os.system(f'git pull origin {target_branch}')

    def __recreate_from_codecommit_reference(self, branch_to_be_recreated):
        self.__delete_local_branch(branch_to_be_recreated)
        self.fetch_checkout_and_pull(branch_to_be_recreated)

    def __recreate_branch_handler(self, branch_to_be_recreated):
        current_branch = self.__get_current_branch_name()
        window = self.popup.mount_recreate_branch_popup(branch_to_be_recreated, current_branch)

        while True:
            event, values = window.read()
            if event == f"Recriar a partir da branch atual ({current_branch})":
                self.__recreate_from_current_branch(branch_to_be_recreated)
                window.close()
                return
            elif event == "Recriar a partir da referência dessa branch no CodeCommit":
                self.__recreate_from_codecommit_reference(branch_to_be_recreated)
                window.close()
                return

    def __branch_already_exists_handler(self, window, branch):
        while True:
            event, values = window.read()
            if event == "Seguir o processo com a branch já existente":
                window.close()
                return
            elif event == "Recriar a branch e seguir com o processo":
                self.__recreate_branch_handler(branch)
                window.close()
                return
            elif event == "Encerrar o processo":
                exit()

    def create_local_branch_controller(self, repo, branch):
        local_branch_exists = self.__verify_if_local_branch_exists(branch)

        if local_branch_exists:
            window = self.popup.mount_branch_already_exists_popup(repo, branch)
            self.__branch_already_exists_handler(window, branch)
        else:
            self.__create_local_branch(branch)