import csv
import datetime
import xml.etree.ElementTree as ET
from urllib.request import urlopen
import pandas as pd


def max_or_min_date(date_list, parameter):
    result_date = date_list[0]
    for date in date_list:
        if parameter == 'max':
            if date > result_date:
                result_date = date
        else:
            if date < result_date:
                result_date = date
    return result_date


with open('vacancies_dif_currencies.csv', mode='r', encoding='utf-8-sig') as file:
    reader = csv.reader(file)
    kzt = 0
    uah = 0
    azn = 0
    uzs = 0
    eur = 0
    rur = 0
    gel = 0
    byr = 0
    usd = 0
    kgs = 0
    time = []
    valutes = {'KZT': kzt,
               'UAH': uah,
               'AZN': azn,
               'UZS': uzs,
               'EUR': eur,
               'RUR': rur,
               'GEL': gel,
               'BYR': byr,
               'USD': usd,
               'KGS': kgs
               }

    for line in reader:
        if line[5] != 'published_at':
            time.append(line[5])
        if line[3] != 'salary_currency' and line[3] != '':
            valutes[line[3]] += 1

    def get_frequent_valutes(valute):
        if valutes.get(valute) != None and valutes.get(valute) > 5000:
            return valute

    maxdate = max_or_min_date(time, 'max')
    mindate = max_or_min_date(time, 'min')
    first_date = datetime.datetime.strptime(f'{mindate[8:10]}-{mindate[5:7]}-{mindate[0:4]}', '%d-%m-%Y')
    sedond_date = datetime.datetime.strptime(f'{maxdate[8:10]}-{maxdate[5:7]}-{maxdate[0:4]}', '%d-%m-%Y')

    def month_count(first_date, second_date):
        months = 0
        while first_date < second_date:
            first_date = first_date + datetime.timedelta(days=30)
            months += 1
        return months - 1

    date = f'{mindate[8:10]}/{mindate[5:7]}/{mindate[0:4]}'
    kzt_list = []
    uah_list = []
    eur_list = []
    byr_list = []
    usd_list = []
    date_list = []
    for i in range(month_count(first_date, sedond_date)):
        date_list.append(date)
        tree = ET.parse(urlopen(f'http://www.cbr.ru/scripts/XML_daily.asp?date_req={date}'))
        date = str(datetime.datetime.strptime(date.replace('/','-'), '%d-%m-%Y') + datetime.timedelta(days=30))
        date = f'{date[8:10]}/{date[5:7]}/{date[0:4]}'
        root = tree.getroot()

        for child in root.findall("Valute"):
            charcode = child.find("CharCode").text
            value = float((child.find("Value").text).replace(',', '.')) / int(child.find("Nominal").text)
            if get_frequent_valutes(charcode) or charcode == 'BYN':
                if charcode == 'KZT':
                    kzt_list.append(value)
                if charcode == 'UAH':
                    uah_list.append(value)
                if charcode == 'EUR':
                    eur_list.append(value)
                if charcode == 'BYR' or charcode == 'BYN':
                    byr_list.append(value)
                if charcode == 'USD':
                    usd_list.append(value)

dict_csv = {'date': date_list, 'KZT': kzt_list, 'UAH': uah_list,
            'EUR': eur_list, 'BYR': byr_list, 'USD': usd_list}

dict_df = pd.DataFrame(dict_csv)
dict_df.to_csv('data.csv', index=False)
