import requests

class Notifications():
    def __init__(self, token: str, chat_id: str) -> None:
        self.token = token
        self. chat_id = chat_id

        self.url = f"https://api.telegram.org/bot{self.token}"

        # telegram stuff
        self.max_length = 4096 # characters

    def send_messages(self, messages: list, max_length: int):
        if not self.get_length(messages=messages) > max_length:
            message = ''.join(messages)
            self.send_message(message=message)
            return
        
        sublists = self.split_strings(messages, max_length=max_length)
        for sublist in sublists:
            message = ''.join(sublist)
            self.send_message(message=sublist)
    
    def send_message(self, message: str):
        params = {"chat_id": self.chat_id, "text": message}
        r = requests.post(self.url + "/sendMessage", params=params)

    def get_length(self, messages: list):
        return sum(len(message) for message in messages)
    
    @staticmethod
    def split_strings(strings, max_length = 4096):
        """
        Split a list of strings such that the total sum of characters in each sublist doesn't exceed max_length.

        Args:
            strings (list): The list of strings to split.
            max_length (int): The maximum total sum of characters allowed in each sublist.

        Returns:
            list: A list of sublists containing strings.
        """
        sublists = []
        current_sublist = []
        current_length = 0

        for string in strings:
            # If adding the next string exceeds the max_length, start a new sublist
            if current_length + len(string) > max_length:
                sublists.append(current_sublist)
                current_sublist = []
                current_length = 0
            
            current_sublist.append(string)
            current_length += len(string)

        # Append the last sublist
        if current_sublist:
            sublists.append(current_sublist)

        return sublists