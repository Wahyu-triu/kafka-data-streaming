from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pprint import pprint
import pandas as pd
from sqlalchemy import create_engine
import sqlalchemy
import time
import os
 
# set up connection to postgres database

username = 'root'
password = 'root'
server = 'localhost'
database = 'postgres'
port = '5432'

engine = create_engine(f'postgresql://{username}:{password}@{server}:{port}/{database}')

# scraper function
def scraper():

    # define empty list
    list_player_name = []
    list_position = []
    list_club = []
    list_country = []
    list_age = []
    list_market_value = []
    
    for tr in range(0,25):
        tr = tr + 1
        time.sleep(1)
        # scrap each values
        name = driver.find_element(By.XPATH, f'//*[@id="yw1"]/table/tbody/tr[{tr}]/td[2]/table/tbody/tr[1]/td[2]/a').text
        position = driver.find_element(By.XPATH, f'//*[@id="yw1"]/table/tbody/tr[{tr}]/td[2]/table/tbody/tr[2]/td').text
        age = driver.find_element(By.XPATH, f'//*[@id="yw1"]/table/tbody/tr[{tr}]/td[3]').text
        age = int(age)
        club = driver.find_element(By.XPATH, f'//*[@id="yw1"]/table/tbody/tr[{tr}]/td[5]/a').get_attribute('title')
        country = driver.find_element(By.XPATH, f'//*[@id="yw1"]/table/tbody/tr[{tr}]/td[4]/img[1]').get_attribute('title')
        market_value = driver.find_element(By.XPATH, f'//*[@id="yw1"]/table/tbody/tr[{tr}]/td[6]/a').text
        market_value = ''.join(i for i in market_value if i not in '"Rp.Mlyr')
        market_value = round(float(market_value.replace(',', '.')) * 1000000000, 0)        

        df_line = pd.DataFrame({
            'player_name' : [name],
            'position' : [position],
            'club_name' : [club],
            'country_name' : [country],
            'age' : [age],
            'market_value' : [market_value]
        })

        df_line.to_sql(f"db_football_player", engine, if_exists='append', index=False)
        print(f'Insert data ---> name : {name}, age : {age}, position : {position}, from {club} has market value around {market_value}')

        # append data
        list_player_name.append(name)
        list_position.append(position)
        list_club.append(club)
        list_country.append(country)
        list_age.append(age)
        list_market_value.append(market_value)

    temp_df = pd.DataFrame({
        'player_name' : list_player_name,
        'position' : list_position,
        'club_name' : list_club,
        'country_name' : list_country,
        'age' : list_age,
        'market_value' : list_market_value
    })

    return temp_df

# scraping data from transfermark website, Indonesian league 23/24
url = 'https://www.transfermarkt.co.id/spieler-statistik/wertvollstespieler/marktwertetop'
# driver = webdriver.Chrome()
options = webdriver.ChromeOptions()
options.add_argument('--ignore-certificate-errors')
options.add_argument('--ignore-ssl-errors')
driver = webdriver.Chrome(options=options)

driver.get(url)

# dealing with cookies
accept_cookies = True

if accept_cookies:
    print('Waiting for the cookies . . .')
    try:
        iframe = WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[id="sp_message_iframe_953428"]')))
        driver.switch_to.frame(iframe)

        # print(driver.page_source)
        print('switched to pop up frame .... ')

        button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Accept & continue")]')))
        button.click()

        print("Coockies Appecpted")

        accept_cookies = False
        driver.switch_to.default_content()
    except:
        print("No iframe found or cookies already accepted")
        driver.switch_to.default_content()
        accept_cookies = False

# crawling data
df = pd.DataFrame()

num_page = 0
max_entries = 21 # max 20
basepath = r'D:\Portofolio\DataEn\data'
filename = 'player_market_value_2024.csv'

while num_page < max_entries:
    print(f'Scraping data number {len(df) + 1} to { len(df) + 25}')
    if (len(df) == 0) and (num_page == 0):
        temp_df = scraper()
        df = pd.concat([df, temp_df])
        if not os.path.exists(basepath):
            os.makedirs(basepath)
        df.to_csv(os.path.join(basepath, filename))
        num_page = num_page + 1
        print(f'Succesfully scrap data from page {num_page}')
        print('Navigating to the next page ...')
        time.sleep(2)
    else:
        try:  
            driver.find_element(By.XPATH, '//a[@title="Ke Halaman Selanjutnya"]').click()
            print('Navigating to the next page ...')
            temp_df = scraper()
            df = pd.concat([df, temp_df])
            if not os.path.exists(basepath):
                os.makedirs(basepath)
            df.to_csv(os.path.join(basepath, filename))
            num_page = num_page + 1
            print(f'Succesfully scrap data from page {num_page}')
            time.sleep(2)

        except Exception as e:
            print('Last page reached')
            break

print(f'Successfully scrap {len(df)} data from {url}')

driver.quit()