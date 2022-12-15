import os
from subprocess import subprocess, CalledProcessError
from dotenv import load_dotenv, find_dotenv  
from library.popup import Popup

load_dotenv(find_dotenv()) 

class Git():
    def add_and_commit(self, commit_message):
        os.system('git add .')
        os.system(f'git commit -m "{commit_message}"')

    def push_branch_to_codecommit(self, branch_name):
        os.system(f'git push --set-upstream origin {branch_name}')

    def create_local_branch(self, local_branch_name):
        os.system('git checkout master')
        os.system('git pull origin master')
        os.system(f'git checkout -b {local_branch_name}')

    def __verify_if_local_branch_exists(branch): 
        try:
            subprocess.Popen(['git', 'show-ref', '--verify', f'refs/heads/{branch}'], stderr=subprocess.STDOUT)
            return True
        except CalledProcessError as e:
            if 'fatal not a valid ref' in str(e.output):
                return False

    def __delete_local_branch(branch):
        os.system(f'git branch -D {branch}')

    def __create_local_branch(branch):
        os.system(f'git checkout -b {branch}')

    def create_local_branch_controller(self, repo, branch):
        popup = Popup()

        local_branch_exists = self.__verify_if_local_branch_exists(branch)

        if local_branch_exists:
            window = popup.mount_branch_already_exists_popup(repo, branch)

            while True:
                event, values = window.read()
                if event == "Seguir o processo com a branch já existente":
                    break
                elif event == "Recriar a branch e seguir com o processo":
                    self.__delete_local_branch(branch)
                    self.__create_local_branch(branch)
                    break
                elif event == "Encerrar o processo":
                    exit()
        else:
            self.__create_local_branch(branch)