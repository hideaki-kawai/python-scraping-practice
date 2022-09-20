from time import sleep
 
import requests
from bs4 import BeautifulSoup
import pandas as pd
 
 
base_url = 'https://employment.en-japan.com'
 
url = 'https://employment.en-japan.com/wish/search_list/?companytype=0&worktype=0&areaid=23_24_21_50&occupation=101000_102500_103000_103500_104500_105000_105500_109000&indexNoWishArea=0&sort=wish&pagenum={}'
 
max_page_index = 3
d_list = []
 
for i in range(max_page_index):
    print('d_list:', len(d_list))
    access_url = url.format(i+1)
 
    sleep(3)
    r = requests.get(access_url)
    r.raise_for_status()
 
    soup = BeautifulSoup(r.content, 'lxml')
 
    jobs = soup.find_all('div', class_='jobNameArea')
    print(access_url, len(jobs))
 
 
    for job in jobs:
        company_name = job.find('span', class_='company').text
        page_url = base_url + job.find('a').get('href')
 
 
        if 'fromSearch' in page_url:
            path = page_url.replace(base_url+'/desc_eng_', '')
            e_index = path.rfind('/')
 
            company_id = path[:e_index]
 
            page_url = f'https://en-gage.net/recruit/?getFromEmploy={company_id}'
 
        sleep(3)
        page_r = requests.get(page_url)
        page_r.raise_for_status()
 
        page_soup = BeautifulSoup(page_r.content, 'lxml')
 
        company_url = None
 
        if 'PK' in page_url:
            company_info_block = [h2 for h2 in page_soup.find_all('h2', class_='text') if '会社概要' in h2.text][0]
            company_summary = company_info_block.parent.parent
 
            for table_row in company_summary.find_all('tr'):
                if table_row.find('th').text == '企業ホームページ':
                    company_url = table_row.find('td').find('a').text
        
        elif 'getFromEmploy' in page_url:
            company_summary = page_soup.find('table', class_='companyTable')
            
            for table_row in company_summary.find_all('tr'):
                if table_row.find('th').text == '企業WEBサイト':
                    company_url = table_row.find('td').find('a').get('href')
        
        else:
            raise
        
        d_list.append({
            'company_name': company_name,
            'company_url': company_url
        })
        print(d_list[-1])
 
 
# 取得した企業名と企業URLをCSVファイルに格納
df = pd.DataFrame(d_list)
df.to_csv('enjapan_company_list.csv', index=False, encoding='utf-8-sig')