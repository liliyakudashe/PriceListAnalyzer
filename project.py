import os
import csv
import logging
from tabulate import tabulate

logging.basicConfig(level=logging.INFO, filename='price_machine.log', filemode='a',
                    format='%(asctime)s - %(levelname)s -%(message)s')


class PriceMachine:

    def __init__(self):
        self.data = []
        self.result = ''
        self.logger = logging.getLogger(__name__)

    def load_prices(self, file_path):
        try:
            files = os.listdir(file_path)
        except FileNotFoundError as e:
            self.logger.error(f'Указанный путь не существует: {file_path}')
            return

        prices = []
        for file in files:
            if 'price' in file.lower():
                prices.append(file)
                with open(file=os.path.join(file_path, file), mode='r', encoding='utf-8', errors='replace') as fl:
                    try:
                        reader = csv.DictReader(fl, delimiter=',')
                    except csv.Error as e:
                        self.logger.error(f'Ошибка чтения файла {file}: {e}')
                        continue
                    headers = reader.fieldnames
                    columns = self._search_product_price_weight(headers=headers)
                    for row in reader:
                        product_name = row.get(columns[0])
                        price = row.get(columns[1])
                        weight = row.get(columns[2])
                        try:
                            price_per_kg = float(price) / float(weight)
                        except (ValueError, ZeroDivisionError) as e:
                            self.logger.error(f'Ошибка расчёта цены за килограмм для файла {file}: {e}')
                            continue
                        self.data.append([product_name, price, weight, file, round(price_per_kg, 2)])

    def _search_product_price_weight(self, headers):
        if headers is None:
            self.logger.error('Заголовки столбцов не определены')
            return None, None, None

        normal_name_columns = ["название", "продукт", "товар", "наименование"]
        normal_price_column = ["цена", "розница"]
        normal_weight_columns = ["фасовка", "масса", "вес"]
        name_column = None
        price_column = None
        weight_column = None

        for header in headers:
            if header.lower() in normal_name_columns:
                name_column = header
            elif header.lower() in normal_price_column:
                price_column = header
            elif header.lower() in normal_weight_columns:
                weight_column = header
        return name_column, price_column, weight_column

    def export_to_html(self, fname='output.html'):
        if not self.data:
            self.logger.warning('Нет данных для экспорта')
            return

        with open(fname, mode='w') as file:
            file.write("<html><body>")
            table = tabulate(self.data, headers=['Наименование', 'Цена', 'Вес', 'Файл', 'Цена за кг.'], tablefmt='html')
            file.write(table)
            file.write("</body></html>")
            self.logger.info(f'Данные успешно экспортированы в файл: {fname}')

    def find_text(self, text):
        if not self.data:
            self.logger.warning('Нет данных для поиска')
            return

        filtered_data = [row for row in self.data if text.lower() in row[0].lower()]
        sorted_data = sorted(filtered_data, key=lambda x: x[4])
        headers = ["№", "Наименование", "Цена", "Вес", "Файл", "Цена за кг."]
        table = [[idx + 1, *row] for idx, row in enumerate(sorted_data)]
        result = tabulate(table, headers, tablefmt='grid')
        self.logger.info('Поиск выполнен успешно')
        return result


pm = PriceMachine()
pm.load_prices('C:\\Users\\Acer\\PycharmProjects\\PriceListAnalyzer')

while True:
    search_text = input('Введите название товара для поиска (или "exit" для завершения): ')
    if search_text.lower() == 'exit':
        print('Работа завершена')
        break
    print(pm.find_text(search_text))

pm.export_to_html('output.html')
