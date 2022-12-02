import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class TransferDocsFolder:
    def __init__(self):
        self.doc_content_repository_path = os.getenv('DOC_CONTENT_REPOSITORY_PATH')
        self.docs_folder_in_doc_content_repository_path = os.getenv('DOCS_FOLDER_IN_DOC_CONTENT_REPOSITORY_PATH')
        self.doc_frontend_repository_path = os.getenv('DOC_FRONTEND_REPOSITORY_PATH')

    def transferDocsToFrontendRepo(self):
        os.system(f'rm -r {self.doc_frontend_repository_path}/docs')
        os.system(f'cp -r {self.docs_folder_in_doc_content_repository_path} {self.doc_frontend_repository_path}')
        os.system(f'npm start --prefix {self.doc_frontend_repository_path}')

    def transferDocsToContentRepo(self):
        os.system(f'rm -r {self.docs_folder_in_doc_content_repository_path}')
        os.system(f'cp -r {self.doc_frontend_repository_path}/docs {self.doc_content_repository_path}')

    def main(self):
        self.transferDocsToContentRepo()
        
tdf = TransferDocsFolder()
tdf.main()