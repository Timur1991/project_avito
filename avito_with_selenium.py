from bs4 import BeautifulSoup
from selenium import webdriver
import time
import pandas
from selenium.webdriver.chrome.service import Service
import re
# pip install openpyxl

"""
Парсер торговой площидки Avito, с помощью Selenium
Для работоспособности не забудьте скачать сам драйвер, под свою версию браузера Chrome.
По всем возникшим вопросам, можете писать в группу https://vk.com/happython
Ссылка на статью: None
Отзывы, предложения, советы приветствуются.
"""


def get_pages(html):
    """определяем количеоств страниц выдачи"""
    soup = BeautifulSoup(html, 'lxml')
    pages = soup.find('div', class_=re.compile('pagination-root')).find_all('span', class_=re.compile('pagination-item'))[-2].text
    print(f'Найдено страниц выдачи: {pages}')
    return int(pages)


def get_content_page(html):
    """Функция сбора данных"""
    soup = BeautifulSoup(html, 'lxml')
    blocks = soup.find_all('div', class_=re.compile('iva-item-content'))
    # сбор данных с страницы
    data = []
    for block in blocks:
        data.append({
            "Наименование": block.find('h3', class_=re.compile('title-root')).get_text(strip=True),
            'Цена': block.find('span', class_=re.compile('price-text')).get_text(strip=True).replace('₽', '').replace(
                '\xa0', ''),
            'Город': block.find('a', class_=re.compile('link-link')).get('href').split('/')[1],
            'Район': block.find('div', class_=re.compile('geo-root')).get_text(strip=True),
            'Ссылка': 'https://www.avito.ru/' + block.find('a', class_=re.compile('link-link')).get('href'),
        })
    return data


def parser(url):
    """Основная функция, сам парсер"""
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument('--log-level=3')
    options.add_argument("--headless")  #режим без запуска браузера

    # укажите путь до драйвера
    service = Service(executable_path="chromedriver")
    browser = webdriver.Chrome(service=service, options=options)
    browser.get(url)
    html = browser.page_source
    pages = get_pages(html)  #определяем количество страниц выдачи
    data_list_pages = []
    for page in range(1, pages + 1):
        link = url + f'&p={page}'
        try:
            browser.get(link)
            time.sleep(1)
            html = browser.page_source
            data_list_pages.extend(get_content_page(html))
            print(f'Парсинг страницы {page} завершен. Собрано {len(data_list_pages)} позиций')
        except Exception as ex:
            print(f'Не предвиденная ошибка: {ex}')
            browser.close()
            browser.quit()
    print('Сбор данных завершен.')
    return data_list_pages


def save_exel(data):
    """Функция сохранения в файл"""
    dataframe = pandas.DataFrame(data)
    df = dataframe.drop_duplicates(['Ссылка'])
    writer = pandas.ExcelWriter(f'data_avito.xlsx')
    df.to_excel(writer, 'data_avito')
    writer.save()
    print(f'Удаление дубликатов...\nСобрано {len(df)} объявлений')
    print(f'Данные сохранены в файл "data_avito.xlsx"')


if __name__ == "__main__":
    url = input('Введите ссылку на раздел, с заранее выбранными характеристиками (ценовой диапазон и тд):\n')
    # url = 'https://www.avito.ru/bashkortostan?bt=1&f=ASgCAgECAUXGmgwZeyJmcm9tIjoxMTAwMCwidG8iOjEyMDAwfQ&i=1&q=%D0%B2%D0%B5%D0%BB%D0%BE%D1%81%D0%B8%D0%BF%D0%B5%D0%B4&s=104'
    print('Запуск парсера...')
    save_exel(parser(url))
