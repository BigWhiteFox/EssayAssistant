from urllib.parse import urlencode, quote
import requests
import pandas as pd


def translate(text):
    # 查询参数字典
    params = {'query': f'{text}'}

    # 对查询参数进行百分号编码
    encoded_params = urlencode(params, quote_via=quote)

    sjr_url = f'https://consensus.app/api/paper_search/?{encoded_params}&page=0&size=10&sjr_min=1&sjr_max=2'

    return sjr_url


def extract_data(text, n):
    url = translate(text)
    data = []
    for page in range(n):
        r1 = requests.get(url)
        data1 = r1.json()['papers']
        for i in data1:
            tittle = i['title']
            llm_summary = i['display_text']
            citation_count = i['citation_count']
            tem_url = 'https://consensus.app/papers/advances-networks-gu/' + i['paper_id']
            journal = i['journal']
            doi = i['doi']
            authors = i['authors']
            data.append([tittle, llm_summary, citation_count, tem_url, journal, doi, authors])

        url = url.replace(f'page={page}', f'page={page + 1}')
    total_data = pd.DataFrame(data, columns=['Tittle', 'LLM Summary',
                                             'Citation_count', 'URL', 'Journal', 'Doi', 'Authors'])
    total_data.to_csv('consensus_data.csv', encoding='utf-8-sig')
    return total_data

