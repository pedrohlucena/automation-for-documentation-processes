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

    def send_message(self, channel_ids, message):
        payload, header = self.__fetch_request_information(message)
        for channel_id in channel_ids:
            r = requests.post(
                f'https://discord.com/api/v9/channels/{channel_id}/messages', data=payload, headers=header
            )
            print(f'Return Code:: {r.status_code}')
            print(f'Return Content:: {r.content}')
            print(f'Message Length:: {len(payload["content"])}')