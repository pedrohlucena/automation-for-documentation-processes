import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class TransferDocsFolder:
    def __init__(self):
        self.doc_content_repository_path = os.getenv('DOC_CONTENT_REPOSITORY_PATH')
        self.doc_frontend_repository_path = os.getenv('DOC_FRONTEND_REPOSITORY_PATH')
    def main(self):
        os.system(f'rm -r {self.doc_frontend_repository_path}/docs')
        os.system(f'cp -r {self.doc_content_repository_path}/docs {self.doc_frontend_repository_path}')
        os.system(f'npm start --prefix {self.doc_frontend_repository_path}')
        
tdf = TransferDocsFolder()
tdf.main()