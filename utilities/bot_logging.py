import requests

class BotLogging():
    def __init__(self, webhook=None, username=None):
        self.webhook = webhook
        self.username = username
    
    def send_message(self, message):
        # for all params, see https://discordapp.com/developers/docs/resources/webhook#execute-webhook
        data = {
            "content": message,
            "username": self.username
        }

        result = requests.post(self.webhook, json=data)

        try:
            result.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)