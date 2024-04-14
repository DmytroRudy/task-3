from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from google.oauth2.service_account import Credentials
import pandas as pd
import numpy as np
import re
import gspread

url = 'https://www.olx.ua/uk/nedvizhimost/kvartiry/prodazha-kvartir/kiev/?currency=UAH'

service = Service(executable_path='chromedriver.exe')
driver = webdriver.Chrome(service=service)

class_id = 'css-z3gu2d'
price_id = 'css-12vqlj3'
list_id = "css-1r0si1e"
titles = []
cities = []
prices = []
floors = []
total_areas = []
levels = []
flats = []

driver.get(url)
elements = driver.find_elements(By.CLASS_NAME, class_id)

for element in elements:
    href = element.get_attribute(name='href')
    flats.append(href)

flats = np.array(flats)
flats = np.unique(flats)
titles = np.array(titles)
titles = np.unique(titles)
all_data = []
for flat in flats:
    driver.execute_script("window.open();")
    driver.switch_to.window(driver.window_handles[-1])

    driver.get(flat)
    titles = np.append(titles, driver.title)
    price = driver.find_element(By.CLASS_NAME, price_id).text
    prices.append(price)
    li_elements = driver.find_elements(By.CLASS_NAME, list_id)
    data = []
    for element in li_elements:
        data.append(element.text)

    all_data.append(data)

    driver.close()

    driver.switch_to.window(driver.window_handles[0])

driver.quit()

for subarray in all_data:
    floor_match = re.search(r'Поверховість:\s*(\d+)', ' '.join(subarray))
    total_area_match = re.search(r'Загальна площа:\s*([\d.]+)\s*м²', ' '.join(subarray))
    level_match = re.search(r'Поверх:\s*(\d+)', ' '.join(subarray))

    # Додаємо значення або '-' в залежності від того, чи вдалося знайти дані
    if floor_match:
        floors.append(floor_match.group(1))
    else:
        floors.append('-')

    if total_area_match:
        total_areas.append(total_area_match.group(1))
    else:
        total_areas.append('-')

    if level_match:
        levels.append(level_match.group(1))
    else:
        levels.append('-')
data = {
    'Title': titles,
    'Price': prices,
    'Floor': floors,
    'Total Area': total_areas,
    'Level': levels,
    'Link': flats
}


df = pd.DataFrame(data)


scopes = ['https://www.googleapis.com/auth/spreadsheets']
creds = Credentials.from_service_account_file('credentials.json', scopes=scopes)
client = gspread.authorize(creds)
sheet_id = '1cawXiAvXCa49egZm-fa_s99YBdPSs9HnmJm10N1bioc'
sheet = client.open_by_key(sheet_id)
worksheet = sheet.get_worksheet(0)

def write_to_spreadsheet(worksheet, df):
    worksheet.update([df.columns.values.tolist()] + df.values.tolist())

write_to_spreadsheet(worksheet, df)



#%%

#%%

#%%
