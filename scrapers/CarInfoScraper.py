from bs4 import BeautifulSoup
from lxml import etree
from tqdm import tqdm
import threading
import requests
import re

from helpers.CSVHelper import CSVHelper


class CarInfo:

    def __init__(self, url):
        self.url = url
        page = requests.get(url)
        self.soup = BeautifulSoup(page.content, "html.parser")
        self.dom = etree.HTML(str(self.soup))

        self.brand = self.get_head_elems()[0]
        self.model = self.get_head_elems()[1]
        self.year = int(self.get_head_elems()[-1])
        self.mileage = self.get_mileage()
        self.fuel_type = self.get_fuel_type()
        self.engine_volume = self.get_engine_volume()
        self.transmission_type = self.get_transmission_type()
        self.owners = self.get_number_of_owners()
        self.price = self.get_price()

    def car_info(self):
        return {
            'brand': self.brand,
            'model': self.model,
            'year': self.year,
            'mileage': self.mileage,
            'fuel_type': self.fuel_type,
            'engine_volume': self.engine_volume,
            'transmission_type': self.transmission_type,
            'owners': self.owners,
            'price': self.price
        }

    def get_head_elems(self):
        head_elem = self.dom.xpath('//*[@id="heading-cars"]/div/h1/text()')[0]
        splitted_head_elem = head_elem.split(' ')
        return splitted_head_elem

    def get_mileage(self):
        milage_elem = self.dom.xpath('//*[@class="technical-info"][@id="details"]/dl/dd[2]/span[@class="argument"]/text()')[0]
        milage = ''.join([s for s in milage_elem if s.isdigit()])
        return int(milage)

    def get_fuel_type(self):
        fuel_type_elem = self.dom.xpath('//*[@class="technical-info"][@id="details"]/dl/dd[3]/span[@class="argument"]/text()')[1]
        fuel_type = str(fuel_type_elem)

        return fuel_type.replace(" ", ' ').replace('\n', '').strip()

    def get_engine_volume(self):
        engine_volume_elem = self.dom.xpath('//*[@class="technical-info"][@id="details"]/dl/dd[3]/span[@class="argument"]/text()')[0]
        engine_volume = list(map(float, (float(num) for num in re.findall(r'[-+]?\d*\.\d+|\d+', engine_volume_elem))))
        try:
            if engine_volume[0] > 9.0 and engine_volume[0] < 100:
                return round(float(engine_volume[0]) / 10, 1)
            if engine_volume[0] > 100.0:
                return round(float(engine_volume[0]) * 1.36 / 200, 1)
            else:
                return float(engine_volume[0])
        except:
            return 2.0

    def get_transmission_type(self):
        try:
            # Знаходимо елемент з класом "technical-info" та ідентифікатором "details"
            technical_info = self.soup.find('div', {'class': 'technical-info', 'id': 'details'})
            # Знаходимо всі елементи 'dd'
            dd_elements = technical_info.find_all('dd')
            # Список значень для пошуку
            values_to_search = ["Автомат", "Ручна / Механіка", "Робот", "Варіатор", "Типтронік"]
            # Перебираємо елементи 'dd' та елементи 'span' з класом "argument"
            found_value = None
            for dd_element in dd_elements:
                span_argument = dd_element.find('span', {'class': 'argument'})
                if span_argument:
                    for value in values_to_search:
                        if value in span_argument.text:
                            found_value = value
                            break
                if found_value:
                    break

            if found_value:
                return found_value
            else:
                return 'Ручна / Механіка'
        except:
            return 'Ручна / Механіка'

    def get_number_of_owners(self):
        try:
            # Знаходимо елемент з класом "technical-info" та ідентифікатором "details"
            technical_info_checked = self.soup.find('div', {'class': 'technical-info ticket-checked'})
            # Знаходимо всі елементи 'dd'
            dd_elements = technical_info_checked.find_all('dd')
            # Перебираємо елементи 'dd' та елементи 'span' з класом "argument"
            values_to_search = ["Кількість власників"]
            found_value = None
            for dd_element in dd_elements:
                span_label = dd_element.find('span', {'class': 'label'})
                if span_label:
                    for value in values_to_search:
                        if value in span_label.text:
                            span_argument = dd_element.find('span', {'class': 'argument'})
                            found_value = span_argument.text
                            break
                if found_value:
                    break

            if found_value: return int(found_value)
            else: return 1
        except: return 1

    def get_price(self):
        price_elem = self.dom.xpath('//*[@id="showLeftBarView"]/section[1]/div[1]/strong/text()')[0]
        price = ''.join([s for s in price_elem.split() if s.isdigit()])
        return int(price)



class CarInfoScraper:
    def parse_car_info(self, links):
        for i in tqdm(range(len(links))):
            try:
                res = CarInfo(links[i]).car_info()
                CSVHelper.write(path='./data/cars/data.csv', data=[res], headers=res.keys())
            except:
                continue

    def threaded_parse_car_info(self, links, num_of_threads):
        chunk_size = len(links) // num_of_threads

        # Створення потоків
        threads = []
        for i in range(self.num_of_threads):
            start = i * chunk_size
            if i != self.num_of_threads - 1:
                end = start + chunk_size
            else:
                end = len(self.links)
            thread = threading.Thread(self.parse_car_info, args=(self.links[start:end], ))
            threads.append(thread)

        # Запуск потоків
        for thread in threads:
            thread.start()

        # Очікування завершення потоків
        for thread in threads:
            thread.join()