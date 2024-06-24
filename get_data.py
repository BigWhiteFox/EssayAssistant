from urllib.parse import urlencode, quote
import requests
from bs4 import BeautifulSoup
import pandas as pd
import gradio as gr
from internVL_find import summary_paper


def translate(text):
    # 查询参数字典
    params = {'wd': f'{text}'}
    # 对查询参数进行百分号编码
    encoded_params = urlencode(params, quote_via=quote)
    url_relevance = (f'https://xueshu.baidu.com/s?{encoded_params}&pn={0}&tn=SE_baiduxueshu_c1gjeupa&'
                     f'ie=utf-8&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&sc_hit=1')
    url_reference = (f'https://xueshu.baidu.com/s?{encoded_params}&pn={0}&tn=SE_baiduxueshu_c1gjeupa&'
                     f'ie=utf-8&sort=sc_cited&sc_f_para=sc_tasktype%3D%7BfirstSimpleSearch%7D&sc_hit=1')
    return url_relevance, url_reference


def scrape_data(url, n):
    data_list = []
    for page in range(n):
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        data = soup.find_all('h3', class_='t c_font')
        href_list = []
        for temp in data:
            href_list.append(temp.a.get('href'))

        for href in href_list:
            req = requests.get(href)
            # 检查响应状态码
            if req.status_code == 404:
                print(f"404 error: {url} not found, skipping.")
                continue  # 跳过本次循环
            req_soup = BeautifulSoup(req.text, 'html.parser')
            print('\ntittle 的 href:')
            print(href)
            print('\n')
            tittle = req_soup.find('div', class_='main-info').find('a').text.strip()

            key_word = req_soup.find('div', class_='kw_wr')
            if key_word:
                key_word = key_word.find('p', class_=lambda x: x in ['kw_main', 'kw_main_s']).text.strip()
            else:
                key_word = '暂无'
            # key_word = req_soup.find('div', class_='kw_wr').find('p', class_=lambda x: x in ['kw_main', 'kw_main_s']).find('a').text.strip()

            abstract = req_soup.find('p', class_='abstract')
            if abstract:
                abstract = abstract.text.strip()
            else:
                abstract = '暂无'
            # abstract = req_soup.find('p', class_='abstract').text.strip()
            # doi = req_soup.find('div', class_='doi_wr').find('p', class_='kw_main').text.strip()

            doi = req_soup.find('div', class_='doi_wr')
            if doi:
                print('\n')
                print(href)
                print(doi)
                doi = doi.find('p', class_=lambda x: x in ['kw_main', 'kw_main_s']).text.strip()
            else:
                doi = '暂无'
            author = req_soup.find('div', class_='author_wr')
            if author:
                author = author.find('p', class_='author_text').text.strip()
            else:
                author = '暂无'
            # author = req_soup.find('div', class_='author_wr').find('p', class_='author_text kw_main_s').text.strip()

            paper_url = href
            data_list.append([tittle, key_word, abstract, doi, author, paper_url])
        print(url)
        url = url.replace(f'pn={page}', f'pn={page + 10}')
        print(url)
    total_data = pd.DataFrame(data_list, columns=['Tittle', 'Keywords', 'Abstract', 'DOI/ISBN', 'Author', 'Paper_url'])
    return total_data


# 定义一个函数来格式化输出
# 定义一个函数来格式化输出特定的列
def format_specific_columns(row, columns):
    formatted_string = ""
    for col in columns:
        formatted_string += f"{col}: {row[col]}  "
    # print("大模型输入的是：\n", formatted_string)
    # print("大模型输出的是：\n", fold_paper(formatted_string.strip()))
    return summary_paper(formatted_string.strip())


def summarize_data(data):
    fold_data = data[['Tittle', 'Keywords', 'Abstract', 'DOI/ISBN', 'Author', 'Paper_url']]
    abstract = []
    for i in range(len(fold_data)):
        abstract.append(format_specific_columns(fold_data.iloc[i], ['Tittle', 'Abstract']))
        # 应用格式化函数并输出特定的列
        # print(f"第{i}次abstract输出:\n", abstract)

    fold_data['Abstract'] = abstract
    fold_data.rename(columns={'Abstract': 'LLM Summary'}, inplace=True)
    return fold_data


def run(text, n):
    url1, url2 = translate(text)
    relevance_data = scrape_data(url1, n)
    reference_data = scrape_data(url2, n)
    relevance_data.to_csv('relevance_data.csv', encoding='utf-8-sig')
    reference_data.to_csv('reference_data.csv', encoding='utf-8-sig')
    new_relevance_data = summarize_data(relevance_data)
    new_relevance_data.to_csv('new_relevance_data.csv', encoding='utf-8-sig')
    new_reference_data = summarize_data(reference_data)
    new_reference_data.to_csv('new_reference_data.csv', encoding='utf-8-sig')
    return new_relevance_data, new_reference_data


# text = 'CNN'
# n = 2
# run(text, n)
