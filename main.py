from bots.PTBMonitoringBot import PTBMonitoringBot
from helpers.PTBBotHelper import BotHelper
from managers.AccountsManager import AccountsManager
from managers.ApiAutoManager import ApiAutoManager
from predictors.PricePredictor import PricePredictor
import configparser



config = configparser.ConfigParser()
config.read('config.ini')

accountsManager = AccountsManager(config['api'])
autoManager = ApiAutoManager(config['api'])
pricePredictor = PricePredictor('./data/models/trained_model.pkl')
botHelper = BotHelper(accountsManager, autoManager, pricePredictor)

bot = PTBMonitoringBot(config['bot']['token'], botHelper)


if __name__ == "__main__":
    bot.run()




