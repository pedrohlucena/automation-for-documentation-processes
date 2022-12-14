import os

class Os:
    def go_to_docs_repo():
        docs_repo_path = os.getenv('DOC_CONTENT_REPOSITORY_PATH')
        os.chdir(docs_repo_path)

    def stay_in_the_current_dir():
        os.system("/bin/bash")