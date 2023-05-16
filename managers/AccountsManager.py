from urllib.parse import unquote
from pathlib import Path
import requests
import json
import time

class AccountsManager:
    def __init__(self, api_config):
        self.config = api_config
        self.users = {}
        self.data_directory = Path.cwd() / 'data/users'

    def get_user_filename(self, user_id):
        return self.data_directory / f'{user_id}.json'

    def write_user(self, user_id, user_config):
        user_file = self.get_user_filename(user_id)
        with user_file.open('w') as f:
            json.dump(user_config, f, indent=2)

    def get_user(self, user_id):
        user_file = self.get_user_filename(user_id)
        if user_file.exists():
            with user_file.open() as f:
                user_config = json.load(f)
            return user_config
        return {}

    def get_users(self):
        users = {}
        for file in self.data_directory.glob('*.json'):
            user_id = int(file.stem)
            with file.open() as f:
                user = json.load(f)
            if user['watchStatus']:
                users[user_id] = user
        return users

    def make_user(self, user_id, query):
        user_config = self.get_user(user_id)
        user_config['query'] = query
        user_config['setDate'] = int(time.time() * 1000)
        user_config['watchStatus'] = True

        print(f"Create settings for user: {user_id} ...")

        try:
            response = requests.get(self.config['queryTranslateFromNew'] + '?' + query)
            data = response.json()
            user_config['queryOld'] = unquote(data['string'])
            self.write_user(user_id, user_config)
        except Exception as err:
            print("API call failed...")

    def switch_watching_user(self, user_id, watch_status):
        user_file = self.get_user_filename(user_id)
        if user_file.exists():
            with user_file.open() as f:
                user_config = json.load(f)
            user_config['setDate'] = int(time.time())
            user_config['watchStatus'] = watch_status
            self.write_user(user_id, user_config)
            return True
        return False




