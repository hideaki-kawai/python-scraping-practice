from time import sleep

import requests
from bs4 import BeautifulSoup
import pandas as pd

base_url = 'https://employment.en-japan.com'

target_url = 'https://employment.en-japan.com/wish/search_list/?companytype=0&worktype=0&areaid=23_24_21_50&occupation=101000_102500_103000_103500_104500_105000_105500_109000&indexNoWishArea=0&sort=wish'
res = requests.get(target_url)
res.raise_for_status()

# サイト内のHTMLを取得
soup = BeautifulSoup(res.content, 'lxml')

# 企業名を取得
jobs = soup.find_all('div', class_='jobNameArea')

# 1ページあたり50件企業名が取得できているか確認
print(len(jobs))

d_list = []

for job in jobs:
    company_name = job.find('span', class_='company').text
    page_url = base_url + job.find('a').get('href')

    # 各企業の転職ページのURLから各企業のURLを取得する
    recruit_page = requests.get(page_url)
    recruit_page.raise_for_status()

    page_soup =  BeautifulSoup(recruit_page.content, 'lxml')

    company_url = None

    # 転職ページのURLに'PK'が含まれているか
    if 'PK' in page_url:
        company_summary = page_soup.find('div', class_='descArticleUnit dataCompanyInfoSummary')

        for table_row in company_summary.find_all('tr'):
            if table_row.find('th').text == '企業ホームページ':
                company_url = table_row.find('td').find('a').text
    
    elif 'fromSearch' in page_url:
        detail_page_url = page_soup.find('iframe', id='recruitFrame').get('src')

        sleep(3)

        detail_page_res = requests.get(detail_page_url)
        detail_page_res.raise_for_status()

        detail_page_soup = BeautifulSoup(detail_page_res.content, 'lxml')

        company_summary = detail_page_soup.find('table', class_='companyTable')

        for table_row in company_summary.find_all('tr'):
            if table_row.find('th').text == '企業Webサイト':
                company_url = table_row.find('td').find('a').get('href')

    d_list.append({
        'company_name': company_name,
        'company_url': company_url
    })

    print(d_list[-1])

# 取得した企業名と企業URLをCSVファイルに格納
df = pd.DataFrame(d_list)

df.to_csv('enjapan_company_list.csv', index=None, encoding='utf-8-sig')