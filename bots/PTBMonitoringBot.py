import os
import datetime
import pandas as pd
from telegram import Update,InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackContext, filters

from predictors import RFRModel
from scrapers.CarInfoScraper import CarInfoScraper
from scrapers.URLScraper import URLScraper


class PTBMonitoringBot:
    def __init__(self, token, botHelper):
        self.token = token
        self.bot_helper = botHelper
        self.application = ApplicationBuilder().token(self.token).build()
        self.job_queue = self.application.job_queue
        
        self.register_handlers()
        self.start_monitoring()
        self.start_scraping()
        self.start_monitoring()

    async def start(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, self.bot_helper.get_help())

    async def set_command(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, self.bot_helper.set_command(update, context.args))

    async def get_command(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, self.bot_helper.get_command(update))

    async def on_command(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, self.bot_helper.on_command(update))

    async def off_command(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, self.bot_helper.off_command(update))

    async def unknown_command(self, update: Update, context: CallbackContext) -> None:
        chat_id = update.effective_chat.id
        await context.bot.send_message(chat_id, self.bot_helper.unknown_command())

    def register_handlers(self):
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("set", self.set_command))
        self.application.add_handler(CommandHandler("get", self.get_command))
        self.application.add_handler(CommandHandler("on", self.on_command))
        self.application.add_handler(CommandHandler("off", self.off_command))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown_command))

    def run(self):
       self.application.run_polling()

    def start_monitoring(self):

        async def car_market_monitoring(context: CallbackContext):
            print("Обработка всех подписок!")
            accounts_manager = self.bot_helper.accounts_manager
            auto_manager = self.bot_helper.auto_manager
            price_predictor = self.bot_helper.price_predictor
            users = accounts_manager.get_users()
            for key in users:
                print(f"Проверяем подписку пользователя №{key}")
                data = auto_manager.get_search_data(users[key]["queryOld"])
                if len(data["result"]["search_result"]["ids"]) > 0:
                    print(data["result"]["search_result"]["ids"])
                    for id in data["result"]["search_result"]["ids"][:2]:
                        car_data = auto_manager.get_car_data(id)
                        avg_price = auto_manager.get_avg_price(car_data)
                        predicted_price = price_predictor.predict_price(car_data)

                        await context.bot.send_photo(
                            chat_id=key,
                            photo=car_data["photoData"]["seoLinkF"],
                            caption=f'{car_data["title"]} {car_data["autoData"]["year"]} {car_data["USD"]}$\n'
                                    f'{car_data["stateData"]["name"]}  {car_data["autoData"]["race"]}\n'
                                    f'{car_data["autoData"]["description"][:500]} ...\n'
                                    f'\narithmeticMean= {round(avg_price["arithmeticMean"])}\n'
                                    f'interQuartileMean= {round(avg_price["interQuartileMean"])}\n'
                                    f'predictedPrice= {round(predicted_price)}',
                            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Посилання',
                                                                                     url=self.bot_helper.id_to_url(id))]])
                            )

        return self.job_queue.run_repeating(car_market_monitoring, interval=3600, first=1)


    def start_scraping(self):
        async def scraper():
            URLScraper.threaded_parse_links(search_url='https://auto.ria.com/uk/search/?indexName=auto&categories.main.id=1&verified.VIN=1'
                                                        '&country.import.usa.not=-1&price.currency=1&top=11&abroad.not=0&custom.not=1',
                                            num_of_pages=100,
                                            num_of_threads=os.cpu_count() - 4,
                                            file_name='daily_links')
            df_links = pd.read_csv('./data/cars/daily_links.csv')
            links = df_links.values.tolist()
            CarInfoScraper.threaded_parse_car_info(links= links,
                                                   num_of_threads=os.cpu_count() - 4)

        return self.job_queue.run_daily(callback=scraper, time=datetime.time(hour=23, minute=30), days=(0, 1, 2, 3, 4, 5, 6))

    def start_model_training(self):
        async def model_training():
            df = RFRModel.set_train_data('./data/cars/data.csv')
            splited_df = RFRModel.splite_data_frame(df)
            pipeline = RFRModel.pipeline()
            model = RFRModel.train(pipeline, splited_df)
            RFRModel.save_model(model, './data/models/trained_model.pkl')

        return self.job_queue.run_daily(callback=model_training, time=datetime.time(hour=23, minute=30),days=(0,))