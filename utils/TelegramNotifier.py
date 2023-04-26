import json
from pathlib import Path
from typing import Dict

import requests as requests


class TelegramNotifier:

    def __init__(self, secrets_path: Path):
        # get credentials
        with open(secrets_path, "r") as f:
            credentials = json.load(f)
        # init
        self.url = f"https://api.telegram.org/bot{credentials['bot_key']}/sendMessage"
        self.user_ids = credentials['user_ids']

    def notify(self, msg: str) -> None:
        for usr in self.user_ids:
            envelope = self.__createEnvelope(usr, msg)
            self.__sendMessage(envelope)

    def __createEnvelope(self, user_id:str, msg: str) -> Dict:
        envelope = {
            "chat_id": user_id,
            "text": msg,
            "parse_mode": "Markdown"
        }
        return envelope

    def __sendMessage(self, envelope: Dict) -> None:
        requests.post(self.url, json=envelope)




