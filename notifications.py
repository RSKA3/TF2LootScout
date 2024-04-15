import requests

class Notifications():
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self. chat_id = chat_id

        self.url = f"https://api.telegram.org/bot{self.token}"
    
    def send_message(self, message: str):
        params = {"chat_id": self.chat_id, "text": message}
        r = requests.post(self.url + "/sendMessage", params=params)
