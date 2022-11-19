import os
import requests
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

class Discord:
    def __init__(self):
        self.discord_token = os.getenv('DISCORD_TOKEN')

    def __fetch_request_information(self, message):
        payload = {
            'content': f'{message}'
        }

        header = {
            'authorization': self.discord_token
        }

        return [payload, header]

    def send_message(self, pr_channel_id, message):
        payload, header = self.__fetch_request_information(message)
        requests.post(
            f'https://discord.com/api/v9/channels/{pr_channel_id}/messages', data=payload, headers=header
        )