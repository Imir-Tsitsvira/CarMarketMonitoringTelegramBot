import re
from urllib.parse import urlparse


class BotHelper:

    def __init__(self, accountsManager, autoManager, pricePredictor ):
        self.accounts_manager = accountsManager
        self.auto_manager = autoManager
        self.price_predictor = pricePredictor


    def get_help(self):
        help_text = 'Я експериментальний бот>. Готовий допомогти вам відслідковувати будь-який пошуковий запит з сайту AUTO.RIA.com.' + "\n" \
            'Раз на годину я буду переглядати ваш пошук і надсилати нові пропозиції з бази AUTO.RIA (якщо вони для вас з’являться).' + "\n\n" \
            'Я розумію наступні команди:' + "\n" \
            '  /start - Надішлю цей документ' + "\n" \
            '  /set [autoria search url] - запам’ятаю ваш пошуковий запит, наприклад /set https://auto.ria.com/uk/search/?category_id=1&type[5]=6 ' + "\n" \
            '  /get   - нагадаю вам пошуковий запит, який відслідковую для вас' + "\n" \
            '  /on    - відновлю відправку для вас нових пропозицій з бази AUTO.RIA' + "\n" \
            '  /off   - припиню надсилати вам нові пропозиції за вашим пошуковим запитом'

        return help_text

    def set_command(self, update, args):
        if not args:
            response = "Дайте мені команду /set [пошуковий запит з AUTO.RIA.com], де \"пошуковий запит з AUTO.RIA.com\" " \
                       "- це скопійована строка браузера при пошуку на AUTO.RIA.com, наприклад " \
                       "/set https://auto.ria.com/uk/search/?category_id=1&type[5]=6"
            return response

        url = args[0]
        myURL = urlparse(url)

        if not myURL.hostname.endswith('auto.ria.com'):
            response = f"Ви вказали невідомий мені хост {myURL.hostname}"
            return response

        if not myURL.path.endswith('search/'):
            response = f'Пошукова строка має бути скопійована зі сторінки пошуку б / у авто ' \
                       f'https://auto.ria.com/search/?..., а у вас інша адреса: "{myURL.hostname}"'
            return response

        query = myURL.query or ''
        hash = myURL.fragment

        if not query:
            query = hash[0:]
        else:
            query = query[0:]

        self.accounts_manager.make_user(update.message.chat_id, query)
        response = f'З цього моменту я буду відслідковувати всі нові оголошення по пошуку {url}'
        return response

    def get_command(self, update):
        user_config = self.accounts_manager.get_user(update.message.chat_id)
        if 'query' in user_config and user_config['query'] is not None:
            response = f'Відслідковую пошук: https://auto.ria.com/search/?{user_config["query"]}'
        else:
            response = 'Я в замешательстве :(, пошукова строка не задана: Встановіть пошукову строку за допомогою команди /set'
        return response

    def off_command(self, update):
        self.accounts_manager.switch_watching_user(update.message.chat_id, False)
        response ='Я призупинив відслідковування пошуку для вас'
        return response

    def on_command(self, update):
        result = self.accounts_manager.switch_watching_user(update.message.chat_id, True)
        if not result:
            response ='Я в замешательстве, не можу виконати цю команду: ви не вказали пошукову строку за допомогою команди /set'
        else:
            response ='Я знову, з радістю, буду надсилати вам нові пропозиції за вашим пошуковим запитом'
        return response

    def unknown_command(self):
        response = 'Я експериментальний робот і, на жаль, вашу команду не розумію. Напишіть мені /start, щоб дізнатися команди, які я вже вивчив.'
        return response


    def id_to_url(self, id):
        link = f'https://auto.ria.com/auto___{id}.html'
        return link

    def url_to_id(self, url):
        pattern = r'https://auto\.ria\.com/uk/auto_[\w_]+_(\d+)\.html'
        match = re.search(pattern, url)

        if match:
            return int(match.group(1))
        else:
            raise ValueError(f"Неможливо зчитати ID з URL: {url}")
